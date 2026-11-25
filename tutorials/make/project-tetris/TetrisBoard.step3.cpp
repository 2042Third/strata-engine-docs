// Plays Tetris on the entity it is attached to. The well's bottom-left cell sits at the entity's origin, one world unit per
// cell; the script creates the cube entities it draws with (under a child named "Cells") and shows score, level and lines
// in the UI text elements named by its fields (on the HUD canvas), and game over and pause messages on a panel it shows
// while there is one.
//
// Controls: Left/Right or A/D move (held keys repeat), Down or S soft drop, Space hard drop, Up or X rotate clockwise,
// Z rotate counterclockwise, P pause, R or Enter restart, Escape quit.

#include "StrataScript/StrataScript.h"

#include "TetrisGame.h"

#include <algorithm>
#include <cmath>
#include <string>
#include <vector>

using namespace Strata;

class TetrisBoard : public Script
{
public:
	// Rules
	int32_t Seed = 60;              // Piece sequence of the first game; each restart uses the next seed
	int32_t StartLevel = 1;
	int32_t LinesPerLevel = 10;     // Cleared lines per level

	// Looks
	AssetHandle CellMesh; // Builtin/Cube when unset
	AssetHandle MaterialI;
	AssetHandle MaterialO;
	AssetHandle MaterialT;
	AssetHandle MaterialS;
	AssetHandle MaterialZ;
	AssetHandle MaterialJ;
	AssetHandle MaterialL;
	AssetHandle GhostMaterial; // Marks where the piece would land; no ghost when unset
	float CellScale = 0.92f;   // Gaps between the cubes
	glm::vec3 PreviewOffset = { 12.0f, 15.0f, 0.0f }; // Where the next piece is shown, relative to the board

	void OnCreate() override
	{
		for (AssetHandle asset : { MaterialI, MaterialO, MaterialT, MaterialS, MaterialZ, MaterialJ, MaterialL, GhostMaterial })
		{
			if (asset)
				Assets::RequestLoad(asset);
		}
		if (!CellMesh)
			CellMesh = Assets::Find("Builtin/Cube");

		CreateCells();
		NewGame();
	}

	void OnUpdate(float) override
	{
		Refresh();
	}
private:
	static constexpr int32_t c_Ghost = Tetris::c_PieceTypeCount; // Display type of ghost cells
	static constexpr int32_t c_Unknown = -2;                      // Display type before the first refresh

	void NewGame()
	{
		const uint64_t seed = static_cast<uint64_t>(Seed);
		m_Game.Reset(seed, StartLevel, LinesPerLevel);
		Log::Info("Tetris: new game with seed ", seed);
		LogPiece();
	}

	void LogPiece()
	{
		Log::Info("Tetris: piece ", m_Game.GetPiecesDealt(), " is ", Tetris::GetPieceName(m_Game.GetPiece().Type), ", next ",
			Tetris::GetPieceName(m_Game.GetNextType()));
	}

	void CreateCells()
	{
		Entity container = Scene::CreateEntity("Cells", GetEntity());
		m_Cells.clear();
		for (int32_t y = 0; y < Tetris::c_Height; y++)
		{
			for (int32_t x = 0; x < Tetris::c_Width; x++)
				m_Cells.push_back(CreateCell(container, glm::vec3(static_cast<float>(x), static_cast<float>(y), 0.0f)));
		}
		m_Preview.clear();
		for (int32_t index = 0; index < 4; index++)
			m_Preview.push_back(CreateCell(container, PreviewOffset));
		ResetShownTypes();
	}

	Entity CreateCell(Entity parent, const glm::vec3& position)
	{
		Entity cell = Scene::CreateEntity("Cell", parent);
		cell.AddComponent("MeshRenderer");
		cell.SetProperty("MeshRenderer", "Mesh", CellMesh);
		TransformComponent transform = cell.GetTransform();
		transform.SetTranslation(position);
		transform.SetScale(glm::vec3(CellScale));
		cell.SetActive(false);
		return cell;
	}

	void ResetShownTypes()
	{
		m_ShownCells.assign(m_Cells.size(), c_Unknown);
		m_ShownPreview.assign(m_Preview.size(), c_Unknown);
		m_ShownPreviewType = c_Unknown;
	}

	// Brings the cell entities and the HUD up to date, touching only what changed.
	void Refresh()
	{
		std::vector<int32_t> types(m_Cells.size(), Tetris::c_Empty);
		for (int32_t y = 0; y < Tetris::c_Height; y++)
		{
			for (int32_t x = 0; x < Tetris::c_Width; x++)
				types[static_cast<size_t>(y * Tetris::c_Width + x)] = m_Game.GetCell(x, y);
		}
		auto place = [&](const Tetris::PieceCells& cells, int32_t type)
		{
			for (const Tetris::Cell& cell : cells)
			{
				if (cell.Y < Tetris::c_Height && types[static_cast<size_t>(cell.Y * Tetris::c_Width + cell.X)] == Tetris::c_Empty)
					types[static_cast<size_t>(cell.Y * Tetris::c_Width + cell.X)] = type;
			}
		};
		if (!m_Game.IsGameOver())
		{
			if (GhostMaterial)
				place(m_Game.GetGhostCells(), c_Ghost);
			// The piece covers its own ghost: overwrite instead of filling empty cells only.
			for (const Tetris::Cell& cell : m_Game.GetPieceCells())
			{
				if (cell.Y < Tetris::c_Height)
					types[static_cast<size_t>(cell.Y * Tetris::c_Width + cell.X)] = static_cast<int32_t>(m_Game.GetPiece().Type);
			}
		}
		for (size_t index = 0; index < m_Cells.size() && index < types.size(); index++)
			ShowCell(m_Cells[index], m_ShownCells[index], types[index]);

		const int32_t nextType = static_cast<int32_t>(m_Game.GetNextType());
		if (nextType != m_ShownPreviewType && m_Preview.size() == 4)
		{
			const Tetris::PieceCells shape = Tetris::GetShape(m_Game.GetNextType(), 0);
			for (size_t index = 0; index < 4; index++)
			{
				const glm::vec3 offset(static_cast<float>(shape[index].X), static_cast<float>(shape[index].Y), 0.0f);
				m_Preview[index].GetTransform().SetTranslation(PreviewOffset + offset);
				ShowCell(m_Preview[index], m_ShownPreview[index], nextType);
			}
			m_ShownPreviewType = nextType;
		}
	}

	void ShowCell(Entity cell, int32_t& shown, int32_t type)
	{
		if (shown == type)
			return;
		if (type == Tetris::c_Empty)
		{
			cell.SetActive(false);
		}
		else
		{
			cell.SetProperty("MeshRenderer", "Material", GetMaterial(type));
			cell.SetActive(true);
		}
		shown = type;
	}

	AssetHandle GetMaterial(int32_t type) const
	{
		switch (type)
		{
			case 0: return MaterialI;
			case 1: return MaterialO;
			case 2: return MaterialT;
			case 3: return MaterialS;
			case 4: return MaterialZ;
			case 5: return MaterialJ;
			case 6: return MaterialL;
			default: return GhostMaterial;
		}
	}

private:
	Tetris::Game m_Game;
	std::vector<Entity> m_Cells;   // Row by row from the bottom
	std::vector<Entity> m_Preview; // The next piece's four cells
	std::vector<int32_t> m_ShownCells;
	std::vector<int32_t> m_ShownPreview;
	int32_t m_ShownPreviewType = c_Unknown;
};

ST_SCRIPT_CLASS(TetrisBoard)
{
	ST_SCRIPT_FIELD(Seed);
	ST_SCRIPT_FIELD(StartLevel);
	ST_SCRIPT_FIELD(LinesPerLevel);
	ST_SCRIPT_FIELD(CellMesh);
	ST_SCRIPT_FIELD(MaterialI);
	ST_SCRIPT_FIELD(MaterialO);
	ST_SCRIPT_FIELD(MaterialT);
	ST_SCRIPT_FIELD(MaterialS);
	ST_SCRIPT_FIELD(MaterialZ);
	ST_SCRIPT_FIELD(MaterialJ);
	ST_SCRIPT_FIELD(MaterialL);
	ST_SCRIPT_FIELD(GhostMaterial);
	ST_SCRIPT_FIELD(CellScale);
	ST_SCRIPT_FIELD(PreviewOffset);
}
