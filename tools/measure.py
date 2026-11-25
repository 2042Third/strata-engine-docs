#!/usr/bin/env python3
"""Runs a command and measures it: wall time, the peak memory of the command and every process it starts (the build's
Node process, Chromium for diagrams, Pagefind), sampled four times a second, and how busy the machine was with other
programs meanwhile.

    python tools/measure.py [--label <name>] [--json <file>] [--env NAME=VALUE ...] -- <command> [arguments...]

Memory is the resident set (Windows: the working set) summed over the process tree at each sample; the peak of that
sum, and the peak of the largest single process, are reported. A sample interval of 250 ms can miss a peak shorter than
that, so the numbers are a lower bound of the true peak. Run full-scale measurements under the engine's performance
lock (the engine's Tools/PerfLock.py), so that they never overlap another measurement. The lock lives in the user's
temporary folder, so the lock must run with the normal TEMP; --env gives the measured command the book's own
(TEMP=.tools/tmp and the toolchain's PATH) without changing the lock's.

The lock keeps other measurements away, not the engine's builds and tests, which run without it. So the machine's
CPU time over the run (all processors) minus the CPU time of the measured processes and of this tool is recorded as
"other_cpu_seconds", and "other_load" is that divided by the wall time: how many processors other programs kept busy
on average. tools/budgets.py judges a time only when that load was low. Processes of the command that end between two
samples count as other programs for their last quarter second, so the load is an upper bound.

Only the standard library is used (ctypes on Windows, /proc on Linux). Exit code: the command's.
"""

import argparse
import ctypes
import json
import os
import subprocess
import sys
import threading
import time

c_Interval = 0.25

if os.name == 'nt':
    from ctypes import wintypes

    class ProcessEntry(ctypes.Structure):
        _fields_ = [
            ('dwSize', wintypes.DWORD), ('cntUsage', wintypes.DWORD), ('th32ProcessID', wintypes.DWORD),
            ('th32DefaultHeapID', ctypes.c_size_t), ('th32ModuleID', wintypes.DWORD), ('cntThreads', wintypes.DWORD),
            ('th32ParentProcessID', wintypes.DWORD), ('pcPriClassBase', ctypes.c_long), ('dwFlags', wintypes.DWORD),
            ('szExeFile', ctypes.c_char * 260),
        ]

    class MemoryCounters(ctypes.Structure):
        _fields_ = [
            ('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD), ('PeakWorkingSetSize', ctypes.c_size_t),
            ('WorkingSetSize', ctypes.c_size_t), ('QuotaPeakPagedPoolUsage', ctypes.c_size_t), ('QuotaPagedPoolUsage', ctypes.c_size_t),
            ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t), ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
            ('PagefileUsage', ctypes.c_size_t), ('PeakPagefileUsage', ctypes.c_size_t),
        ]

    c_Kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    c_Psapi = ctypes.WinDLL('psapi', use_last_error=True)
    c_Kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    c_Kernel.OpenProcess.restype = wintypes.HANDLE
    c_InvalidHandle = wintypes.HANDLE(-1).value

    def process_table():
        """{pid: (parent pid, name)} of every process."""
        snapshot = c_Kernel.CreateToolhelp32Snapshot(0x2, 0)
        if snapshot == c_InvalidHandle:
            return {}
        table = {}
        entry = ProcessEntry()
        entry.dwSize = ctypes.sizeof(ProcessEntry)
        try:
            more = c_Kernel.Process32First(snapshot, ctypes.byref(entry))
            while more:
                table[entry.th32ProcessID] = (entry.th32ParentProcessID, entry.szExeFile.decode('mbcs', 'replace'))
                more = c_Kernel.Process32Next(snapshot, ctypes.byref(entry))
        finally:
            c_Kernel.CloseHandle(snapshot)
        return table

    class FileTime(ctypes.Structure):
        _fields_ = [('low', wintypes.DWORD), ('high', wintypes.DWORD)]

    def seconds_of(value):
        return ((value.high << 32) | value.low) / 1e7

    def system_busy_seconds():
        """CPU time all processors spent outside the idle process since the machine started."""
        idle, kernel, user = FileTime(), FileTime(), FileTime()
        if not c_Kernel.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)):
            return None
        return seconds_of(kernel) - seconds_of(idle) + seconds_of(user)  # kernel time includes the idle time

    def cpu_seconds(pid):
        handle = c_Kernel.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return None
        try:
            creation, exited, kernel, user = FileTime(), FileTime(), FileTime(), FileTime()
            if c_Kernel.GetProcessTimes(handle, ctypes.byref(creation), ctypes.byref(exited), ctypes.byref(kernel), ctypes.byref(user)):
                return seconds_of(kernel) + seconds_of(user)
            return None
        finally:
            c_Kernel.CloseHandle(handle)

    def resident_bytes(pid):
        handle = c_Kernel.OpenProcess(0x1000 | 0x0010, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ
        if not handle:
            return 0
        try:
            counters = MemoryCounters()
            counters.cb = ctypes.sizeof(MemoryCounters)
            if c_Psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                return counters.WorkingSetSize
            return 0
        finally:
            c_Kernel.CloseHandle(handle)
else:
    def process_table():
        table = {}
        for name in os.listdir('/proc'):
            if not name.isdigit():
                continue
            try:
                with open('/proc/%s/stat' % name, encoding='utf-8', errors='replace') as file:
                    stat = file.read()
                command = stat[stat.index('(') + 1:stat.rindex(')')]
                parent = int(stat[stat.rindex(')') + 2:].split()[1])
                table[int(name)] = (parent, command)
            except (OSError, ValueError):
                continue
        return table

    c_Ticks = os.sysconf('SC_CLK_TCK')

    def system_busy_seconds():
        """CPU time all processors spent busy (not idle, not waiting for I/O) since the machine started."""
        try:
            with open('/proc/stat', encoding='utf-8') as file:
                fields = [int(value) for value in file.readline().split()[1:9]]
        except (OSError, ValueError):
            return None
        return (sum(fields) - fields[3] - fields[4]) / c_Ticks

    def cpu_seconds(pid):
        try:
            with open('/proc/%d/stat' % pid, encoding='utf-8', errors='replace') as file:
                stat = file.read()
            fields = stat[stat.rindex(')') + 2:].split()
            return (int(fields[11]) + int(fields[12])) / c_Ticks
        except (OSError, ValueError, IndexError):
            return None

    def resident_bytes(pid):
        try:
            with open('/proc/%d/status' % pid, encoding='utf-8') as file:
                for line in file:
                    if line.startswith('VmRSS:'):
                        return int(line.split()[1]) * 1024
        except OSError:
            pass
        return 0


def tree_of(root, table):
    """The pids of root and all its descendants."""
    children = {}
    for pid, (parent, _) in table.items():
        children.setdefault(parent, []).append(pid)
    found = []
    pending = [root]
    while pending:
        pid = pending.pop()
        if pid in found:
            continue
        found.append(pid)
        pending.extend(children.get(pid, []))
    return found


class Sampler(threading.Thread):
    def __init__(self, pid):
        super().__init__(daemon=True)
        self.pid = pid
        self.stop = threading.Event()
        self.peak_total = 0
        self.peak_single = 0
        self.peak_by_name = {}
        self.samples = 0
        self.cpu_by_pid = {}

    def sample(self):
        table = process_table()
        total = 0
        by_name = {}
        for pid in tree_of(self.pid, table) + [os.getpid()]:
            cpu = cpu_seconds(pid)
            if cpu is not None:
                self.cpu_by_pid[pid] = max(self.cpu_by_pid.get(pid, 0.0), cpu)
            if pid == os.getpid():
                continue
            size = resident_bytes(pid)
            total += size
            name = table.get(pid, (0, '?'))[1]
            by_name[name] = by_name.get(name, 0) + size
            self.peak_single = max(self.peak_single, size)
        for name, size in by_name.items():
            self.peak_by_name[name] = max(self.peak_by_name.get(name, 0), size)
        self.peak_total = max(self.peak_total, total)
        self.samples += 1

    def run(self):
        while not self.stop.is_set():
            self.sample()
            self.stop.wait(c_Interval)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Measures wall time and peak memory of a command and its child processes.')
    parser.add_argument('--label', default='command')
    parser.add_argument('--json', help='append the result as one JSON line to this file')
    parser.add_argument('--env', action='append', default=[], metavar='NAME=VALUE', help='set a variable for the command (repeatable)')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    options = parser.parse_args(argv)
    command = options.command[1:] if options.command[:1] == ['--'] else options.command
    if not command:
        parser.error('give the command after --')
    env = dict(os.environ)
    for item in options.env:
        name, separator, value = item.partition('=')
        if not separator or not name:
            parser.error('--env takes NAME=VALUE, not %r' % item)
        env[name] = value
    started = time.monotonic()
    busy_before = system_busy_seconds()
    try:
        process = subprocess.Popen(command, env=env)
    except OSError as error:
        print('measure: cannot run %s: %s' % (command[0], error), file=sys.stderr)
        return 2
    sampler = Sampler(process.pid)
    sampler.start()
    code = process.wait()
    seconds = time.monotonic() - started
    sampler.stop.set()
    sampler.join()
    sampler.sample()  # this tool's own CPU time to the end
    busy_after = system_busy_seconds()
    measured_cpu = sum(sampler.cpu_by_pid.values())
    other_cpu = None if busy_before is None or busy_after is None else max(0.0, busy_after - busy_before - measured_cpu)
    result = {
        'label': options.label,
        'command': command,
        'exit_code': code,
        'seconds': round(seconds, 2),
        'peak_tree_bytes': sampler.peak_total,
        'peak_process_bytes': sampler.peak_single,
        'peak_by_program': dict(sorted(sampler.peak_by_name.items(), key=lambda item: -item[1])[:8]),
        'samples': sampler.samples,
        'cpu_count': os.cpu_count(),
        'cpu_seconds': round(measured_cpu, 2),
        'other_cpu_seconds': None if other_cpu is None else round(other_cpu, 2),
        'other_load': None if other_cpu is None or seconds <= 0 else round(other_cpu / seconds, 3),
    }
    load = '' if result['other_load'] is None else ', other programs kept %.2f processors busy' % result['other_load']
    print('measure: %s: %.1f s, peak %.0f MB (largest process %.0f MB)%s, exit %d' % (options.label, seconds, sampler.peak_total / 2**20, sampler.peak_single / 2**20, load, code), file=sys.stderr)
    if options.json:
        with open(options.json, 'a', encoding='utf-8') as file:
            file.write(json.dumps(result) + '\n')
    return code


if __name__ == '__main__':
    sys.exit(main())
