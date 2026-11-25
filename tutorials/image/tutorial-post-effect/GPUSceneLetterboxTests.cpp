#include "Renderer/SceneRendererTestUtils.h"
#include "Strata/Renderer/PostProcessMath.h"
#include "Strata/Renderer/RendererComponents.h"

using namespace Strata;
using namespace Strata::Tests;

// The letterbox (PostProcess/Letterbox.comp): black bars that crop the image to a wider aspect, off by default.
namespace
{

	constexpr uint32_t c_Width = 1024;
	constexpr uint32_t c_Height = 576;
	constexpr int c_Code = 128;

	// A wall of one display code (unlit, the neutral post-processing shows it unchanged) filling the view.
	struct GrayWall
	{
		Scene SceneData;
		PostProcessComponent* PostProcess = nullptr;

		explicit GrayWall(SceneTestAssets& assets)
		{
			PostProcess = &AddNeutralPostProcess(SceneData);
			AddMesh(SceneData, BuiltinAssets::QuadMesh, assets.AddMaterial(Emitting(PostProcessMath::SRGBToLinear(static_cast<float>(c_Code) / 255.0f))),
				glm::vec3(0.0f), "Wall")
				.GetComponent<TransformComponent>().Scale = glm::vec3(40.0f, 40.0f, 1.0f);
		}
	};

	ReadbackImage RenderWall(SceneRenderer& renderer, GrayWall& wall)
	{
		const SceneCamera camera = LookAt(glm::vec3(0.0f, 0.0f, 2.0f), glm::vec3(0.0f), static_cast<float>(c_Width) / static_cast<float>(c_Height));
		REQUIRE(renderer.Render(wall.SceneData, camera));
		ReadbackImage image;
		REQUIRE(Renderer::ReadTexture(renderer.GetOutputTexture(), image));
		return image;
	}

}

TEST_SUITE("GPU.SceneRenderer.Letterbox")
{
	TEST_CASE("The letterbox blacks the bars and leaves the picture between them as it was")
	{
		GPUContext gpu;
		REQUIRE(gpu.IsValid());
		SceneTestAssets assets;
		GrayWall wall(assets);
		SceneRenderer renderer(ExactSpecification());
		renderer.SetViewportSize(c_Width, c_Height);
		const ReadbackImage plain = RenderWall(renderer, wall);
		CHECK(Red(plain, c_Width / 2, c_Height / 2) == c_Code);

		// 1024 / 2 = 512 rows of picture, so 32 rows of bar above and below.
		wall.PostProcess->Letterbox = true;
		wall.PostProcess->LetterboxAspect = 2.0f;
		const ReadbackImage barred = RenderWall(renderer, wall);
		for (uint32_t x = 0; x < c_Width; x++)
		{
			for (uint32_t y = 0; y < c_Height; y++)
			{
				const bool inBar = y < 32 || y >= c_Height - 32;
				if (inBar)
					CHECK(GetPixelRGBA8(barred, x, y) == glm::u8vec4(0, 0, 0, 255));
				else
					CHECK(GetPixelRGBA8(barred, x, y) == GetPixelRGBA8(plain, x, y));
			}
		}
		CHECK(gpu.GetNewErrorCount() == 0);
	}

	TEST_CASE("A view as wide as the aspect, or at the neutral value, renders bit for bit as without the effect")
	{
		GPUContext gpu;
		REQUIRE(gpu.IsValid());
		SceneTestAssets assets;
		GrayWall wall(assets);
		SceneRenderer renderer(ExactSpecification());
		renderer.SetViewportSize(c_Width, c_Height);
		const ReadbackImage plain = RenderWall(renderer, wall);

		// The neutral value is off: AddNeutralPostProcess leaves the letterbox off, and the bars wait for it.
		CHECK_FALSE(wall.PostProcess->Letterbox);
		wall.PostProcess->LetterboxAspect = 2.0f;
		CHECK(MaxDifference(RenderWall(renderer, wall), plain) == 0);

		// On, with an aspect the view already has (a narrower one): no bars, no pass.
		wall.PostProcess->Letterbox = true;
		wall.PostProcess->LetterboxAspect = 1.0f;
		CHECK(MaxDifference(RenderWall(renderer, wall), plain) == 0);
		CHECK(gpu.GetNewErrorCount() == 0);
	}
}
