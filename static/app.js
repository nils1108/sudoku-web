const GRID_SIZE = 9;
const BOX_SIZE = 3;

const state = {
    difficulty: "Leicht",
    puzzle: [],
    solution: [],
    board: [],
    fixedCells: new Set(),
    selectedCell: null,
    showSolution: false,
    locked: false,
    hintUsed: false,
    status: "Bereit",
    hintText: "",
};

const el = {
    difficultySelect: document.getElementById("difficulty-select"),
    newGameBtn: document.getElementById("new-game-btn"),
    hintBtn: document.getElementById("hint-btn"),
    solveBtn: document.getElementById("solve-btn"),
    resetBtn: document.getElementById("reset-btn"),
    clearBtn: document.getElementById("clear-btn"),
    statusBox: document.getElementById("status-box"),
    hintBox: document.getElementById("hint-box"),
    selectionBox: document.getElementById("selection-box"),
    grid: document.getElementById("sudoku-grid"),
    numberPad: document.getElementById("number-pad"),
};

function deepCopyBoard(board) {
    return board.map((row) => row.slice());
}

function cellKey(row, col) {
    return `${row}-${col}`;
}

function isFixed(row, col) {
    return state.fixedCells.has(cellKey(row, col));
}

function isSelected(row, col) {
    return !!state.selectedCell && state.selectedCell[0] === row && state.selectedCell[1] === col;
}

function setStatus(message, kind = "info") {
    state.status = message;
    el.statusBox.textContent = message;
    el.statusBox.className = `status ${kind}`;
}

function setHint(message) {
    state.hintText = message;
    if (message) {
        el.hintBox.textContent = message;
        el.hintBox.classList.remove("hidden");
    } else {
        el.hintBox.textContent = "";
        el.hintBox.classList.add("hidden");
    }
}

function updateSelectionBox() {
    if (!state.selectedCell) {
        el.selectionBox.textContent = "Wähle zuerst ein Feld aus.";
        el.selectionBox.className = "status info";
        return;
    }

    const [row, col] = state.selectedCell;
    if (isFixed(row, col)) {
        el.selectionBox.textContent = `Feld (${row + 1}, ${col + 1}) ist vorgegeben und nicht änderbar.`;
        el.selectionBox.className = "status info";
    } else {
        el.selectionBox.textContent = `Aktives Feld: (${row + 1}, ${col + 1})`;
        el.selectionBox.className = "status info";
    }
}

function renderGrid() {
    el.grid.innerHTML = "";

    for (let row = 0; row < GRID_SIZE; row += 1) {
        for (let col = 0; col < GRID_SIZE; col += 1) {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "sudoku-cell";
            button.dataset.row = String(row);
            button.dataset.col = String(col);

            if ((col + 1) % BOX_SIZE === 0) button.classList.add("box-right");
            if ((row + 1) % BOX_SIZE === 0) button.classList.add("box-bottom");
            if (isFixed(row, col)) button.classList.add("fixed");
            if (isSelected(row, col)) button.classList.add("selected");

            const value = state.showSolution ? state.solution[row][col] : state.board[row][col];
            button.textContent = value ? String(value) : "";
            button.disabled = state.locked;
            button.addEventListener("click", () => selectCell(row, col));
            el.grid.appendChild(button);
        }
    }
}

function renderPad() {
    el.numberPad.innerHTML = "";
    const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9];

    numbers.forEach((number) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = String(number);
        button.disabled = !canEditSelectedCell();
        button.addEventListener("click", () => placeNumber(number));
        el.numberPad.appendChild(button);
    });
}

function canEditSelectedCell() {
    if (!state.selectedCell) return false;
    if (state.locked || state.showSolution) return false;
    const [row, col] = state.selectedCell;
    return !isFixed(row, col);
}

function selectCell(row, col) {
    if (state.locked) {
        setStatus("Spiel ist beendet. Starte ein neues Spiel.", "info");
        return;
    }

    state.selectedCell = [row, col];
    if (isFixed(row, col)) {
        setStatus(`Feld (${row + 1}, ${col + 1}) ist vorgegeben.`, "info");
    } else {
        setStatus(`Feld (${row + 1}, ${col + 1}) ausgewählt.`, "info");
    }
    updateSelectionBox();
    renderGrid();
    renderPad();
}

function placeNumber(value) {
    if (!canEditSelectedCell()) return;

    const [row, col] = state.selectedCell;
    state.board[row][col] = value;
    setStatus(`Zahl ${value} gesetzt in Feld (${row + 1}, ${col + 1}).`, "info");
    setHint("");
    checkIfCompleted();
    renderGrid();
    renderPad();
}

function clearSelectedCell() {
    if (!canEditSelectedCell()) return;

    const [row, col] = state.selectedCell;
    state.board[row][col] = 0;
    setStatus(`Feld (${row + 1}, ${col + 1}) geleert.`, "info");
    setHint("");
    renderGrid();
    renderPad();
}

function revealSolution() {
    if (state.locked) {
        setStatus("Lösung wurde bereits gezeigt.", "info");
        return;
    }

    state.showSolution = true;
    state.locked = true;
    state.board = deepCopyBoard(state.solution);
    setStatus("Lösung angezeigt. Spiel ist beendet.", "info");
    setHint("");
    renderGrid();
    renderPad();
    updateSelectionBox();
}

function useHintOnce() {
    if (state.locked) {
        setStatus("Kein Tipp mehr möglich. Spiel ist beendet.", "info");
        return;
    }
    if (state.hintUsed) {
        setStatus("Tipp wurde bereits verwendet.", "info");
        return;
    }

    const wrongCells = [];
    for (let row = 0; row < GRID_SIZE; row += 1) {
        for (let col = 0; col < GRID_SIZE; col += 1) {
            if (isFixed(row, col)) continue;
            const value = state.board[row][col];
            if (value !== 0 && value !== state.solution[row][col]) {
                wrongCells.push([row, col, value]);
            }
        }
    }

    if (wrongCells.length > 0) {
        const [row, col, value] = wrongCells[Math.floor(Math.random() * wrongCells.length)];
        state.selectedCell = [row, col];
        setHint(`Tipp: In Feld (${row + 1}, ${col + 1}) ist die ${value} aktuell falsch.`);
        state.hintUsed = true;
        setStatus("Tipp genutzt: Falsche Zahl gefunden.", "info");
        updateSelectionBox();
        renderGrid();
        renderPad();
        return;
    }

    for (let row = 0; row < GRID_SIZE; row += 1) {
        const emptyCols = [];
        for (let col = 0; col < GRID_SIZE; col += 1) {
            if (state.board[row][col] === 0) emptyCols.push(col);
        }
        if (emptyCols.length === 1) {
            const col = emptyCols[0];
            const value = state.solution[row][col];
            state.selectedCell = [row, col];
            setHint(`Tipp: Reihe ${row + 1} ist leicht. In Spalte ${col + 1} gehört die ${value}.`);
            state.hintUsed = true;
            setStatus("Tipp genutzt: Einfache Reihe gefunden.", "info");
            updateSelectionBox();
            renderGrid();
            renderPad();
            return;
        }
    }

    setHint("Kein passender Tipp verfügbar.");
    setStatus("Tipp geprüft: aktuell kein leichter Hinweis.", "info");
}

function checkIfCompleted() {
    for (let row = 0; row < GRID_SIZE; row += 1) {
        for (let col = 0; col < GRID_SIZE; col += 1) {
            if (state.board[row][col] === 0) return;
        }
    }

    const solved = state.board.every((row, rowIndex) =>
        row.every((value, colIndex) => value === state.solution[rowIndex][colIndex])
    );

    if (solved) {
        state.locked = true;
        setStatus("Perfekt gelöst!", "info");
        setHint("Stark! Du hast das Sudoku korrekt gelöst.");
    } else {
        setStatus("Noch nicht korrekt.", "info");
    }
}

function resetGameState(payload) {
    state.difficulty = payload.difficulty;
    state.puzzle = payload.puzzle;
    state.solution = payload.solution;
    state.board = deepCopyBoard(payload.puzzle);
    state.fixedCells = new Set(payload.fixed_cells.map(([row, col]) => cellKey(row, col)));
    state.selectedCell = null;
    state.showSolution = false;
    state.locked = false;
    state.hintUsed = false;
    setHint("");
    setStatus(`Neues Spiel gestartet: ${payload.difficulty}`, "info");
    updateSelectionBox();
    renderGrid();
    renderPad();
}

async function loadGame(difficulty) {
    const response = await fetch(`/api/new-game?difficulty=${encodeURIComponent(difficulty)}`);
    if (!response.ok) {
        throw new Error("Spiel konnte nicht geladen werden");
    }
    const payload = await response.json();
    resetGameState(payload);
}

function bindEvents() {
    el.newGameBtn.addEventListener("click", async () => {
        await loadGame(el.difficultySelect.value);
    });

    el.difficultySelect.addEventListener("change", async () => {
        await loadGame(el.difficultySelect.value);
    });

    el.hintBtn.addEventListener("click", useHintOnce);
    el.solveBtn.addEventListener("click", revealSolution);
    el.resetBtn.addEventListener("click", async () => {
        await loadGame(el.difficultySelect.value);
    });
    el.clearBtn.addEventListener("click", clearSelectedCell);

    window.addEventListener("keydown", (event) => {
        const targetTag = event.target?.tagName?.toLowerCase();
        if (["input", "textarea", "select"].includes(targetTag)) {
            return;
        }

        if (/^[1-9]$/.test(event.key)) {
            if (canEditSelectedCell()) {
                event.preventDefault();
                placeNumber(Number(event.key));
            }
            return;
        }

        if (event.key === "0" || event.key === "Backspace" || event.key === "Delete") {
            if (canEditSelectedCell()) {
                event.preventDefault();
                clearSelectedCell();
            }
        }
    });
}

async function init() {
    bindEvents();
    await loadGame(el.difficultySelect.value || document.body.dataset.defaultDifficulty || "Leicht");
}

init().catch((error) => {
    console.error(error);
    setStatus("Fehler beim Laden des Spiels. Bitte Seite neu laden.", "info");
});
