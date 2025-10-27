# AIAgents — local development

Quick commands to run the FastAPI app locally.

1. Activate the venv (from project root):

```bash
cd "/Users/austinle/Documents/UrSaviour-Project 2"
source AIAgents/.venv/bin/activate
```

2. Start the server (recommended):

```bash
# from repo root
./start_server.sh
```

Or use make:

```bash
make run
```

Notes
- Running from the repository root ensures the `AIAgents` package is importable as `AIAgents`.
- If you prefer to run from inside the `AIAgents/` folder, use `uvicorn main:app --reload --port 8000` instead.
