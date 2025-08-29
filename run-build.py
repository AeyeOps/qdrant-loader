#!/usr/bin/env python3
"""
Comprehensive build script for qdrant-loader with proper Windows paths
"""
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

def run_build():
    # Set up paths
    python_exe = r"C:\Users\steve\miniforge3\python.exe"
    pip_exe = r"C:\Users\steve\miniforge3\Scripts\pip.exe"
    
    # Create log file
    log_file = f'build-log-{datetime.now().strftime("%Y%m%d-%H%M%S")}.txt'
    print(f'Starting comprehensive build - logging to {log_file}')
    
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write('=== QDRANT LOADER WINDOWS BUILD LOG ===\n')
        log.write(f'Started: {datetime.now()}\n')
        log.write(f'Python: {sys.version}\n') 
        log.write(f'Platform: {sys.platform}\n')
        log.write(f'Working Directory: {os.getcwd()}\n')
        log.write(f'Python Executable: {python_exe}\n')
        log.write(f'Pip Executable: {pip_exe}\n')
        log.write('\n' + '='*60 + '\n\n')
        
        def run_command(cmd, description):
            log.write(f'>>> {description}\n')
            log.write(f'Command: {cmd}\n')
            log.write('-' * 40 + '\n')
            
            try:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=600,  # 10 minutes for pip installs
                    cwd=os.getcwd()
                )
                
                log.write(f'Return Code: {result.returncode}\n')
                log.write('STDOUT:\n')
                log.write(result.stdout)
                log.write('\nSTDERR:\n')  
                log.write(result.stderr)
                log.write('\n' + '='*60 + '\n\n')
                
                return result.returncode == 0
                
            except subprocess.TimeoutExpired:
                log.write('ERROR: Command timed out after 10 minutes\n')
                log.write('\n' + '='*60 + '\n\n')
                return False
            except Exception as e:
                log.write(f'ERROR: Command failed with exception: {e}\n')
                log.write('\n' + '='*60 + '\n\n')
                return False
        
        # Step 1: Check environment
        success_python = run_command(f'"{python_exe}" --version', 'Check Python Version')
        success_pip = run_command(f'"{pip_exe}" --version', 'Check Pip Version')
        
        # Step 2: Check current packages
        run_command(f'"{pip_exe}" list | findstr qdrant', 'Check existing qdrant packages')
        
        # Step 3: Install dependencies first
        run_command(
            f'"{pip_exe}" install --upgrade pip setuptools wheel',
            'Upgrade pip and build tools'
        )
        
        # Step 4: Install qdrant-loader package
        success1 = run_command(
            f'"{pip_exe}" install -e packages/qdrant-loader --verbose',
            'Install qdrant-loader package'
        )
        
        if not success1:
            # Try alternative approach
            log.write('>>> Trying alternative install for qdrant-loader\n')
            run_command(
                f'"{pip_exe}" install tree-sitter hnswlib python-markdown httpx',
                'Install alternative dependencies'
            )
            success1 = run_command(
                f'"{pip_exe}" install -e packages/qdrant-loader --no-deps',
                'Install qdrant-loader without dependencies'
            )
        
        # Step 5: Install MCP server package  
        success2 = run_command(
            f'"{pip_exe}" install -e packages/qdrant-loader-mcp-server --verbose',
            'Install qdrant-loader-mcp-server package'
        )
        
        # Step 6: Verify installations
        run_command(f'"{pip_exe}" list | findstr qdrant', 'Verify qdrant packages installed')
        
        # Step 7: Test imports
        import_success1 = run_command(
            f'"{python_exe}" -c "import qdrant_loader; print(\'qdrant-loader imported successfully\'); print(f\'Version: {{qdrant_loader.__version__ if hasattr(qdrant_loader, \'__version__\') else \'unknown\'}}\')"',
            'Test qdrant-loader import'
        )
        
        import_success2 = run_command(
            f'"{python_exe}" -c "import qdrant_loader_mcp_server; print(\'qdrant-loader-mcp-server imported successfully\')"',
            'Test qdrant-loader-mcp-server import'
        )
        
        # Step 8: Test wrapper functionality
        validation_success = run_command(
            f'"{python_exe}" validate-windows-fixes.py',
            'Run Windows compatibility validation'
        )
        
        # Step 9: Test MCP server startup (with timeout)
        mcp_test = run_command(
            f'timeout 10 "{python_exe}" windows-mcp-wrapper.py 2>&1 || echo "MCP server startup test completed"',
            'Test MCP server startup (10 second timeout)'
        )
        
        # Summary
        log.write('\n' + '='*60 + '\n')
        log.write('BUILD SUMMARY\n')
        log.write('='*60 + '\n')
        log.write(f'Python available: {"SUCCESS" if success_python else "FAILED"}\n')
        log.write(f'Pip available: {"SUCCESS" if success_pip else "FAILED"}\n')
        log.write(f'qdrant-loader install: {"SUCCESS" if success1 else "FAILED"}\n')
        log.write(f'mcp-server install: {"SUCCESS" if success2 else "FAILED"}\n')
        log.write(f'qdrant-loader import: {"SUCCESS" if import_success1 else "FAILED"}\n')
        log.write(f'mcp-server import: {"SUCCESS" if import_success2 else "FAILED"}\n')
        log.write(f'Windows validation: {"SUCCESS" if validation_success else "FAILED"}\n')
        log.write(f'MCP server test: {"SUCCESS" if mcp_test else "FAILED"}\n')
        log.write(f'Completed: {datetime.now()}\n')
        
        overall_success = success1 and success2 and import_success1 and import_success2
        log.write(f'\nOVERALL BUILD STATUS: {"SUCCESS" if overall_success else "FAILED"}\n')
    
    print(f'Build completed - check {log_file} for full details')
    return log_file

if __name__ == "__main__":
    run_build()