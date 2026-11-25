#include "Include/Common.slang"

// The letterbox: black bars over the first and the last BarRows rows of the post source, written into the next source. Every
// other texel is copied as it is, alpha included (the depth of field's and the motion blur's mark of what they blurred).

Texture2D<float4> u_Source : register(t0);
[vk::image_format("rgba16f")] RWTexture2D<float4> o_Output : register(u0);

struct LetterboxParameters
{
	uint BarRows; // Rows of each bar
	uint Padding0;
	uint Padding1;
	uint Padding2;
};
[[vk::push_constant]] ConstantBuffer<LetterboxParameters> u_Parameters;

[numthreads(8, 8, 1)]
void main(uint3 globalID : SV_DispatchThreadID)
{
	uint2 size;
	u_Source.GetDimensions(size.x, size.y);
	if (any(globalID.xy >= size))
		return;
	float4 color = u_Source.Load(int3(globalID.xy, 0));
	bool inBar = globalID.y < u_Parameters.BarRows || globalID.y >= size.y - u_Parameters.BarRows;
	o_Output[globalID.xy] = float4(inBar ? float3(0.0) : SanitizeHDR(color.rgb), color.a);
}
