@echo off
cd /d C:\dev\qdrant-loader
echo Starting MCP server install test...
C:\Users\steve\miniforge3\Scripts\pip.exe install -e packages\qdrant-loader-mcp-server > install-result.log 2>&1
echo Install completed with exit code: %ERRORLEVEL%
type install-result.log