#!/usr/bin/env python
"""
Enhanced Windows-compatible wrapper for qdrant-loader-mcp-server
Fixes multiple Windows compatibility issues:
1. Signal handler registration (NotImplementedError)
2. Pipe transport issues (_ProactorReadPipeTransport)
3. Stdin handling with binary mode
4. Event loop policy selection
5. Graceful shutdown handling
"""
import sys
import os
import asyncio
import signal
import json
import threading
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any

# Force Windows to use SelectorEventLoop instead of ProactorEventLoop
# This fixes stdin pipe handling issues
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Global shutdown event
shutdown_event = threading.Event()

def setup_signal_handlers():
    """Set up Windows-compatible signal handlers"""
    def signal_handler(signum, frame):
        shutdown_event.set()
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)

def patch_asyncio_signal_handlers():
    """Monkey-patch asyncio signal handlers for Windows compatibility only"""
    if sys.platform != 'win32':
        # Don't patch on non-Windows platforms
        return
        
    original_add_signal_handler = asyncio.AbstractEventLoop.add_signal_handler
    
    def patched_add_signal_handler(self, sig, callback, *args):
        """Skip signal handler registration on Windows - use threading instead"""
        # Only apply this patch on Windows
        if sys.platform == 'win32':
            # Don't register with asyncio, use threading-based handlers
            return
        # On non-Windows, use original implementation (this shouldn't be reached)
        return original_add_signal_handler(self, sig, callback, *args)
    
    asyncio.AbstractEventLoop.add_signal_handler = patched_add_signal_handler

def create_windows_stdin_reader():
    """Create a Windows-compatible stdin reader"""
    executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="stdin_reader")
    
    async def read_stdin_windows():
        """Windows-compatible stdin reader using SelectorEventLoop"""
        loop = asyncio.get_running_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        
        try:
            # Use the selector event loop's stdin handling
            transport, _ = await loop.connect_read_pipe(lambda: protocol, sys.stdin)
            return reader
        except Exception as e:
            # Fallback to thread-based reading if pipe connection fails
            print(f"Pipe connection failed, using thread fallback: {e}", file=sys.stderr)
            return await fallback_stdin_reader(loop, executor)
    
    async def fallback_stdin_reader(loop, executor):
        """Thread-based fallback stdin reader"""
        reader = asyncio.StreamReader()
        
        def read_stdin_blocking():
            """Read from stdin in blocking mode"""
            try:
                return sys.stdin.buffer.readline()
            except Exception as e:
                print(f"Stdin read error: {e}", file=sys.stderr)
                return b""
        
        async def feed_reader():
            """Feed data to the StreamReader from thread"""
            while not shutdown_event.is_set():
                try:
                    line = await loop.run_in_executor(executor, read_stdin_blocking)
                    if not line:
                        reader.feed_eof()
                        break
                    reader.feed_data(line)
                    
                    # Check for shutdown after each line
                    if shutdown_event.is_set():
                        break
                        
                except Exception as e:
                    print(f"Reader feed error: {e}", file=sys.stderr)
                    reader.set_exception(e)
                    break
        
        # Start feeding data
        asyncio.create_task(feed_reader())
        return reader
    
    return read_stdin_windows

def patch_mcp_server():
    """Apply Windows-specific patches to the MCP server only when needed"""
    # Only patch on Windows
    if sys.platform != 'win32':
        return True  # No patches needed on non-Windows
        
    try:
        import qdrant_loader_mcp_server.cli as cli_module
        
        # Replace the problematic read_stdin function only on Windows
        original_read_stdin = cli_module.read_stdin
        cli_module.read_stdin = create_windows_stdin_reader()
        
        # Patch the CLI shutdown handling only on Windows
        original_shutdown = cli_module.shutdown
        
        async def patched_shutdown(loop, shutdown_event_param=None):
            """Enhanced shutdown that works with threading signals"""
            # Set both the asyncio event and threading event
            if shutdown_event_param:
                shutdown_event_param.set()
            shutdown_event.set()
            
            # Call original shutdown
            if original_shutdown:
                try:
                    await original_shutdown(loop, shutdown_event_param)
                except Exception as e:
                    print(f"Shutdown error: {e}", file=sys.stderr)
        
        cli_module.shutdown = patched_shutdown
        
        print("Windows patches applied successfully", file=sys.stderr)
        return True
        
    except ImportError as e:
        print(f"Failed to import MCP server: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Failed to patch MCP server: {e}", file=sys.stderr)
        return False

def check_environment():
    """Check and validate required environment variables and Python version"""
    # Check Python version compatibility
    python_version = sys.version_info
    if python_version < (3, 12):
        print(f"ERROR: Python {python_version.major}.{python_version.minor} not supported. Requires Python 3.12 or 3.13.", file=sys.stderr)
        return False
    elif python_version >= (3, 14):
        print(f"WARNING: Python {python_version.major}.{python_version.minor} not tested. Supported versions: 3.12, 3.13.", file=sys.stderr)
    
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API key for embeddings',
        'QDRANT_URL': 'Qdrant server URL', 
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  {var}: {description}")
    
    if missing_vars:
        print("ERROR: Missing required environment variables:", file=sys.stderr)
        for var in missing_vars:
            print(var, file=sys.stderr)
        print("\nPlease set these environment variables and try again.", file=sys.stderr)
        return False
    
    # Set defaults for optional variables
    if not os.getenv('QDRANT_COLLECTION_NAME'):
        os.environ['QDRANT_COLLECTION_NAME'] = 'documents'
        print(f"Using default collection name: documents", file=sys.stderr)
    
    return True

def setup_windows_stdio():
    """Set up stdio for Windows binary mode"""
    if sys.platform != 'win32':
        return  # Only apply on Windows
        
    try:
        import msvcrt
        # Set stdin to binary mode for JSON-RPC communication
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        print("Windows stdio configured", file=sys.stderr)
    except Exception as e:
        print(f"Failed to setup Windows stdio: {e}", file=sys.stderr)

def main():
    """Main entry point with Windows compatibility from existing wrapper"""
    # Only apply Windows-specific setup on Windows
    if sys.platform == 'win32':
        print("Starting Qdrant Loader MCP Server (Windows Edition)", file=sys.stderr)
        
        # Check environment first
        if not check_environment():
            sys.exit(1)
        
        # Set up Windows-specific configurations
        setup_signal_handlers()
        patch_asyncio_signal_handlers()
        setup_windows_stdio()
        
        # Apply MCP server patches
        if not patch_mcp_server():
            print("Failed to apply Windows patches", file=sys.stderr)
            sys.exit(1)
    else:
        # On non-Windows, minimal setup
        if not check_environment():
            sys.exit(1)
    
    # Import and run the MCP server (works on all platforms)
    try:
        from qdrant_loader_mcp_server.cli import cli
        if sys.platform == 'win32':
            print("Starting MCP server...", file=sys.stderr)
        cli()
        
    except KeyboardInterrupt:
        if sys.platform == 'win32':
            print("Interrupted by user", file=sys.stderr)
        sys.exit(0)
    except ImportError as e:
        print(f"Import error: {e}", file=sys.stderr)
        print("Make sure qdrant-loader-mcp-server is installed", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if sys.platform == 'win32':
            shutdown_event.set()
            print("Server shutdown complete", file=sys.stderr)

if __name__ == "__main__":
    main()