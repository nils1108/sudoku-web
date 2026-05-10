# Sudoku Studio Web

FastAPI browser version of the Sudoku app with a custom HTML/CSS/JavaScript frontend.

## Run locally

```bash
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000`.

## Notes

- `main.py` is the only app entry point.
- The Sudoku board uses a real HTML grid, so the 3x3 borders and colors are fully under control.
- The browser UI is the only supported version in this workspace.
