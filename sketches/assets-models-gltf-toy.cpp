// A toy glTF reader: one triangle, a base64 buffer, two accessors.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

static const char* s_Document = R"({
  "asset": { "version": "2.0" },
  "buffers": [ { "byteLength": 44, "uri": "data:application/octet-stream;base64,AAAAAAAAAAAAAAAAAACAPwAAAAAAAAAAAAAAAAAAgD8AAAAAAAABAAIAAAA=" } ],
  "bufferViews": [ { "buffer": 0, "byteOffset": 0, "byteLength": 36 }, { "buffer": 0, "byteOffset": 36, "byteLength": 6 } ],
  "accessors": [
    { "bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3" },
    { "bufferView": 1, "componentType": 5123, "count": 3, "type": "SCALAR" } ]
})";

// Every number that follows the key, in file order. A real parser reads the JSON tree; the toy trusts this layout.
static std::vector<size_t> NumbersAfter(const std::string& text, const std::string& key)
{
	std::vector<size_t> numbers;
	for (size_t at = text.find(key); at != std::string::npos; at = text.find(key, at + 1))
		numbers.push_back(std::strtoul(text.c_str() + at + key.size() + 1, nullptr, 10));
	return numbers;
}

static std::vector<uint8_t> DecodeBase64(const std::string& text)
{
	const std::string alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
	std::vector<uint8_t> bytes;
	uint32_t bits = 0;
	int count = 0;
	for (char letter : text)
	{
		const size_t value = alphabet.find(letter);
		if (value == std::string::npos)
			break; // The padding "=" ends the data
		bits = (bits << 6) | static_cast<uint32_t>(value);
		count += 6;
		if (count >= 8)
		{
			count -= 8;
			bytes.push_back(static_cast<uint8_t>((bits >> count) & 0xFF));
		}
	}
	return bytes;
}

int main()
{
	const std::string document = s_Document;
	const std::string marker = "base64,";
	const size_t start = document.find(marker) + marker.size();
	const std::vector<uint8_t> buffer = DecodeBase64(document.substr(start, document.find('"', start) - start));

	const std::vector<size_t> offsets = NumbersAfter(document, "\"byteOffset\":");
	const std::vector<size_t> counts = NumbersAfter(document, "\"count\":");
	std::printf("buffer: %zu bytes\n", buffer.size());

	// Accessor 0: three float triples (VEC3, componentType 5126) starting at the first view's offset.
	for (size_t vertex = 0; vertex < counts[0]; vertex++)
	{
		float position[3];
		std::memcpy(position, buffer.data() + offsets[0] + vertex * sizeof(position), sizeof(position));
		std::printf("position %zu: (%g, %g, %g)\n", vertex, position[0], position[1], position[2]);
	}

	// Accessor 1: three 16-bit unsigned integers (SCALAR, componentType 5123) from the second view.
	for (size_t corner = 0; corner < counts[1]; corner++)
	{
		uint16_t index;
		std::memcpy(&index, buffer.data() + offsets[1] + corner * sizeof(index), sizeof(index));
		std::printf("index %zu: %u\n", corner, static_cast<unsigned>(index));
	}
	return 0;
}
