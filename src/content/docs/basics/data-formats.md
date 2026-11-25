---
id: basics/data-formats
title: "JSON, Base64, hashes and UUIDs"
description: "How programs write numbers and data as text and read them back exactly, and how hashes, checksums and random identifiers name and protect data."
kind: primer
size: L
tracks: [B, E]
needs: [basics/bytes]
time: 150
learn:
  - id: numbers-text
    text: choose enough digits to write a float or a double as text that reads back as the same number
  - id: json-text
    text: find the errors in a JSON text and read the format header and the version of a project file
  - id: tokens-patterns
    text: trace how a reader cuts text into tokens and write a regular expression for a file name pattern
  - id: base64-hashes
    text: compute the Base64 text of bytes and choose a stable hash, a checksum or a cryptographic hash for a job
  - id: uuids
    text: compute the chance that two random identifiers meet and name how many digits Strata's UUID takes
status: final
---

::::test-out

1. The float `1.0f / 3.0f` is written as the text `0.333333` and read back into a float. Is the result the same float?
   How many digits always suffice for a float?

   :::answer{tests="numbers-text"}
   No. Six digits name a float near the original, not the original. Nine digits always suffice for a float, and
   17 for a double.
   :::

2. Find the two mistakes in this text: `{"Name": "Coin Run", "Levels": [1, 2, 3,], "Done": True}`.

   :::answer{tests="json-text"}
   The `,` after `3` has no value behind it, and `True` must be written `true`. A strict reader refuses the whole
   text for either mistake.
   :::

3. Which of `Hash.cpp`, `Hash.h` and `Hash.cpp.bak` does the pattern `^.*\.cpp$` match?

   :::answer{tests="tokens-patterns"}
   Only `Hash.cpp`. The `^` and `$` tie the pattern to the whole name, `.*` takes any start, and `\.cpp` needs a real
   dot and the letters `cpp` at the very end, which `Hash.cpp.bak` lacks.
   :::

4. A file arrives, and its CRC-32C matches the one its sender wrote. What did that check catch, and what can it not rule
   out?

   :::answer{tests="base64-hashes"}
   The check catches damage by accident, such as a bit flipped on the way. It cannot rule out a change made on purpose,
   because whoever changes the file can compute a new CRC-32C for it.
   :::

5. How many hexadecimal digits does Strata's universally unique identifier (UUID) take, and how many bits do they hold?

   :::answer{tests="uuids"}
   16 digits. Each digit holds 4 bits, so the UUID holds 16 × 4 = 64 bits.
   :::

::::

## Why you will need this

A game is made of files and messages that two programs must read the same way: a project file, a command sent to the
editor, a screenshot inside a reply. This page teaches the text formats Strata uses for them. It also teaches the numbers
a program computes from :term[bytes]{id=byte}, to name them or to check that nothing damaged them.

Other pages use these ideas at once. [Commands](../editor/commands.md) sends every request as a JSON value.
[What an asset is](../assets/what-is-an-asset.md) stores documents as JSON text and names assets with identifiers.
[Sockets, framing and JSON-RPC](../automation/json-rpc.md) cuts a stream of text into messages. [The security
model](../automation/security.md) builds on the hashes of this page.

The page goes from numbers written as text to JSON, then to reading text by hand, and then to hashes and identifiers. Each
idea starts with a small example worked by hand.

## A number written as text must read back exactly

A program saves a number by writing its digits into a file, and loads it later by reading the digits back. For a whole
number this is exact. For a fraction it is not, because a float keeps its value in binary, and most decimal fractions
have no exact binary form. [Numbers in a computer](../basics/numbers.md) shows that a float is one of a fixed set of
values, and that neighbouring floats lie some distance apart.

Writing a float as text picks a decimal number, and reading it picks the nearest float. If the text has too few digits,
the nearest float is a neighbour of the original, and the saved game loads a slightly different number. The next
sketch writes `1.0f / 3.0f` with 6, 8 and 9 digits and reads each text back.

```cpp sketch="basics-data-formats-roundtrip.cpp"
// Writing a float as text: how many digits does it take to read back the same float?
#include <cstdio>
#include <cstdlib>
#include <initializer_list>
#include <limits>

int main()
{
	const float value = 1.0f / 3.0f;
	for (const int digits : { 6, 8, 9 })
	{
		char text[32];
		std::snprintf(text, sizeof(text), "%.*g", digits, value);
		const float back = std::strtof(text, nullptr);
		std::printf("%d digits: %s reads back %s\n", digits, text, back == value ? "equal" : "different");
	}
	std::printf("always enough: %d digits for a float, %d for a double\n", std::numeric_limits<float>::max_digits10, std::numeric_limits<double>::max_digits10);
}
```

```text output-of="basics-data-formats-roundtrip.cpp"
6 digits: 0.333333 reads back different
8 digits: 0.33333334 reads back equal
9 digits: 0.333333343 reads back equal
always enough: 9 digits for a float, 17 for a double
```

1. **Line 9:** the float nearest to one third, a number with no end in decimal and none in binary.
2. **Lines 13–14:** `snprintf` writes the float with the chosen count of significant digits, and `strtof` reads that text back into a float.
3. **Line 17:** `max_digits10` is the :term[standard library's]{id=standard-library} name for the digits that always suffice.

Six digits fail for this value, and eight happen to work. Nine always work for a float, and 17 for a double, because
nine digits are enough to tell any two neighbouring floats apart, and 17 do the same for doubles. A writer that uses fewer
digits trades exactness for shorter files. The JSON writer inside Strata, the `nlohmann::json` library, picks a
short text that is sure to read back to the same number, as the comment at `Strata/vendor/json/include/nlohmann/detail/output/serializer.hpp`
says.

:::example[Two texts for one float]
The float nearest one third is 0.3333333432674408 in full. Written with 6 digits it is `0.333333`, which lies about
3.4 × 10⁻⁷ away from it. Floats near 0.33 lie about 3 × 10⁻⁸ apart, so a number that far off is more than ten gaps away, and the
reader picks another float. With 9 digits the text is `0.333333343`, only 3 × 10⁻¹⁰ off, so the reader picks the original.
:::

Try it: a double is saved with 15 digits and loaded again. Can it change?

:::answer
Yes. A double needs up to 17 digits to read back exactly, so a text of 15 digits can name a neighbour of the original.
:::

## JSON writes values as text with a few rules

**JavaScript Object Notation (JSON)** is a text format for data that stands for values of six kinds: objects, arrays,
strings, numbers, the words `true` and `false`, and `null`. Programs in every language read and write it, and a person can
read it without a tool. Strata saves projects, scenes and other documents in it, and its automation commands take and return it.

A **JSON object** is a pair of curly braces around members, each a name in double quotes, a colon and a value, with a `,`
between two members. A name should appear once in an object.

A **JSON array** is square brackets around values separated by `,`, in an order that matters. Both can hold any value,
including other objects and arrays, so a document is a tree.

```json
{"Name": "Coin Run", "Levels": [1, 2, 3], "Done": false, "Best": null}
```

The line above is one object with four members. `"Name"` holds a string, `"Levels"` an array of three numbers, `"Done"`
the word `false`, and `"Best"` the word `null`, which stands for "no value". Spaces and line breaks between the pieces do not
matter, and a string may hold any text if the quote, the backslash and the control characters are escaped with a
backslash, as in `"say \"hi\""`. [Bytes](../basics/bytes.md) explains that the text is UTF-8.

Two JSON values are equal when they have the same shape and the same contents. The order of the members of an object does
not matter, so `{"a": 1, "b": 2}` equals `{"b": 2, "a": 1}`. The order of an array does matter: `[1, 2]` differs from
`[2, 1]`. Spaces and line breaks do not count. A program that compares two documents compares these values, never the
raw text.

Strata's own project file is a JSON document. The next quote is the whole file of the Tetris sample. Notice the two
objects at the top level, and how the handles look.

```json src="Samples/Tetris/Tetris.stproj#L1-L22"
{
	"Project": {
		"AssetDirectory": "Assets",
		"Game": {
			"Company": "",
			"Copyright": "",
			"Icon": "F8DFB22B97ABAE5B",
			"Title": "Tetris",
			"Version": "1.0.0"
		},
		"Name": "Tetris",
		"Scripts": {
			"ModuleName": "TetrisScripts",
			"SourceDirectory": "Scripts"
		},
		"StartScene": "BD75622ED18E84E4"
	},
	"Strata": {
		"Format": "Project",
		"Version": 3
	}
}
```

1. **Lines 2–17:** the `"Project"` object holds the settings of the game. Its `"Game"` member is an object inside it, and `"Version": "1.0.0"` on line 9 is a string, the game's own version.
2. **Line 16:** the start scene is a handle, written as a string of 16 :term[hexadecimal]{id=hexadecimal} digits.
3. **Lines 18–21:** the `"Strata"` object holds the format header of the next section.

The members of each object appear sorted by name. A project with settings of its own, such as input actions, has a third
object at the top level, `"Settings"`, between the other two. A handle is a number of 64 bits, and the file writes it as a
string of its digits. Some readers keep every JSON number in a double, as the language JavaScript does. A double holds a whole
number exactly only up to 2⁵³, so a string keeps all 64 bits whichever program reads the file.

## A format header lets a reader refuse a file it cannot read

Strata changes the shape of its files from release to release, and an old engine can meet a file written by a newer one.
A **format header** is a small part of a document that names its kind and its version, so the reader checks them before it
trusts anything else. In the Tetris file, lines 18 to 21 say that this is a `"Project"` file of version 3.

`Project::Load` in `Strata/src/Strata/Project/Project.cpp` reads the :term[header]{id=header} first. A file without the `"Strata"` object,
or with another `"Format"`, fails with "not a Strata project file". A version of 0, or above the version the engine
writes, fails with the message `unsupported project version` and names the highest version the engine reads. Files of
version 1 and 2 are older still: the editor migrates what they kept elsewhere when it opens one, and saves it as the
current version.

The reader is strict about the header and generous about the rest. `Load` copies the members of the `"Project"` object it
does not know, and `Save` writes them back. A newer release can add members without a new version, and an older
one that saves the file then keeps them. The version number protects a file from a reader that would read it wrongly, and the unknown members protect it
from a reader that would forget something.

:::example[Reading a header]
A file holds `{"Strata": {"Format": "Project", "Version": 4}, "Project": {}}`, and the engine writes version 3. The format
matches, so the reader continues. The version 4 is above 3, so the reader stops with `unsupported project version 4` and
leaves the file alone. A file with `"Version": 0` stops the same way.
:::

Try it: a file says `"Format": "Scene"` and `"Version": 3`. What does `Project::Load` do?

:::answer
`Project::Load` refuses the file as "not a Strata project file", because the format is not `"Project"`. The version is never looked at.
:::

## A reader cuts text into tokens before it understands it

A program that reads JSON starts with a long row of characters and must find the pieces. The first step cuts the text
into **tokens**, the smallest meaningful pieces: one special character, a whole string, a number or a word such as
`true`. The second step, a **parser**, checks that the tokens follow the rules and builds the values from them. This
section writes the first step by hand.

Take the text `{"Version": 3}`. The reader looks at one character at a time. The character `{` makes a token by itself, and
so do `:` and the closing `}`. A `"` starts a string that ends at the next `"`, so `"Version"` is one token.

The reader skips the space, and `3` runs until the next special character. The row of tokens is `{`, `"Version"`, `:`,
`3`, `}`.

The next sketch does this for a longer text. Its loop keeps `start`, the place where the next token begins, and finds the
`end` of the token. Its text is a raw string, `R"(...)"`, in which a quote needs no backslash. Notice the two cases
that decide where a token ends.

```cpp sketch="basics-data-formats-tokens.cpp"
// Cuts a JSON text into tokens, one character at a time; a string that never ends is an error.
#include <iostream>
#include <string>

int main()
{
	const std::string text = R"({"Name": "Coin Run", "Version": 3, "Done": true})";
	const std::string punctuation = "{}[]:, ";
	for (size_t start = 0; start < text.size();)
	{
		size_t end = text.find_first_of(punctuation, start + 1);
		if (text[start] == '"')
			end = text.find('"', start + 1) + 1;
		else if (punctuation.find(text[start]) != std::string::npos)
			end = start + 1;
		if (end == 0 || end == std::string::npos)
		{
			std::cout << "error: the text ends inside a token\n";
			return 1;
		}
		if (text[start] != ' ')
			std::cout << text.substr(start, end - start) << '\n';
		start = end;
	}
}
```

```text output-of="basics-data-formats-tokens.cpp"
{
"Name"
:
"Coin Run"
,
"Version"
:
3
,
"Done"
:
true
}
```

1. **Line 11:** a token ends at the next special character or space, which suits numbers and words.
2. **Lines 12–13:** a string ends at the next quote, whatever it holds, so the space in `"Coin Run"` stays inside.
3. **Lines 14–15:** a special character such as `{` or `,` is a token of one character.
4. **Lines 16–20:** a string that never ends, or a word that runs to the end of the text, is a mistake the reader reports, never a token it invents.

The sketch is only the start of a reader. It does not know the escape `\"` inside a string, and it checks no grammar: it
would cut `{]` into tokens without complaint. A parser adds the grammar.

A value is a string, a number, a word, an array or
an object. An object is `{`, then members separated by `,`, then `}`, and each member holds a string, a colon and a
value. Because a value can hold values, the parser calls itself for each nested array or object.

:::example[Tokens of a text with a mistake]
The text `[1, 2,]` gives the tokens `[`, `1`, `,`, `2`, `,`, `]`. Each token is valid alone. The parser expects a value after
every `,`, and finds `]`, so it reports the mistake at the last `,`. The tokens alone could not see it, because the mistake
lies in their order.
:::

Try it: cut `{"a": "b c"}` into tokens by hand.

:::answer
`{`, `"a"`, `:`, `"b c"`, `}`. The space inside the quotes belongs to the string, and the space after the colon is skipped.
:::

## Strict readers refuse what forgiving readers accept

A strict reader accepts only text that follows the rules of the format. A forgiving reader repairs what it can: it ignores a `,`
before a closing bracket, accepts comments, and takes `True` or single quotes. That looks friendly, and it costs more
than it gives. Two forgiving readers forgive different things, so a file that one accepts, another refuses.

A forgiving reader
also hides damage. A file cut short by a full disk can still look complete after the reader guesses the missing closing
brace.

Strata reads JSON strictly. `JsonUtils::Parse` in `Strata/src/Strata/Core/JsonUtils.cpp` calls the `nlohmann::json` parser
with comments off and without exceptions, and returns nothing for text that breaks the rules. The cost falls on people
who edit files by hand: a `,` left behind after deleting the last member makes every reader of the file fail until the `,` is gone. For the file's reader that is the right trade, because one clear refusal beats a game that loads a guessed
version of a save.

JSON has plain rules, and Strata keeps them. It has no comments and no `,` before a closing bracket. Strings use double quotes,
and the words `true`, `false` and `null` use lower case. A number has no leading zeros, and the whole text holds one value,
so `{"a": 1}{"b": 2}` is invalid.

## Patterns find text, and JSON needs more than a pattern

Pages of the track for engine developers quote patterns, such as the ones in build files and in tests, and this section
teaches the small part they use. A **regular expression**, also called a pattern, is a short text that describes a set of
texts. A program asks whether a text matches the pattern, or finds the part that does.

Most characters stand for themselves: the pattern `cpp` matches the letters `cpp`. The rest have a meaning.

| Piece | Meaning | Example |
| --- | --- | --- |
| `.` | any one character | `a.c` matches `abc` and `a-c` |
| `*` | the piece before it, zero or more times | `ab*` matches `a`, `ab` and `abbb` |
| `+` | the piece before it, one or more times | `ab+` matches `ab` but not `a` |
| `?` | the piece before it, zero or one time | `colou?r` matches `color` and `colour` |
| `[a-z]` | one character of a class: here a lower-case letter | `[a-z]+` matches `coin` |
| `^` and `$` | the start and the end of the text | `^cpp$` matches only `cpp` |
| `( )` | a group, which the repeat marks apply to as a whole | `(ab)+` matches `abab` |
| `\` | the next character stands for itself | `\.` matches a dot and nothing else |

The backslash matters because the dot is a command. The pattern `a.c` also matches `abc`, but `a\.c` matches only `a.c`.
Without `^` and `$` a pattern matches any text that contains a match, so `cpp` finds a match inside `Hash.cpp.bak`.

A **glob** is the simpler pattern that file names use, as in `*.cpp`: `*` stands for any run of characters, and the dot
stands for itself. The next sketch turns a glob into a regular expression: it writes `^` first, escapes each dot, puts a
dot before each star, and ends with `$`. See which names the pattern accepts.

```cpp sketch="basics-data-formats-glob.cpp"
// A glob turned into a regular expression: the dot of a glob is a plain dot, so the pattern escapes it.
#include <iostream>
#include <regex>
#include <string>

std::string GlobToPattern(const std::string& glob)
{
	std::string pattern = "^";
	for (const char character : glob)
	{
		if (character == '.')
			pattern += '\\';
		if (character == '*')
			pattern += '.';
		pattern += character;
	}
	return pattern + "$";
}
int main()
{
	const std::regex pattern(GlobToPattern("*.cpp"));
	const std::string names[] = { "Hash.cpp", "Hash.h", "cpp", "a.cpp.bak" };
	for (const std::string& name : names)
		std::cout << name << ": " << std::regex_match(name, pattern) << '\n';
}
```

```text output-of="basics-data-formats-glob.cpp"
Hash.cpp: 1
Hash.h: 0
cpp: 0
a.cpp.bak: 0
```

1. **Lines 11–12:** a dot becomes a backslash and a dot.
2. **Lines 13–14:** a star becomes a dot and a star, so `*.cpp` turns into `^.*\.cpp$`.
3. **Line 24:** `regex_match` asks that the whole name matches, so `a.cpp.bak` fails.

The sketch handles only the star and the dot. A real glob also has `?` and classes, and a name with characters such as `+`
or `(` needs a backslash too.

JSON cannot be checked with a pattern. A pattern has no memory of how deep it is. It cannot require that every `[` finds
its own `]` when arrays nest to any depth, as in `[[[1]]]`. The tokens of the previous section are the part a pattern can
find. The nesting needs a parser, which keeps track of the depth by calling itself.

Try it: write a pattern for names such as `Level1.json` to `Level9.json`.

:::answer
`^Level[1-9]\.json$`. The class `[1-9]` takes one digit, the backslash makes the dot a real dot, and `^` and `$` allow
nothing before or after.
:::

## Base64 writes bytes with 64 safe characters

A JSON string holds text. Bytes, such as the contents of a picture, are not text: many byte values are no valid UTF-8, and
others are control characters or quotes. **Base64** is a way to write any bytes with 64 safe characters: the letters `A`
to `Z` and `a` to `z`, the digits `0` to `9`, `+` and `/`. Any program can then carry the bytes inside a text.

The rule works on three bytes at a time. Three bytes are 24 bits. Cut the 24 bits into four groups of 6 bits. Each
group is a number from 0 to 63, and it picks one character of the alphabet in order. Number 0 is `A`, 25 is `Z`, 26 is `a`, 51 is
`z`, 52 is `0`, 61 is `9`, 62 is `+` and 63 is `/`.

:::example[The bytes of "Man"]
The letters M, a and n are the bytes 77, 97 and 110, which are `01001101`, `01100001` and `01101110` in binary. Joined, they
are `010011010110000101101110`. The four groups of six bits are `010011`, `010110`, `000101` and `101110`, which are 19, 22,
5 and 46. The alphabet gives `T`, `W`, `F` and `u`, so `Man` becomes `TWFu`.
:::

The next sketch does the same with shifts and masks, the tools of [Numbers in a computer](../basics/numbers.md). Notice
how a shift and the mask `0x3F`, which keeps 6 bits, pull out each group.

```cpp sketch="basics-data-formats-base64.cpp"
// Base64 of three bytes: their 24 bits are cut into four groups of 6 bits, and each group picks a character.
#include <cstdint>
#include <iostream>
#include <string>

int main()
{
	const char alphabet[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
	const uint8_t bytes[3] = { 'M', 'a', 'n' };
	const uint32_t bits = (bytes[0] << 16) | (bytes[1] << 8) | bytes[2];
	std::string text;
	for (int shift = 18; shift >= 0; shift -= 6)
	{
		const uint32_t group = (bits >> shift) & 0x3F;
		std::cout << group << ' ';
		text += alphabet[group];
	}
	std::cout << "-> " << text << '\n';
}
```

```text output-of="basics-data-formats-base64.cpp"
19 22 5 46 -> TWFu
```

1. **Line 10:** the three bytes join into one number of 24 bits, the first byte highest.
2. **Lines 12–14:** shifting right by 18, 12, 6 and 0 brings each group to the bottom, and `& 0x3F` keeps only its 6 bits.
3. **Line 16:** the group is the index into the alphabet.

When the bytes do not fill a multiple of three, the writer pads. Two bytes give three characters and one `=`; one byte
gives two characters and `==`. The text of `Ma` is `TWE=`. Every group of four characters
carries up to three bytes, so n bytes take (n + 2) ÷ 3 groups, rounded down, times 4 characters. That is a third more than
the bytes themselves, the price of the safe alphabet.

Strata uses Base64 where bytes must travel inside JSON. The editor command `viewport.capture` can return a screenshot as
a PNG file encoded in Base64, in the member `Data` of the result's `Image` object. `Base64::Decode` in
`Strata/src/Strata/Core/Base64.h` is strict: it rejects characters outside the alphabet, including spaces, bad padding
and non-zero bits inside the padding. Every byte sequence then has exactly one accepted text.

Try it: how many characters does Base64 write for 4 bytes?

:::answer
4 bytes make one full group of three and one byte more, so two groups of four characters: 8 characters, the last two being
`==`.
:::

## A stable hash gives the same number everywhere

A **hash** is a number computed from data by a fixed rule, and a hash map uses it to choose a bucket, as [Data
structures I](../basics/data-structures.md) shows. The same data always gives the same number. That page's toy hash adds
the letter codes of a text: `ant` gives 97 + 110 + 116 = 323. The same page warns about `std::hash`, the hash of the
standard library. It is good only inside one running program, because another library or version may compute other
numbers for the same text, so storing one in a file is a mistake.

A **stable hash** is a hash whose rule is written down and never changes, so every program on every machine gives the same
number for the same bytes.

Strata needs one wherever a number goes to disk, and its answer is **FNV-1a**. This hash has a
64-bit result and two steps for each byte: mix the byte into the hash with exclusive or (`XOR`), then multiply by a large prime.
`XOR` compares two numbers bit by bit and sets each bit of the result where the two bits differ. It
puts the byte in, and the multiplication spreads its effect over many bits. Multiplying wraps around in 64 bits, as
unsigned numbers do: a product too large for 64 bits keeps only its lowest 64 bits, as [Numbers in a
computer](../basics/numbers.md) explains.

:::question
What does `constexpr` mean? Read it as "may be computed while the program is built"; [Modern C++ as Strata uses it](../basics/cpp-modern.md) teaches it.
:::

The quote is the whole function in `Strata/src/Strata/Core/Hash.h`. Notice the two constants and the two statements
inside the loop.

```cpp src="Strata/src/Strata/Core/Hash.h#L16-L28"
static constexpr uint64_t FNVOffsetBasis = 14695981039346656037ull;
static constexpr uint64_t FNVPrime = 1099511628211ull;

static constexpr uint64_t FNV1a(std::string_view text, uint64_t seed = FNVOffsetBasis)
{
	uint64_t hash = seed;
	for (char character : text)
	{
		hash ^= static_cast<uint8_t>(character);
		hash *= FNVPrime;
	}
	return hash;
}
```

1. **Lines 16–17:** the offset basis is where every hash starts, and the prime is the number every step multiplies by; both are fixed by the definition of the hash.
2. **Lines 19–21:** the `seed` parameter defaults to the offset basis, and `hash` starts from it, so a caller can continue a hash across several pieces.
3. **Lines 24–25:** `XOR` the byte in, then multiply: the whole algorithm.

The comment above the class says what it is for: stable hashing, "suitable for identifiers persisted to disk", not
cryptographic. The next sketch follows the one-byte text `a` through the two steps.

```cpp sketch="basics-data-formats-fnv.cpp"
// FNV-1a of the one-byte text "a": the XOR puts the byte in, and the multiplication spreads it over the 64 bits.
#include <cstdint>
#include <iostream>

int main()
{
	const uint64_t offsetBasis = 14695981039346656037ull;
	const uint64_t prime = 1099511628211ull;
	uint64_t hash = offsetBasis;
	std::cout << std::hex << "start:       " << hash << '\n';
	hash ^= static_cast<uint8_t>('a');
	std::cout << "after XOR:   " << hash << '\n';
	hash *= prime;
	std::cout << "after times: " << hash << '\n';
}
```

```text output-of="basics-data-formats-fnv.cpp"
start:       cbf29ce484222325
after XOR:   cbf29ce484222344
after times: af63dc4c8601ec8c
```

1. **Line 11:** the byte `a` is 0x61, and `XOR` changes only the lowest byte of the start value, from `25` to `44`.
2. **Line 13:** the multiplication wraps around in 64 bits and changes every part of the number.

The result `af63dc4c8601ec8c` is the published FNV-1a value of `a`, so any correct program prints the same. Strata uses it
for numbers that must be the same on every machine. `DeriveSubAssetHandle` in `Strata/src/Strata/Asset/AssetImporter.cpp`
makes the handle of a part of an imported file from the part's name and its parent's handle, so
that importing the file again gives the same handle. `Hash::Combine`, in the same header, mixes one hash into another to
build such a number from several pieces.

A 64-bit hash cannot be unique, because there are more texts than numbers. Two different texts can share a hash, a
collision, which a hash map expects and tolerates. FNV-1a is fast and spreads well, and it is no protection against someone
who searches for texts with equal hashes, which is the work of a later section.

Try it: why does the toy hash above, the sum of the letter codes, make a poor stable hash?

:::answer
The sum gives `ant` and `tan` the same number, 323, because it ignores the order of the letters. FNV-1a mixes each byte in
turn, so the order changes the result.
:::

## A checksum catches damaged data

Disks fail, cables flip bits and downloads stop halfway. A **checksum** is a small number computed from data and stored or
sent beside it. The reader computes the number again from the data it received, and a different number means the data was
damaged. The simplest checksum adds the bytes and keeps the remainder of the sum after division by 256. It
catches one changed byte, but misses `ab` swapped for `ba`, because 97 + 98 and 98 + 97 are both 195.

**CRC-32C** is the checksum Strata uses. It treats the bytes as one very long
number and keeps the remainder of a division, calculated in a special arithmetic of bits, so the 32-bit result depends on
every byte and on its place. It catches every change of one burst of up to 32 bits, and almost every other change. The
next sketch is the slow bit-by-bit form of the algorithm, with the constant `0x82F63B78` that `Strata/src/Strata/Core/Hash.cpp`
also uses.

```cpp sketch="basics-data-formats-crc.cpp"
// CRC-32C: the checksum of "ab" differs from that of "ba", and "123456789" gives the standard check value.
#include <cstdint>
#include <iostream>
#include <string>

uint32_t CRC32C(const std::string& text)
{
	uint32_t crc = 0xFFFFFFFFu;
	for (const char character : text)
	{
		crc ^= static_cast<uint8_t>(character);
		for (int bit = 0; bit < 8; bit++)
			crc = (crc & 1u) ? (crc >> 1) ^ 0x82F63B78u : crc >> 1;
	}
	return ~crc;
}

int main()
{
	const std::string texts[] = { "ab", "ba", "123456789" };
	for (const std::string& text : texts)
		std::cout << text << ": CRC-32C " << std::hex << CRC32C(text) << '\n';
}
```

```text output-of="basics-data-formats-crc.cpp"
ab: CRC-32C e2a22936
ba: CRC-32C c515725b
123456789: CRC-32C e3069283
```

1. **Line 8:** the checksum starts with all 32 bits set, and the last line of the function inverts it.
2. **Lines 11–13:** the byte goes into the lowest bits, and then each of its 8 bits either shifts, or shifts and then applies `XOR` with the constant.
3. **Line 20:** the text `123456789` is the standard test: every correct CRC-32C gives `e3069283`.

The sums of `ab` and `ba` are equal, yet the two CRC-32C values differ. `Hash::CRC32C` in
`Strata/src/Strata/Core/Hash.h` computes the same value, and where the processor has instructions for it, as many modern processors do, it uses them. Every implementation gives the same results. The asset pack
reader checks the checksum of a pack's header, of its tables and of each block of data, so a damaged pack is detected.

A checksum protects against accidents and not against people. The CRC-32C of a changed file is cheap to compute, so whoever
changes the data on purpose changes the checksum too, and the reader sees a match.

## A cryptographic hash cannot be forged or inverted

A **cryptographic hash** is a hash built so that nobody can invert it or forge data for it. Given a hash, no one can find
data that produces it, short of trying every possibility. No one can find two different data with the same hash either.
Change one bit of the data, and about half of the bits of the hash change.

**SHA-256** is the cryptographic hash Strata
uses, and its result, the digest, has 256 bits: 32 bytes, which a program writes as 64 hexadecimal digits.

The digest of the three letters `abc` is `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`. The digest of
`abd`, one letter different, is `a52d159f262b2c6ddb724a61840befc36eb30c88877a4030b65cbe86298449c9`, which shares nothing
visible with it. Even the empty text has a digest, which begins `e3b0c442`. These are the standard values that every
correct SHA-256 gives.

Strata has `Sha256` and `Crypto::ToHex` in `Strata/src/Strata/Core/Crypto.h`. `ToHex` writes lower-case hexadecimal. The
editor uses a digest to tell whether a file changed. It keeps the digest of the script module it loaded, and when the file
on disk later has another digest, it reports that the module changed. A checksum would catch an
accident here, and a digest also catches a change that someone made carefully.

Two more names appear in the same header, and [The security model](../automation/security.md) teaches them. **HMAC** is a
hash of a message mixed with a secret key, so that only a holder of the key can compute it. `Crypto::ConstantTimeEquals`
compares two values without stopping at the first difference, so the time it takes does not reveal how much of a secret
matched. The editor's server uses both to check who is connecting.

Try it: you download an installer, and its maker's site lists a SHA-256 digest. What do you compute, and what does a match
prove?

:::answer
Compute the digest of the downloaded file and compare it with the listed one. A match proves that the file is the one the
maker published, if you trust the site's page, because nobody can build another file with the same digest.
:::

## A UUID names a thing without asking anyone

A game has thousands of entities and assets that need names, and several people, or several programs, create them at the
same time. A counter would need one place that hands out numbers. A **UUID**, a universally unique identifier, needs none:
each creator draws a random number so large that another creator is very unlikely to draw the same one.

The standard UUID has 128 bits, written as 32 hexadecimal digits. They come in groups of 8, 4, 4, 4 and 12 digits with a `-` between groups, such as
`123e4567-e89b-12d3-a456-426614174000`. Strata's has 64 bits, written as 16 hexadecimal digits.

The `UUID` class in
`Strata/src/Strata/Core/UUID.h` draws a random number from a generator that each thread seeds from the system's
random device. It never draws zero, which means "no identifier". `ToString` writes the number in upper-case digits, as in `BD75622ED18E84E4`.
`UUID::FromString` reads upper and lower case, with or without the prefix `0x`, up to 16 digits.

"Very unlikely" needs a number. Take n identifiers drawn from 2⁶⁴ possible values. The chance that some two are equal is
about n² ÷ 2⁶⁵ while the chance stays small. This is the birthday problem: the pairs among n values number about n² ÷ 2, and
each pair meets with probability 2⁻⁶⁴. The sketch prints the chance for four counts.

```cpp sketch="basics-data-formats-birthday.cpp"
// The chance that two of n random 64-bit identifiers are equal: about n * n / 2^65 while it stays small.
#include <cmath>
#include <cstdio>
#include <initializer_list>

int main()
{
	const double space = 18446744073709551616.0; // 2^64 identifiers
	for (const double count : { 1.0e3, 1.0e6, 1.0e9, 5.06e9 })
	{
		const double chance = -std::expm1(-count * count / (2.0 * space));
		std::printf("%.2e identifiers: chance %.3g, one in %.3g\n", count, chance, 1.0 / chance);
	}
}
```

```text output-of="basics-data-formats-birthday.cpp"
1.00e+03 identifiers: chance 2.71e-14, one in 3.69e+13
1.00e+06 identifiers: chance 2.71e-08, one in 3.69e+07
1.00e+09 identifiers: chance 0.0267, one in 37.4
5.06e+09 identifiers: chance 0.5, one in 2
```

1. **Line 8:** the number of possible identifiers, 2⁶⁴ as a double.
2. **Line 11:** `expm1` computes the chance 1 − e⁻ˣ without losing digits when x is tiny.

For a million handles the chance is 2.71 × 10⁻⁸, one in 37 million. For a thousand it is one in 3.7 × 10¹³. It reaches one
half only near five billion handles, and a project holds thousands to millions.

So two identifiers can meet, and it is
rare enough that Strata's :term[constructor]{id=constructor} only draws a number and does not check it. The choice costs a small risk, where 128 bits would cost none. It buys an identifier that is one 64-bit :term[integer]{id=integer}: it fits one register, compares in one instruction and
hashes with `std::hash` directly.

A UUID is no secret. The generator is built for spreading numbers, not for hiding
them. [Entities and components](../world/ecs.md) and [Handles, .meta files and sub-assets](../assets/handles-meta.md) use it
as the identity of entities and assets.

Try it: four digits is 16 bits. How likely is it that two of 300 four-digit random codes meet?

:::answer
About 300² ÷ 2¹⁷ = 90,000 ÷ 131,072, which is 0.69. The formula is only right while the chance is small, but it shows the
answer: more likely than not.
:::

## Common mistakes

- **A float written with too few digits.** Symptom: a loaded save differs from the saved game in the last digits, and the
  same file gives different results after another save. Fix: write at least 9 digits for a float and 17 for a double, or
  use a writer that picks the shortest exact text.
- **A `std::hash` stored in a file.** Symptom: a file written by one build finds nothing when another build reads it. Fix:
  store a stable hash such as FNV-1a, or store the key itself.
- **A stray `,` or a comment in JSON.** Symptom: a strict reader refuses the whole file, often with a short message
  and no line. Fix: remove the `,`, delete the comment, and validate the text with a tool before saving.
- **A checksum used as protection.** Symptom: a file changed on purpose still passes the check. Fix: use a cryptographic
  hash, kept or sent where the attacker cannot change it, or a keyed hash.
- **A UUID taken for a secret.** Symptom: someone guesses or reads an identifier and uses it as a key. Fix: use random
  identifiers for names, and a separate secret for access.

## Summary

- Write a float with 9 digits and a double with 17 to read back the same number; fewer digits can name a neighbour.
- JSON has objects, arrays, strings, numbers, `true`, `false` and `null`; a format header gives the kind and version of a
  document, and a strict reader refuses text that breaks the rules.
- A reader cuts text into tokens and then parses them; a regular expression describes simple texts such as a glob, and
  JSON needs a parser because it nests.
- Base64 writes three bytes as four characters; FNV-1a is a stable hash, CRC-32C catches accidents and SHA-256 cannot be forged.
- Strata's UUID has 64 bits in 16 hexadecimal digits, and the chance that two meet is about n² ÷ 2⁶⁵.

## Check yourself

1. A game saves a `double` as text with 10 digits and loads it later. Which is true?

   - A. The number is always exact, because a double has 15 digits.
   - B. The number can differ in its last bits; 17 digits would make it exact.
   - C. The number is always exact if the text has a decimal point.
   - D. The number can only be off by a whole unit.

   :::answer{tests="numbers-text"}
   B. A double needs up to 17 digits to read back exactly, so 10 digits can name a neighbour. A has the wrong reason, C
   mistakes the point for precision, and D confuses the error with a whole number.
   :::

2. Which of these texts is valid JSON, and what does a strict reader do with the others?

   - A. `{"a": 1, "b": 2,}`
   - B. `{'a': 1}`
   - C. `{"a": [1, 2], "b": null}`
   - D. `{"a": 1} // note`

   :::answer{tests="json-text"}
   C. A has a `,` before the closing brace, B uses single quotes and D has a comment. A strict reader refuses each of them as a whole
   and reports an error, as Strata's reader does.
   :::

3. Write a pattern that matches `data.json` and `save3.json` but not `data.jsonl`, and say why `^` and `$` matter.

   :::answer{tests="tokens-patterns"}
   `^[a-z]+[0-9]*\.json$`. The `$` ends the match right after `json`, so `data.jsonl` fails. Without `^` and `$` the
   pattern would match any text that merely contains such a name.
   :::

4. How many characters does Base64 write for 100 bytes?

   :::answer{tests="base64-hashes"}
   The answer is 136. The 100 bytes make 33 full groups and one byte more, so 34 groups of 4 characters, which is 136. The formula
   (100 + 2) ÷ 3 rounded down, times 4, gives the same.
   :::

5. True or false: a Strata UUID can never repeat. Give the chance for a million handles.

   :::answer{tests="uuids"}
   False. With 64 bits the chance that two of a million handles meet is about 10¹² ÷ 2⁶⁵, which is 1 in 37 million: small,
   never zero.
   :::

## Practice

1. **Basic.** Which of these are valid JSON? Give the mistake in each other one: `[1, 2, 3]`, `{"a": 1 "b": 2}`,
   `{"a": undefined}`, `{"a": {"b": [true, null]}}`.

   :::answer[Worked solution]{tests="json-text"}
   The first and the last are valid. The second has no `,` between the members, and the third uses `undefined`, which
   JSON does not have; only `true`, `false` and `null` are words.
   :::

2. **Basic.** Write the bytes of the text `Hi` in Base64 by hand. The letters H and i are the bytes 72 and 105.

   :::answer[Worked solution]{tests="base64-hashes"}
   72 and 105 are `01001000` and `01101001`. The 16 bits cut into groups of six are `010010`, `000110` and `1001`, and the
   last group is padded with two zeros to `100100`. They are 18, 6 and 36, the characters `S`, `G` and `k`, and the
   padding `=` completes the group: `SGk=`.
   :::

3. **Medium.** Choose a stable hash, a checksum or a cryptographic hash for each job. First, the handle of a mesh that an
   import makes again on every machine. Second, whether a download arrived whole. Third, whether the file on the server is
   the file its maker published.

   :::answer[Worked solution]{tests="base64-hashes"}
   First: a stable hash such as FNV-1a, because only the same number everywhere matters. Second: a checksum such as
   CRC-32C, because the danger is an accident. Third: a cryptographic hash such as SHA-256, because someone might change
   the file on purpose.
   :::

4. **Medium.** Trace the tokens sketch by hand on `{"a": "b`. Where does it stop, and what does it print? Then compute the FNV-1a
   hashes of `ant` and `tan` with the program below and compare them.

   :::answer[Worked solution]{tests="tokens-patterns" solution="sketches/basics-data-formats-anagrams.cpp"}
   The sketch prints `{`, `"a"` and `:`. The string `"b` never ends, so `find` returns "not found", the end becomes 0,
   and the reader prints its error instead of a token. The hashes differ, because FNV-1a mixes each byte in turn.

   ```cpp sketch="basics-data-formats-anagrams.cpp"
   // Practice 4: the toy hash of the data structures page gives "ant" and "tan" one number; FNV-1a does not.
   #include <cstdint>
   #include <initializer_list>
   #include <iostream>
   #include <string>

   uint64_t FNV1a(const std::string& text)
   {
   	uint64_t hash = 14695981039346656037ull;
   	for (const char character : text)
   	{
   		hash ^= static_cast<uint8_t>(character);
   		hash *= 1099511628211ull;
   	}
   	return hash;
   }

   int main()
   {
   	for (const std::string name : { "ant", "tan" })
   		std::cout << name << ": " << std::hex << FNV1a(name) << '\n';
   }
   ```

   ```text output-of="basics-data-formats-anagrams.cpp"
   ant: e6f7a71905200db6
   tan: 56d7b2194448b0d8
   ```

   1. **Lines 7–16:** the same loop as the quoted `Hash::FNV1a`, with its constants written in place.
   2. **Lines 20–21:** `ant` and `tan` have the same letters and the toy sum gives both 323, yet their FNV-1a values differ.
   :::

5. **Hard.** How many random 64-bit identifiers make a 1 in 1,000 chance that two are equal? Use n² ÷ 2⁶⁵, and take 2⁶⁵ as
   3.69 × 10¹⁹.

   :::answer[Worked solution]{tests="uuids"}
   Solve n² ÷ 2⁶⁵ = 0.001, so n² = 0.001 × 3.69 × 10¹⁹ = 3.69 × 10¹⁶. The square root is n = 1.9 × 10⁸, about 190 million
   identifiers. A project is far below that, which is why 64 bits are enough for it.
   :::

6. **Hard.** Optional, starting from the end of Coin Run: your project from [Coin Run](../make/project-coin-run.md), or
   Checkpoint 4 at the end of [Ship the finished game](../make/project-coin-run.md#ship-the-finished-game), whose zip holds
   a folder with `CoinRun.stproj`. Open that project file in your :term[code editor]{id=code-editor}, and change nothing.
   Find the format header, the version, and the handle of the start scene.

   :::answer[Worked solution]{tests="json-text"}
   The file is built like the Tetris file above, with a third object at the top level: `"Settings"`, between `"Project"`
   and `"Strata"`. It holds the input actions and collision layers that Coin Run made, under the names `Input.Actions` and
   `Scene.CollisionLayers`, so the file is about 170 lines long, with the header at its end. The `"Strata"` object holds
   `"Format": "Project"` and the version 3. The `"Project"` object, at the top, holds `"StartScene"`, a string of 16
   hexadecimal digits that differs from project to project. Close the file without saving.
   :::

## Where the book uses it

- [Commands](../editor/commands.md) sends a command's input and result as JSON values, and its ids as 16-digit strings.
- [Sockets, framing and JSON-RPC](../automation/json-rpc.md) cuts a stream into messages that are JSON text, a reader like
  the one of this page.
- [What an asset is](../assets/what-is-an-asset.md) stores the engine's documents as JSON and names assets by handle.
- [Reflection](../world/reflection.md) writes each property of a component as a JSON value.
- [The security model](../automation/security.md) builds the keyed hash and the constant-time comparison on SHA-256.

## Further reading

- [json.org, "Introducing JSON"](https://www.json.org/json-en.html): the whole grammar of JSON on one page; beginner.
- [RFC 8259, The JSON Data Interchange Format](https://www.rfc-editor.org/rfc/rfc8259): the standard text, short and exact; advanced.
- [RFC 4648, The Base16, Base32 and Base64 Data Encodings](https://www.rfc-editor.org/rfc/rfc4648): the alphabet and the padding rules; intermediate.
- [RegexOne](https://regexone.com/): an interactive course on patterns; beginner.
- [FIPS 180-4, Secure Hash Standard](https://csrc.nist.gov/pubs/fips/180-4/upd1/final): the definition of SHA-256; advanced.
