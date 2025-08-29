@echo off
REM Windows installation script for qdrant-loader with dependency fixes
REM Supports Python 3.12 and 3.13
echo Installing Qdrant Loader for Windows...

REM Check if we're in the right directory
if not exist "packages\qdrant-loader\pyproject.toml" (
    echo ERROR: Must run from qdrant-loader root directory
    echo Current directory: %CD%
    exit /b 1
)

REM Check Python version
python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')"

echo Installing qdrant-loader package (Windows + Python 3.13 compatible)...
pip install -e packages/qdrant-loader

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install qdrant-loader
    echo Trying alternative approach for Windows/Python 3.13...
    
    REM Install compatible alternatives first
    pip install "tree-sitter>=0.20.0,<0.21"
    pip install "hnswlib>=0.7.0"
    pip install "python-markdown>=3.5.0"
    pip install "httpx>=0.24.0"
    
    REM Try installing without problematic deps
    pip install -e packages/qdrant-loader --no-deps
    pip install -r packages/qdrant-loader/requirements.txt 2>nul || echo No requirements.txt found
)

echo Installing qdrant-loader-mcp-server...
pip install -e packages/qdrant-loader-mcp-server

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install qdrant-loader-mcp-server
    exit /b 1
)

echo.
echo Installation completed!
echo.
echo To test the MCP server:
echo   python windows-mcp-wrapper.py
echo.
echo Required environment variables:
echo   set OPENAI_API_KEY=your_openai_key
echo   set QDRANT_URL=http://localhost:6333
echo   set QDRANT_COLLECTION_NAME=documents
echo.