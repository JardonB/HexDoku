import json
import os
from pathlib import Path

SAVE_PATH = Path("savegame.json")

def save_state(board, fixed, difficulty: int):
    state = {
        "size": board.size,
        "grid": board.grid,
        "fixed": fixed,
        "solution": board.solution_grid,
        "difficulty": difficulty,
    }
    with SAVE_PATH.open("w") as f:
        json.dump(state, f)

def load_state():
    if not SAVE_PATH.exists():
        return None
    with SAVE_PATH.open() as f:
        return json.load(f)