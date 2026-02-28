# Makefile for FastAPI + Vue (Vite) project

.DEFAULT_GOAL := help

.PHONY: help sync frontend-sync format lint lint-frontend format-frontend check test run run-backend run-frontend ci clean

# -----------------------
# General help
# -----------------------
help:
	@echo "Available targets:"
	@echo "  sync             Install/sync Python dependencies"
	@echo "  frontend-sync    Install Node dependencies"
	@echo "  format           Auto-format Python code with ruff"
	@echo "  format-frontend  Auto-format frontend code with prettier/eslint"
	@echo "  lint             Lint Python code with ruff"
	@echo "  lint-frontend    Lint frontend code with eslint"
	@echo "  check            Run format + lint (Python + frontend)"
	@echo "  test             Run Python unit tests with coverage"
	@echo "  run-backend      Run FastAPI app only"
	@echo "  run-frontend     Run Vue (Vite) frontend only"
	@echo "  run              Run backend + frontend concurrently"
	@echo "  ci               Full CI pipeline"
	@echo "  clean            Remove cache files"

# -----------------------
# Dependency sync
# -----------------------
sync:
	uv -V
	uv sync --all-groups

frontend-sync:
	cd frontend && npm ci

# -----------------------
# Python formatting & linting
# -----------------------
format:
	uv run ruff format .

lint:
	uv run ruff check --fix

# -----------------------
# Frontend formatting & linting
# -----------------------
format-frontend:
	cd frontend && npm run format

lint-frontend:
	cd frontend && npm run lint

# -----------------------
# Check all code
# -----------------------
check: format lint format-frontend lint-frontend

# -----------------------
# Python tests
# -----------------------
test:
	uv run coverage run -m pytest -v -s
	uv run coverage html
	uv run coverage report -m

# -----------------------
# CLI
# -----------------------
cli:
	uv run python -m app.cli

# -----------------------
# Run backend / frontend
# -----------------------
BACKEND_PORT ?= 8000

run-backend:
	@echo "Running FastAPI app on http://127.0.0.1:$(BACKEND_PORT)"
	uv run uvicorn app.api:app --reload --port $(BACKEND_PORT) --timeout-graceful-shutdown 1 --log-config logging.conf

run-frontend:
	@echo "Running Vite dev server on http://localhost:5173"
	cd frontend && npm run dev

# Run backend + frontend concurrently (requires & or tmux)
run:
	@echo "Running backend + frontend"
	$(MAKE) run-backend & $(MAKE) run-frontend

# -----------------------
# CI
# -----------------------
ci: sync frontend-sync check test

# -----------------------
# Clean caches
# -----------------------
clean:
	rm -rf .ruff_cache .pytest_cache htmlcov .coverage __pycache__
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete