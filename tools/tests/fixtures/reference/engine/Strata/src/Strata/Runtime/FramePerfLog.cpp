// A pretend engine file in the shape of the perf log's columns (tools/tests/test_reference.py).
namespace Strata
{

	Scope<FramePerfLog> FramePerfLog::Create()
	{
		Scope<FramePerfLog> log = CreateScope<FramePerfLog>();
		log->m_Columns = { "Frame", "WorkMs" };
		for (const char* column : { "LoadingAssets", "QueuedLoads", "InFlightLoads" })
		{
			log->m_Columns.push_back(column);
		}
		return log;
	}

}
