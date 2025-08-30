.PHONY: help install install-dev test test-loader test-mcp test-coverage lint format clean build publish-loader publish-mcp docs

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install both packages in development mode
	uv sync

install-dev: ## Install both packages with development dependencies
	uv sync --all-extras --all-packages

sync: ## Sync all dependencies from lock file
	uv sync

sync-dev: ## Sync with dev dependencies
	uv sync --all-extras --all-packages

lock: ## Update lock file
	uv lock

test: ## Run all tests
	uv run pytest packages/

test-loader: ## Run tests for qdrant-loader package only
	uv run pytest packages/qdrant-loader/tests/

test-mcp: ## Run tests for mcp-server package only
	uv run pytest packages/qdrant-loader-mcp-server/tests/

test-coverage: ## Run tests with coverage report
	uv run pytest packages/ --cov=packages --cov-report=html --cov-report=term-missing

lint: ## Run linting on all packages
	uv run ruff check packages/
	uv run mypy packages/

format: ## Format code in all packages
	uv run black packages/
	uv run isort packages/
	uv run ruff check --fix packages/

clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf packages/*/dist/
	rm -rf packages/*/build/
	rm -rf packages/*/src/*.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage coverage.xml
	rm -rf .pytest_cache/

build: ## Build both packages
	cd packages/qdrant-loader && uv run python -m build
	cd packages/qdrant-loader-mcp-server && uv run python -m build

build-loader: ## Build qdrant-loader package only
	cd packages/qdrant-loader && uv run python -m build

build-mcp: ## Build mcp-server package only
	cd packages/qdrant-loader-mcp-server && uv run python -m build

publish-loader: build-loader ## Publish qdrant-loader to PyPI
	cd packages/qdrant-loader && uv run python -m twine upload dist/*

publish-mcp: build-mcp ## Publish mcp-server to PyPI
	cd packages/qdrant-loader-mcp-server && uv run python -m twine upload dist/*

docs: ## Generate documentation
	@echo "Documentation generation not yet implemented"

setup-dev: ## Set up development environment with UV
	uv venv --python 3.12
	@echo "Virtual environment created with UV"
	@echo "Dependencies managed automatically with 'make install-dev'"

check: lint test ## Run all checks (lint + test)

profile-pyspy:
	@echo "Running py-spy..."
	uv run python -m qdrant_loader.cli.cli ingest --source-type=localfile & \
	PID=$$!; sleep 2; py-spy record -o profile.svg --pid $$PID; kill $$PID; echo "Flamegraph saved to profile.svg"

profile-cprofile:
	@echo "Running cProfile..."
	uv run python -m qdrant_loader.cli.cli ingest --source-type=localfile --profile
	@echo "Opening SnakeViz..."
	uv run snakeviz profile.out

metrics:
	@echo "Starting Prometheus metrics endpoint (to be implemented)"
	# TODO: Implement metrics endpoint and start it here

build-nuitka-loader: ## Build standalone executable for qdrant-loader using Nuitka
	@echo "Building qdrant-loader standalone executable with Nuitka..."
	@uv run python -c "import nuitka" 2>/dev/null || (echo "Installing Nuitka..." && uv pip install nuitka)
	cd packages/qdrant-loader && uv run python -m nuitka \
		--standalone \
		--onefile \
		--windows-console-mode=attach \
		--enable-plugin=no-qt \
		--assume-yes-for-downloads \
		--output-filename=qdrant-loader.exe \
		--include-package=qdrant_loader \
		--follow-imports \
		src/qdrant_loader/main.py

build-nuitka-mcp: ## Build standalone executable for MCP server using Nuitka
	@echo "Building MCP server standalone executable with Nuitka..."
	@uv run python -c "import nuitka" 2>/dev/null || (echo "Installing Nuitka..." && uv pip install nuitka)
	cd packages/qdrant-loader-mcp-server && uv run python -m nuitka \
		--standalone \
		--onefile \
		--windows-console-mode=attach \
		--enable-plugin=no-qt \
		--assume-yes-for-downloads \
		--output-filename=mcp-qdrant-loader.exe \
		--include-package=qdrant_loader_mcp_server \
		--follow-imports \
		src/qdrant_loader_mcp_server/main.py

build-nuitka: build-nuitka-loader build-nuitka-mcp ## Build both standalone executables 