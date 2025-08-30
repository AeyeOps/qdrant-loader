@echo off
REM Nuitka Build Script for qdrant-loader
REM Optimized standalone executables for Windows

echo ========================================
echo Nuitka Build System for qdrant-loader
echo ========================================
echo.

REM Check Python version
python --version 2>nul | findstr /C:"3.12" /C:"3.13" >nul
if errorlevel 1 (
    echo ERROR: Python 3.12 or 3.13 required
    exit /b 1
)

REM Install Nuitka if needed
pip show nuitka >nul 2>&1
if errorlevel 1 (
    echo Installing Nuitka...
    pip install nuitka ordered-set zstandard
)

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
mkdir dist

REM Build qdrant-loader executable
echo.
echo Building qdrant-loader.exe...
echo ----------------------------------------
python -m nuitka ^
    --standalone ^
    --onefile ^
    --windows-console-mode=force ^
    --windows-company-name="AeyeOps" ^
    --windows-product-name="Qdrant Loader" ^
    --windows-file-version="0.6.2.0" ^
    --windows-product-version="0.6.2.0" ^
    --output-filename="qdrant-loader.exe" ^
    --output-dir="dist" ^
    --include-package="qdrant_loader" ^
    --include-package="openai" ^
    --include-package="qdrant_client" ^
    --include-package="tiktoken" ^
    --include-package="tiktoken_ext" ^
    --include-package="langchain" ^
    --include-package="langchain_core" ^
    --include-package="langchain_community" ^
    --include-package="pydantic" ^
    --include-package="click" ^
    --include-package="yaml" ^
    --include-package="dotenv" ^
    --include-package="structlog" ^
    --include-package="httpx" ^
    --include-package="certifi" ^
    --include-package-data="qdrant_loader" ^
    --include-package-data="tiktoken" ^
    --include-package-data="certifi" ^
    --assume-yes-for-downloads ^
    --remove-output ^
    --show-progress ^
    --show-memory ^
    packages/qdrant-loader/src/qdrant_loader/main.py

if errorlevel 1 (
    echo ERROR: Failed to build qdrant-loader.exe
    exit /b 1
)

REM Build mcp-qdrant-loader executable
echo.
echo Building mcp-qdrant-loader.exe...
echo ----------------------------------------
python -m nuitka ^
    --standalone ^
    --onefile ^
    --windows-console-mode=force ^
    --windows-company-name="AeyeOps" ^
    --windows-product-name="Qdrant Loader MCP Server" ^
    --windows-file-version="0.6.1.0" ^
    --windows-product-version="0.6.1.0" ^
    --output-filename="mcp-qdrant-loader.exe" ^
    --output-dir="dist" ^
    --include-package="qdrant_loader_mcp_server" ^
    --include-package="qdrant_loader" ^
    --include-package="fastapi" ^
    --include-package="uvicorn" ^
    --include-package="starlette" ^
    --include-package="json_rpc" ^
    --include-package="openai" ^
    --include-package="qdrant_client" ^
    --include-package="pydantic" ^
    --include-package="yaml" ^
    --include-package="dotenv" ^
    --include-package-data="qdrant_loader_mcp_server" ^
    --assume-yes-for-downloads ^
    --remove-output ^
    --show-progress ^
    --show-memory ^
    packages/qdrant-loader-mcp-server/src/qdrant_loader_mcp_server/__main__.py

if errorlevel 1 (
    echo ERROR: Failed to build mcp-qdrant-loader.exe
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executables created in dist/
echo - dist\qdrant-loader.exe
echo - dist\mcp-qdrant-loader.exe
echo.
echo To use with embedded environment variables:
echo 1. Set OPENAI_API_KEY before running
echo 2. Or create .env file in same directory
echo.