# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management
- **Install for development**: `make install-dev` - Installs both packages with dev dependencies
- **Install packages only**: `make install` - Basic installation without dev dependencies

### Testing
- **Run all tests**: `make test` or `pytest packages/`
- **Test core package only**: `make test-loader` or `pytest packages/qdrant-loader/tests/`
- **Test MCP server only**: `make test-mcp` or `pytest packages/qdrant-loader-mcp-server/tests/`
- **Test with coverage**: `make test-coverage`

### Code Quality
- **Lint code**: `make lint` - Runs ruff and mypy
- **Format code**: `make format` - Runs black, isort, and ruff --fix
- **All checks**: `make check` - Runs lint + test

### Building
- **Build both packages**: `make build`
- **Build core only**: `make build-loader` 
- **Build MCP server only**: `make build-mcp`

### Utilities
- **Clean artifacts**: `make clean`
- **Setup dev environment**: `make setup-dev` (creates venv, requires manual activation)

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