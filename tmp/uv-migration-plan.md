# UV Migration Plan for qdrant-loader

## CRITICAL DOS AND DON'TS

### ✅ DOS
- **DO** use cmd.exe on Windows (not PowerShell unless necessary)
- **DO** fail fast without complex error handling
- **DO** validate each step before proceeding
- **DO** backup critical files before modifications
- **DO** test functionality before claiming completion
- **DO** report failures clearly and immediately
- **DO** use absolute paths for clarity
- **DO** keep commands simple and direct

### ❌ DON'TS
- **DON'T** create fallback mechanisms or workarounds
- **DON'T** claim success without validation
- **DON'T** use complex error recovery patterns
- **DON'T** create unnecessary documentation files
- **DON'T** assume commands work - always verify
- **DON'T** hide or compensate for errors
- **DON'T** add features beyond the migration scope
- **DON'T** use emojis in code or commits

### MIGRATION PHILOSOPHY
- **Simple is better** - Prefer fewer options over comprehensive coverage
- **Fail fast** - Stop immediately when something breaks
- **Be factual** - Report what happened, not what should have happened
- **No assumptions** - Test everything, assume nothing
- **Clean execution** - Each phase should complete fully or fail clearly

---

## Project Analysis

**Current Setup:**
- Monorepo with 2 Python packages
- Root workspace pyproject.toml + individual package pyproject.toml files
- Complex dependencies (200+ transitive deps)
- Makefile-based build automation
- Python 3.12-3.13 support

**Migration Goal:**
- Replace pip/conda with UV
- Maintain monorepo structure
- Keep existing pyproject.toml files (UV compatible)
- Update Makefile commands
- Generate uv.lock for reproducibility

---

## Phase 1: Preparation

### 1.1 Install UV
**Windows:**
```cmd
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 1.2 Backup Current State
```cmd
copy requirements.txt tmp\requirements.txt.backup
```

### 1.3 Validate Current Dependencies
```cmd
uv pip compile pyproject.toml > tmp\compiled-requirements.txt
uv pip compile packages\qdrant-loader\pyproject.toml > tmp\loader-requirements.txt
uv pip compile packages\qdrant-loader-mcp-server\pyproject.toml > tmp\mcp-requirements.txt
```

---

## Phase 2: Migration (REVISED)

### 2.1 Add UV Configuration to Root pyproject.toml
**NO build system changes - keep setuptools**
**NO uv init - work with existing structure**

Add to end of root `pyproject.toml`:
```toml
[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",
    "pre-commit>=3.0.0",
    "build>=0.10.0",
    "twine>=4.0.0",
]

[tool.uv.workspace]
members = ["packages/*"]
```

### 2.2 Generate Lock File
```cmd
uv lock
```
**Expected**: Creates `uv.lock` with all dependencies resolved
**Validation**: Check file exists and has content

### 2.3 Update Makefile (Incremental)
**Start with install-dev only as test**

Change lines 13-15 in Makefile:
```makefile
# FROM:
install-dev: ## Install both packages with development dependencies
	pip install -e packages/qdrant-loader[dev]
	pip install -e packages/qdrant-loader-mcp-server[dev]

# TO:
install-dev: ## Install both packages with development dependencies
	uv sync --all-extras
```

### 2.4 Test UV Sync
```cmd
uv sync --all-extras
```
**Validation**: Both packages should be importable

### 2.5 Update Remaining Makefile Commands (If 2.4 succeeds)
Only proceed if sync works. Update:
- `install` target to use `uv sync`
- Add new targets for `sync`, `lock`
- Update test/lint/format targets to use `uv run`

**STOP POINTS**:
- If `uv lock` fails with conflicts → STOP
- If `uv sync` cannot install packages → STOP
- If packages cannot be imported after sync → STOP

---

## Phase 3: Validation

### 3.1 Test Installation
```cmd
uv sync --all-extras
```

### 3.2 Verify Dependencies
```cmd
uv pip list
uv pip show qdrant-loader
uv pip show qdrant-loader-mcp-server
```

### 3.3 Run Test Suite
```cmd
uv run pytest packages/
```

### 3.4 Test Build Process
```cmd
uv run python -m build packages/qdrant-loader/
uv run python -m build packages/qdrant-loader-mcp-server/
```

### 3.5 Validate Scripts
```cmd
uv run qdrant-loader --help
uv run mcp-qdrant-loader --help
```

---

## Phase 4: Cleanup

### 4.1 Remove Old Files
```cmd
del requirements.txt
rmdir /s packages\qdrant_loader_workspace.egg-info
```

### 4.2 Update .gitignore
Add UV-specific entries:
```
# UV
.python-version
```

### 4.3 Update Documentation
Update build commands in README.md and CONTRIBUTING.md to use UV commands.

---

## Files Modified/Created/Deleted

### Created:
- `uv.lock` (root workspace lock)
- `tmp/uv-migration-plan.md` (this file)
- `tmp/*.txt` (backup and validation files)

### Modified:
- `pyproject.toml` (root - add workspace and UV config)
- `Makefile` (replace pip with uv commands)
- `.gitignore` (add UV entries)

### Deleted:
- `requirements.txt` (replaced by uv.lock)
- `packages/qdrant_loader_workspace.egg-info/` (build artifact)

---

## Command Reference

### Development Workflow
```cmd
# Install dependencies
uv sync --all-extras

# Add new dependency
uv add package-name

# Add dev dependency  
uv add --dev package-name

# Update all dependencies
uv lock --upgrade

# Run commands in UV environment
uv run pytest
uv run qdrant-loader --help

# Build packages
uv run python -m build packages/qdrant-loader/
```

### Cross-Platform Commands
**Windows:**
```cmd
uv sync --all-extras
uv run pytest packages/
```

**Linux:**
```bash
uv sync --all-extras
uv run pytest packages/
```

---

## Success Criteria

✅ UV lock file generated successfully  
✅ All dependencies resolved without conflicts  
✅ Test suite passes with UV environment  
✅ Both packages build successfully  
✅ Scripts execute correctly  
✅ Makefile targets work with UV commands  
✅ Cross-platform compatibility maintained  

---

## Rollback Plan

If migration fails:
```cmd
# Restore requirements.txt
copy tmp\requirements.txt.backup requirements.txt

# Remove UV files
del uv.lock

# Revert pyproject.toml changes
git checkout pyproject.toml Makefile

# Reinstall with pip
pip install -e packages/qdrant-loader[dev]
pip install -e packages/qdrant-loader-mcp-server[dev]
```