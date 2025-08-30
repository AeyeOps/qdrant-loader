# UV Migration Commands

## Phase 1: Preparation Commands

### Install UV (Windows)
```cmd
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install UV (Linux)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Backup and Validate
```cmd
copy requirements.txt tmp\requirements.txt.backup
uv pip compile pyproject.toml > tmp\compiled-requirements.txt
```

## Phase 2: Migration Commands

### Initialize UV Workspace
```cmd
uv init --workspace
```

### Update pyproject.toml (manual step)
- Add workspace config from `tmp/uv-workspace-config.toml` to root `pyproject.toml`

### Replace Makefile (manual step)  
- Replace Makefile targets with content from `tmp/makefile-uv-updates.mk`

### Generate Lock File
```cmd
uv lock
```

## Phase 3: Validation Commands

### Test Installation
```cmd
uv sync --all-extras
```

### Verify Environment
```cmd
uv pip list
uv pip show qdrant-loader
uv pip show qdrant-loader-mcp-server
```

### Test Commands
```cmd
uv run pytest packages/
uv run qdrant-loader --help
uv run mcp-qdrant-loader --help
```

### Test Building
```cmd
uv run python -m build packages/qdrant-loader/
uv run python -m build packages/qdrant-loader-mcp-server/
```

## Phase 4: Cleanup Commands

### Remove Old Files
```cmd
del requirements.txt
rmdir /s packages\qdrant_loader_workspace.egg-info
```

### Update .gitignore (manual step)
Add: `.python-version`

## Daily Workflow Commands

### Install Dependencies
```cmd
uv sync --all-extras
```

### Add New Dependency
```cmd
uv add package-name
uv add --dev package-name  # for dev dependencies
```

### Run Tests
```cmd
make test          # or uv run pytest packages/
make test-coverage # or uv run pytest packages/ --cov=packages
```

### Format Code
```cmd
make format   # or uv run black packages/ && uv run isort packages/
```

### Build Packages
```cmd
make build    # or individual: make build-loader, make build-mcp
```

## Emergency Rollback Commands

```cmd
copy tmp\requirements.txt.backup requirements.txt
del uv.lock
git checkout pyproject.toml Makefile
pip install -e packages/qdrant-loader[dev]
pip install -e packages/qdrant-loader-mcp-server[dev]
```