#include "Include/Common.slang"

// A fullscreen gradient: the vertex shader hands over the pixel's place in the image, uv, from 0 to 1.
float4 main([[vk::location(0)]] float2 uv : TEXCOORD0) : SV_Target0
{
	float3 display = float3(uv.x, uv.y, 0.25);
	return float4(SRGBToLinear(display), 1.0);
}
