# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Package Manager

**This project uses UV** - a fast Rust-based Python package manager (10-100x faster than pip).
- **Lock file**: `uv.lock` tracks all dependencies with exact versions
- **Workspace**: Both packages managed as workspace members in root `pyproject.toml`
- **No pip/conda needed**: UV handles everything including virtual environments

### UV Quick Reference
```bash
# Install UV (if not present)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/Mac
winget install ezwinports.make                    # Windows

# Essential commands
uv sync                        # Install base dependencies
uv sync --all-extras --all-packages  # Install with dev dependencies
uv lock                        # Update lock file after dependency changes
uv run <command>              # Run any command in UV environment
uv run pytest                 # Run tests
uv run qdrant-loader          # Run CLI tools
```

### Development Commands (via make or UV)

**Package Management**
- `make install-dev` or `uv sync --all-extras --all-packages` - Full dev install
- `make install` or `uv sync` - Basic installation
- `make sync` or `uv sync` - Sync from lock file

**Testing** (run from package directory for config.test.yaml)
- `make test` or `cd packages/qdrant-loader && uv run pytest`
- `make test-loader` - Test core package only
- `make test-mcp` - Test MCP server only
- `make test-coverage` - With coverage report

**Code Quality**
- `make lint` or `uv run ruff check && uv run mypy`
- `make format` or `uv run black . && uv run isort .`
- `make check` - Lint + test

**Building**
- `make build` or `uv run python -m build`
- `make build-loader` - Core package only
- `make build-mcp` - MCP server only

### Known Issues & Fixes

**scipy/gensim incompatibility**
- gensim 4.3.x incompatible with scipy >=1.13 (triu function moved)
- Fixed via version constraints in `packages/qdrant-loader/pyproject.toml`

**Windows make command**
- Install via: `winget install ezwinports.make`
- Restart shell after installation for PATH update
- Alternative: Run UV commands directly without make

**Test execution directory**
- Tests must run from package directory to find `config.test.yaml`
- Use: `cd packages/qdrant-loader && uv run pytest`

## Architecture Overview

### Monorepo Structure
This is a monorepo containing two complementary packages:

1. **qdrant-loader** (`packages/qdrant-loader/`): Core data ingestion and processing engine
2. **qdrant-loader-mcp-server** (`packages/qdrant-loader-mcp-server/`): MCP server for AI development tool integration

### Core Package (`qdrant-loader`)
- **Entry point**: `qdrant_loader/main.py` with CLI at `main:cli`
- **CLI commands**: init, ingest, config, project (implemented in `qdrant_loader/cli/`)
- **Connectors**: Git, Confluence, JIRA, Local Files, Public Docs (in `qdrant_loader/connectors/`)
- **Core pipeline**: Async ingestion pipeline with document processing, embedding, and vector storage
- **State management**: SQLite-based with async support for incremental updates
- **File conversion**: Uses MarkItDown library for 20+ file formats

### MCP Server Package (`qdrant-loader-mcp-server`)
- **Entry point**: `qdrant_loader_mcp_server/__main__.py` with CLI at `cli.py`
- **Protocol**: MCP (Model Context Protocol) compliance for AI development tools
- **Search capabilities**: Semantic search, hierarchy-aware search, cross-document intelligence
- **Transport**: HTTP and MCP protocol handlers

### Key Architecture Patterns
- **Connector-based architecture**: BaseConnector interface with connector-specific implementations
- **Async processing**: Built on async/await patterns throughout
- **State tracking**: SQLite + SQLAlchemy async engine for incremental updates
- **Batch processing**: Configurable batch sizes for efficient operations
- **Project isolation**: Multi-project workspace support with separate state management

### Configuration System
- **Workspace-based**: Uses `config.yaml` and `.env` files in workspace directories
- **Multi-project**: Single workspace can contain multiple projects with shared collections
- **Environment variables**: Supports variable substitution in configuration
- **Validation**: Pydantic-based configuration validation

## Development Practices

### Python Version
- **Required**: Python 3.12+ (<=3.13 for core package)
- **Platform-specific dependencies**: Handles Windows compatibility issues

### Testing Framework
- **pytest** with async support (`pytest-asyncio`)
- **Coverage reporting** with `pytest-cov`
- **Markers**: slow, integration, unit tests
- **Mock support**: Uses `pytest-mock` and `responses` for HTTP mocking

### Code Standards
- **Formatter**: black (88 char line length)
- **Import sorting**: isort with black profile
- **Linting**: ruff with specific rule configuration
- **Type checking**: mypy with strict settings
- **Python version target**: 3.12

### Key Dependencies
- **Vector database**: qdrant-client for vector storage
- **Embeddings**: OpenAI API (text-embedding-3-small default)
- **Web scraping**: httpx, beautifulsoup4, requests
- **CLI**: click framework
- **Config**: pydantic + pydantic-settings
- **Async database**: SQLAlchemy + aiosqlite
- **Document processing**: langchain, tiktoken
- **File conversion**: markitdown (platform-dependent)

## Common Development Tasks

### Adding a New Connector
1. Create connector class inheriting from `BaseConnector` in `qdrant_loader/connectors/`
2. Implement `get_documents()` async method returning list of `Document` objects
3. Add configuration model in connector's `config.py`
4. Update `PipelineOrchestrator._collect_documents_from_sources()` to handle new connector
5. Add comprehensive tests in `tests/unit/connectors/`

### Working with State Management
- State is SQLite-based using async SQLAlchemy
- Document state tracking uses content hashing for change detection
- Project-aware queries and updates throughout
- State manager must be initialized with `async with` context

### MCP Server Development
- Follows MCP protocol specification
- Search handlers implement various search strategies
- Transport layer handles both HTTP and MCP protocol
- Rich search capabilities including cross-document intelligence

### Testing Guidelines
- Use `pytest` with async fixtures
- Mock external services (HTTP, OpenAI API, QDrant)
- Test both unit and integration scenarios
- Use appropriate markers for test categorization

## Windows Compatibility Notes
- Uses cmd.exe compatible commands in documentation
- Platform-specific dependencies (tree-sitter, markitdown) have conditional requirements
- Path handling uses Windows-compatible patterns
- Batch files use `.cmd` extension