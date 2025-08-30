# Updated Makefile targets for UV
# Replace existing targets in Makefile with these

.PHONY: help install install-dev test test-loader test-mcp test-coverage lint format clean build sync sync-dev lock

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# UV-based dependency management
sync: ## Sync all dependencies from lock file
	uv sync

sync-dev: ## Sync with dev dependencies
	uv sync --all-extras

lock: ## Update lock file
	uv lock

install: ## Install both packages in development mode
	uv pip install -e packages/qdrant-loader
	uv pip install -e packages/qdrant-loader-mcp-server

install-dev: ## Install with all extras (preferred)
	uv sync --all-extras

# Testing with UV
test: ## Run all tests
	uv run pytest packages/

test-loader: ## Run tests for qdrant-loader package only
	uv run pytest packages/qdrant-loader/tests/

test-mcp: ## Run tests for mcp-server package only
	uv run pytest packages/qdrant-loader-mcp-server/tests/

test-coverage: ## Run tests with coverage report
	uv run pytest packages/ --cov=packages --cov-report=html --cov-report=term-missing

# Linting and formatting with UV
lint: ## Run linting on all packages
	uv run ruff check packages/
	uv run mypy packages/

format: ## Format code in all packages
	uv run black packages/
	uv run isort packages/
	uv run ruff check --fix packages/

# Building with UV
build: ## Build both packages
	cd packages/qdrant-loader && uv run python -m build
	cd packages/qdrant-loader-mcp-server && uv run python -m build

build-loader: ## Build qdrant-loader package only
	cd packages/qdrant-loader && uv run python -m build

build-mcp: ## Build mcp-server package only
	cd packages/qdrant-loader-mcp-server && uv run python -m build

# Publishing (unchanged)
publish-loader: build-loader ## Publish qdrant-loader to PyPI
	cd packages/qdrant-loader && uv run python -m twine upload dist/*

publish-mcp: build-mcp ## Publish mcp-server to PyPI
	cd packages/qdrant-loader-mcp-server && uv run python -m twine upload dist/*

# Cleanup (updated)
clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf packages/*/dist/
	rm -rf packages/*/build/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -f uv.lock.tmp

# Development setup with UV
setup-dev: ## Set up development environment with UV
	uv sync --all-extras
	@echo "Development environment ready!"
	@echo "Dependencies synchronized via UV lock file"

check: lint test ## Run all checks (lint + test)

# Profiling (updated)
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
	@echo "Starting Prometheus metrics endpoint"
	uv run python -m qdrant_loader.metrics