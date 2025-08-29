# Windows + Python 3.13 Compatibility Fixes for qdrant-loader-mcp-server

## Problem Summary

The qdrant-loader-mcp-server fails on Windows due to multiple compatibility issues:

1. **Signal Handler Issue**: `NotImplementedError` when using `loop.add_signal_handler()`
2. **Pipe Transport Issue**: `_ProactorReadPipeTransport` failures with stdin handling  
3. **Dependency Resolution**: `tree-sitter-languages` has no compatible wheels for Python 3.13
4. **Python 3.13 Compatibility**: Several packages don't support Python 3.13 yet
5. **Configuration Issues**: Missing environment variables and collection setup

## Root Causes

### 1. Signal Handler Problem
**Error**: `NotImplementedError` at `cli.py:492`
**Cause**: Windows doesn't support Unix-style signal handlers in asyncio
**Fix**: Use threading-based signal handlers on Windows

### 2. Pipe Transport Problem  
**Error**: `AttributeError: '_ProactorReadPipeTransport' object has no attribute '_empty_waiter'`
**Cause**: Windows ProactorEventLoop incompatibility with stdin pipe handling
**Fix**: Use SelectorEventLoop on Windows + thread-based stdin reading

### 3. Dependency Problem
**Error**: `tree-sitter-languages>=1.10.0 has no wheels with a matching Python ABI tag`
**Cause**: Package not available for all Python versions/platforms
**Fix**: Platform-specific dependency declarations

### 4. Python 3.13 Compatibility
**Error**: Multiple packages (faiss-cpu, tree-sitter-languages, markitdown, jsonrpcclient/jsonrpcserver) don't support Python 3.13
**Cause**: Newer Python version, packages haven't been updated yet
**Fix**: Version-specific dependency constraints with alternatives

## Solutions Implemented

### 1. Enhanced Windows Wrapper (`windows-mcp-wrapper.py`)

```python
# Key fixes:
- Uses SelectorEventLoop instead of ProactorEventLoop on Windows
- Threading-based signal handlers replace asyncio signal handlers
- Binary mode stdin configuration
- Comprehensive error handling and environment validation
- Platform-specific patching (only applies fixes on Windows)
```

### 2. Dependency Fixes (`pyproject.toml`)

**Platform-specific dependencies:**
```toml
# Windows exclusions
"tree-sitter-languages>=1.10.0; platform_system!='Windows' and python_version<'3.13'",

# Python 3.13 alternatives  
"faiss-cpu>=1.7.4; python_version<'3.13'",
"hnswlib>=0.7.0; python_version>='3.13'",
"markitdown>=0.1.2; python_version<'3.13'",  
"python-markdown>=3.5.0; python_version>='3.13'",
"jsonrpcclient>=4.0.3; python_version<'3.13'",
"jsonrpcserver>=5.0.7; python_version<'3.13'",
"httpx>=0.24.0; python_version>='3.13'",
```

**Python version support:**
```toml
requires-python = ">=3.12,<=3.13"
```

### 3. Installation Script (`install-windows.cmd`)

Handles the complete Windows installation process with fallbacks.

## Usage

### 1. Install the fixed version:
```cmd
cd C:\dev\qdrant-loader
install-windows.cmd
```

### 2. Configure environment:
```cmd
set OPENAI_API_KEY=your_openai_key
set QDRANT_URL=http://localhost:6333
set QDRANT_COLLECTION_NAME=documents
```

### 3. Update Claude MCP configuration:

Replace the existing qdrant-loader-docs configuration in `C:\Users\steve\.claude.json`:

```json
"qdrant-loader-docs": {
  "command": "python",
  "args": [
    "C:\\dev\\qdrant-loader\\windows-mcp-wrapper.py"
  ],
  "env": {
    "OPENAI_API_KEY": "your_openai_key",
    "QDRANT_URL": "http://localhost:6333", 
    "QDRANT_COLLECTION_NAME": "documents"
  }
}
```

## Testing

Test the MCP server directly:
```cmd
cd C:\dev\qdrant-loader
python windows-mcp-wrapper.py
```

Should show:
```
Starting Qdrant Loader MCP Server (Windows Edition)
Windows patches applied successfully
Windows stdio configured
Starting MCP server...
```

## Benefits

1. **Full Windows Compatibility**: Fixes all platform-specific issues
2. **Preserves Cross-Platform Support**: Only applies fixes when running on Windows
3. **Enhanced Error Handling**: Better diagnostics and graceful degradation
4. **Environment Validation**: Checks required variables before startup
5. **Easy Installation**: Automated setup with fallback strategies

## Migration Path

1. **Current MCP config** → Uses problematic uvx wrapper
2. **Fixed MCP config** → Uses local patched installation
3. **Future upstream fixes** → Can revert to standard installation

The fixes are designed to be temporary patches until the upstream project addresses Windows compatibility.