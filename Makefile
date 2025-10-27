.PHONY: run

run:
	bash -lc 'cd "$(PWD)" && if [ -f "AIAgents/.venv/bin/activate" ]; then source AIAgents/.venv/bin/activate; fi && uvicorn AIAgents.main:app --reload --port 8000'
