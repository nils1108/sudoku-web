import random
from copy import deepcopy

import streamlit as st

GRID_SIZE = 9
BOX_SIZE = 3

DIFFICULTIES = {
    "Leicht": 35,
    "Mittel": 45,
    "Schwer": 55,
}


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


def generate_sudoku(difficulty_label):
    if difficulty_label not in DIFFICULTIES:
        raise ValueError("Ungueltige Schwierigkeit")

    solution = create_full_solution()
    puzzle = remove_numbers_with_uniqueness(solution, DIFFICULTIES[difficulty_label])
    return puzzle, solution


def init_state():
    defaults = {
        "difficulty": "Leicht",
        "puzzle": None,
        "solution": None,
        "board": None,
        "fixed_cells": set(),
        "selected_cell": None,
        "show_solution": False,
        "game_locked": False,
        "hint_used": False,
        "status": "",
        "hint_text": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_new_game(difficulty):
    puzzle, solution = generate_sudoku(difficulty)
    st.session_state.difficulty = difficulty
    st.session_state.puzzle = puzzle
    st.session_state.solution = solution
    st.session_state.board = deepcopy(puzzle)
    st.session_state.fixed_cells = {
        (r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if puzzle[r][c] != 0
    }
    st.session_state.selected_cell = None
    st.session_state.show_solution = False
    st.session_state.game_locked = False
    st.session_state.hint_used = False
    st.session_state.status = f"Neues Spiel gestartet: {difficulty}"
    st.session_state.hint_text = ""


def set_selected_cell(row, col):
    if st.session_state.game_locked:
        st.session_state.status = "Spiel ist beendet. Starte ein neues Spiel."
        return
    st.session_state.selected_cell = (row, col)
    if (row, col) in st.session_state.fixed_cells:
        st.session_state.status = f"Feld ({row + 1}, {col + 1}) ist vorgegeben."
    else:
        st.session_state.status = f"Feld ({row + 1}, {col + 1}) ausgewaehlt."


def place_number(value):
    selected = st.session_state.selected_cell
    if selected is None or st.session_state.game_locked:
        return

    row, col = selected
    if (row, col) in st.session_state.fixed_cells:
        return

    st.session_state.board[row][col] = value
    st.session_state.status = f"Zahl {value} gesetzt in Feld ({row + 1}, {col + 1})."
    check_if_completed()


def clear_selected_cell():
    selected = st.session_state.selected_cell
    if selected is None or st.session_state.game_locked:
        return

    row, col = selected
    if (row, col) in st.session_state.fixed_cells:
        return

    st.session_state.board[row][col] = 0
    st.session_state.status = f"Feld ({row + 1}, {col + 1}) geleert."


def reveal_solution():
    if st.session_state.game_locked:
        st.session_state.status = "Loesung wurde bereits gezeigt."
        return

    st.session_state.show_solution = True
    st.session_state.game_locked = True
    st.session_state.status = "Loesung angezeigt. Spiel ist beendet."


def use_hint_once():
    if st.session_state.game_locked:
        st.session_state.status = "Kein Tipp mehr moeglich. Spiel ist beendet."
        return
    if st.session_state.hint_used:
        st.session_state.status = "Tipp wurde bereits verwendet."
        return

    board = st.session_state.board
    solution = st.session_state.solution

    wrong_cells = []
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if (row, col) in st.session_state.fixed_cells:
                continue
            value = board[row][col]
            if value != 0 and value != solution[row][col]:
                wrong_cells.append((row, col, value))

    if wrong_cells:
        row, col, value = random.choice(wrong_cells)
        st.session_state.selected_cell = (row, col)
        st.session_state.hint_text = (
            f"Tipp: In Feld ({row + 1}, {col + 1}) ist die {value} aktuell falsch."
        )
        st.session_state.hint_used = True
        st.session_state.status = "Tipp genutzt: Falsche Zahl gefunden."
        return

    for row in range(GRID_SIZE):
        empty_cols = [col for col in range(GRID_SIZE) if board[row][col] == 0]
        if len(empty_cols) == 1:
            col = empty_cols[0]
            value = solution[row][col]
            st.session_state.selected_cell = (row, col)
            st.session_state.hint_text = (
                f"Tipp: Reihe {row + 1} ist leicht. In Spalte {col + 1} gehoert die {value}."
            )
            st.session_state.hint_used = True
            st.session_state.status = "Tipp genutzt: Einfache Reihe gefunden."
            return

    st.session_state.hint_text = "Kein passender Tipp verfuegbar."
    st.session_state.status = "Tipp geprueft: aktuell kein leichter Hinweis."


def check_if_completed():
    board = st.session_state.board
    if any(0 in row for row in board):
        return

    if board == st.session_state.solution:
        st.session_state.game_locked = True
        st.session_state.status = "Perfekt geloest!"
        st.session_state.hint_text = "Stark! Du hast das Sudoku korrekt geloest."
        st.balloons()
    else:
        st.session_state.status = "Noch nicht korrekt."


def render_board():
    board = st.session_state.solution if st.session_state.show_solution else st.session_state.board
    selected = st.session_state.selected_cell

    st.markdown("### 🎯 Spielfeld")
    st.caption("Tippe ein Feld an und setze unten die Zahl.")

    # CSS für schöne 3x3 Box-Grenzen
    st.markdown("""
    <style>
    .sudoku-grid { 
        display: inline-block; 
        background: #fffaf2;
        border: 3px solid #3e4c59;
        border-collapse: collapse;
    }
    .sudoku-cell {
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #9aa5b1;
        font-weight: bold;
        cursor: pointer;
        background: #fffaf2;
        font-size: 18px;
        color: #1f2933;
    }
    .sudoku-cell.given {
        color: #153e75;
        font-weight: bold;
        background: #f0f4f8;
    }
    .sudoku-cell.selected {
        background: #d8f3ee;
        border: 2px solid #007f73;
    }
    .sudoku-row-3, .sudoku-row-6 {
        border-bottom: 3px solid #3e4c59;
    }
    .sudoku-col-3, .sudoku-col-6 {
        border-right: 3px solid #3e4c59;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container(border=False):
        for row in range(GRID_SIZE):
            cols = st.columns(9, gap="small")
            for col in range(GRID_SIZE):
                value = board[row][col]
                label = " " if value == 0 else str(value)

                is_fixed = (row, col) in st.session_state.fixed_cells
                is_selected = selected == (row, col)

                disabled = st.session_state.game_locked or st.session_state.show_solution
                
                button_key = f"cell-{row}-{col}-{value}"
                if cols[col].button(
                    label,
                    key=button_key,
                    use_container_width=True,
                    disabled=disabled,
                ):
                    set_selected_cell(row, col)


def render_controls():
    selected = st.session_state.selected_cell
    editable_selected = (
        selected is not None and selected not in st.session_state.fixed_cells and not st.session_state.game_locked
    )

    st.markdown("### ⌨️ Eingabe")
    
    if selected is None:
        st.info("Wähle zuerst ein Feld aus.")
    else:
        row, col = selected
        if selected in st.session_state.fixed_cells:
            st.info(f"Feld ({row + 1}, {col + 1}) ist vorgegeben und nicht änderbar.")
        else:
            st.success(f"Aktives Feld: ({row + 1}, {col + 1})")

    st.markdown("**Zahlenfeld:**")
    pad_rows = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
    for number_row in pad_rows:
        cols = st.columns(3, gap="small")
        for index, number in enumerate(number_row):
            if cols[index].button(
                f"  {number}  ",
                key=f"num-{number}",
                use_container_width=True,
                disabled=not editable_selected,
            ):
                place_number(number)

    left, right = st.columns(2, gap="small")
    if left.button("🗑️ Löschen", use_container_width=True, disabled=not editable_selected):
        clear_selected_cell()

    keyboard_value = right.text_input(
        "Tastatur (1-9, 0=löschen)",
        value="",
        max_chars=1,
        disabled=not editable_selected,
    )
    if editable_selected and keyboard_value in "0123456789":
        if keyboard_value == "0":
            clear_selected_cell()
        else:
            place_number(int(keyboard_value))


def main():
    st.set_page_config(
        page_title="Sudoku Studio",
        page_icon="🎮",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    init_state()

    # CSS für elegantes Design mit Beige/Weiß Farbschema
    st.markdown("""
    <style>
    * { margin: 0; padding: 0; }
    body, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] {
        background-color: #f5f0e6 !important;
        color: #1f2933 !important;
    }
    [data-testid="stForm"], [data-testid="stContainer"] {
        background-color: #f5f0e6 !important;
    }
    button {
        background-color: #007f73 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
    }
    button:hover {
        background-color: #005a53 !important;
    }
    .stSelectbox label, .stToggle label {
        color: #1f2933 !important;
        font-weight: bold !important;
    }
    h1, h2, h3 {
        color: #1f2933 !important;
    }
    .stCaption, .stText {
        color: #52606d !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🎮 Sudoku Studio Web")
    st.caption("Kostenlose Web-Version für Handy und Desktop")

    st.divider()

    left_col, right_col = st.columns([2, 1], gap="medium")
    with left_col:
        difficulty = st.selectbox(
            "Schwierigkeit",
            list(DIFFICULTIES.keys()),
            index=list(DIFFICULTIES.keys()).index(st.session_state.difficulty),
            key="difficulty_select",
        )
        if difficulty != st.session_state.difficulty:
            start_new_game(difficulty)

    with right_col:
        if st.button("🔄 Neues Spiel", use_container_width=True):
            start_new_game(st.session_state.difficulty)

    st.divider()

    col_hint, col_solution, col_reset = st.columns(3, gap="small")
    if col_hint.button(
        "💡 Tipp (1x)",
        use_container_width=True,
        disabled=st.session_state.hint_used or st.session_state.game_locked,
    ):
        use_hint_once()
    
    if col_solution.button(
        "📋 Lösung",
        use_container_width=True,
        disabled=st.session_state.game_locked,
    ):
        reveal_solution()
    
    if col_reset.button("↻ Reset", use_container_width=True):
        start_new_game(st.session_state.difficulty)

    st.divider()

    if st.session_state.puzzle is None:
        start_new_game(st.session_state.difficulty)

    if st.session_state.status:
        if st.session_state.game_locked and "geloest" in st.session_state.status:
            st.success(st.session_state.status)
        else:
            st.info(st.session_state.status)
    
    if st.session_state.hint_text:
        st.warning(st.session_state.hint_text)

    render_board()
    render_controls()

    st.divider()
    st.caption("💡 Legende: Beige = vorgegeben | Hellblau = ausgewählt")


if __name__ == "__main__":
    main()
