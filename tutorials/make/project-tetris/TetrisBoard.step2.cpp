// The first board script: it starts a game and logs the pieces. Nothing is drawn yet.

#include "StrataScript/StrataScript.h"

#include "TetrisGame.h"

using namespace Strata;

class TetrisBoard : public Script
{
public:
	int32_t Seed = 60;
	int32_t StartLevel = 1;
	int32_t LinesPerLevel = 10;

	void OnCreate() override
	{
		m_Game.Reset(static_cast<uint64_t>(Seed), StartLevel, LinesPerLevel);
		Log::Info("Tetris: new game with seed ", Seed);
		LogPiece();
	}
private:
	void LogPiece()
	{
		Log::Info("Tetris: piece ", m_Game.GetPiecesDealt(), " is ", Tetris::GetPieceName(m_Game.GetPiece().Type), ", next ",
			Tetris::GetPieceName(m_Game.GetNextType()));
	}
private:
	Tetris::Game m_Game;
};

ST_SCRIPT_CLASS(TetrisBoard)
{
	ST_SCRIPT_FIELD(Seed);
	ST_SCRIPT_FIELD(StartLevel);
	ST_SCRIPT_FIELD(LinesPerLevel);
}
