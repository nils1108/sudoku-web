import random
from copy import deepcopy
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

GRID_SIZE = 9
BOX_SIZE = 3
BASE_DIR = Path(__file__).resolve().parent

DIFFICULTIES = {
    "Leicht": 35,
    "Mittel": 45,
    "Schwer": 55,
}

app = FastAPI(title="Sudoku Studio")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def normalize_difficulty(difficulty_label: str) -> str:
    normalized = (difficulty_label or "Leicht").strip().capitalize()
    if normalized not in DIFFICULTIES:
        return "Leicht"
    return normalized


def is_valid(grid, row, col, num):
    if any(grid[row][x] == num for x in range(GRID_SIZE)):
        return False
    if any(grid[x][col] == num for x in range(GRID_SIZE)):
        return False

    start_row = (row // BOX_SIZE) * BOX_SIZE
    start_col = (col // BOX_SIZE) * BOX_SIZE
    for r in range(start_row, start_row + BOX_SIZE):
        for c in range(start_col, start_col + BOX_SIZE):
            if grid[r][c] == num:
                return False
    return True


def find_empty(grid):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == 0:
                return r, c
    return None


def fill_grid(grid):
    empty_cell = find_empty(grid)
    if not empty_cell:
        return True

    row, col = empty_cell
    numbers = list(range(1, 10))
    random.shuffle(numbers)

    for num in numbers:
        if is_valid(grid, row, col, num):
            grid[row][col] = num
            if fill_grid(grid):
                return True
            grid[row][col] = 0

    return False


def count_solutions(grid, limit=2):
    empty_cell = find_empty(grid)
    if not empty_cell:
        return 1

    row, col = empty_cell
    count = 0
    for num in range(1, 10):
        if is_valid(grid, row, col, num):
            grid[row][col] = num
            count += count_solutions(grid, limit)
            grid[row][col] = 0
            if count >= limit:
                return count

    return count


def create_full_solution():
    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    fill_grid(grid)
    return grid


def remove_numbers_with_uniqueness(solution, cells_to_remove):
    puzzle = deepcopy(solution)
    all_positions = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
    random.shuffle(all_positions)

    removed = 0
    for row, col in all_positions:
        if removed >= cells_to_remove:
            break

        backup = puzzle[row][col]
        puzzle[row][col] = 0

        puzzle_copy = deepcopy(puzzle)
        if count_solutions(puzzle_copy, limit=2) == 1:
            removed += 1
        else:
            puzzle[row][col] = backup

    return puzzle


def generate_sudoku(difficulty_label: str):
    difficulty = normalize_difficulty(difficulty_label)
    solution = create_full_solution()
    puzzle = remove_numbers_with_uniqueness(solution, DIFFICULTIES[difficulty])
    fixed_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if puzzle[r][c] != 0]
    return {
        "difficulty": difficulty,
        "puzzle": puzzle,
        "solution": solution,
        "fixed_cells": fixed_cells,
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "difficulty_options": list(DIFFICULTIES.keys()),
            "default_difficulty": "Leicht",
        },
    )


@app.get("/api/new-game")
def api_new_game(difficulty: str = Query(default="Leicht")):
    return generate_sudoku(difficulty)


@app.get("/health")
def health():
    return {"ok": True}
