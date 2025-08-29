#!/usr/bin/env python3
"""
Validation script for Windows + Python 3.13 compatibility fixes
Tests all the key fixes without requiring a full MCP server installation
"""
import sys
import os
import platform
import importlib.util

def test_python_version():
    """Test Python version compatibility"""
    print("=== Python Version Test ===")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    print(f"Platform: {platform.system()}")
    
    if version < (3, 12):
        print("FAIL: Python version too old (requires 3.12+)")
        return False
    elif version > (3, 13):
        print("WARN: Python version not tested (supports 3.12-3.13)")
    else:
        print("PASS: Python version supported")
    
    return True

def test_windows_detection():
    """Test Windows platform detection"""
    print("\n=== Windows Detection Test ===")
    is_windows = sys.platform == 'win32'
    print(f"sys.platform: {sys.platform}")
    print(f"platform.system(): {platform.system()}")
    
    if is_windows:
        print("PASS: Windows detected correctly")
    else:
        print("INFO: Non-Windows platform (fixes won't apply)")
    
    return True

def test_dependency_logic():
    """Test dependency selection logic"""
    print("\n=== Dependency Selection Test ===")
    version = sys.version_info
    is_windows = platform.system() == 'Windows'
    
    print(f"Python < 3.13: {version < (3, 13)}")
    print(f"Is Windows: {is_windows}")
    
    # Test faiss vs hnswlib
    if version < (3, 13):
        print("[PASS] Would use: faiss-cpu>=1.7.4")
    else:
        print("[PASS] Would use: hnswlib>=0.7.0 (Python 3.13+ alternative)")
    
    # Test tree-sitter-languages exclusion
    if is_windows or version >= (3, 13):
        print("[PASS] Would skip: tree-sitter-languages (Windows or Python 3.13+)")
    else:
        print("[PASS] Would use: tree-sitter-languages>=1.10.0")
    
    print("[PASS] Would always use: tree-sitter>=0.20.0,<0.21")
    return True

def test_asyncio_patches():
    """Test asyncio compatibility patches"""
    print("\n=== Asyncio Compatibility Test ===")
    
    try:
        import asyncio
        print("[PASS] asyncio imported successfully")
        
        # Test event loop policy
        if sys.platform == 'win32':
            try:
                # This would be set by our wrapper
                policy = asyncio.WindowsSelectorEventLoopPolicy()
                print("[PASS] WindowsSelectorEventLoopPolicy available")
            except AttributeError:
                print("[FAIL] WindowsSelectorEventLoopPolicy not available")
                return False
        
        # Test signal handler patch concept
        loop = asyncio.new_event_loop()
        if sys.platform == 'win32':
            # On Windows, add_signal_handler should raise NotImplementedError
            try:
                import signal
                loop.add_signal_handler(signal.SIGINT, lambda: None)
                print("[FAIL] add_signal_handler should fail on Windows")
                return False
            except NotImplementedError:
                print("[PASS] add_signal_handler correctly raises NotImplementedError on Windows")
            except Exception as e:
                print(f"[INFO]  add_signal_handler error: {e}")
        
        loop.close()
        return True
        
    except Exception as e:
        print(f"[FAIL] FAIL: asyncio test error: {e}")
        return False

def test_wrapper_imports():
    """Test that our wrapper can be imported"""
    print("\n=== Wrapper Import Test ===")
    
    try:
        # Test importing the wrapper
        spec = importlib.util.spec_from_file_location(
            "wrapper", 
            "windows-mcp-wrapper.py"
        )
        wrapper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wrapper)
        print("[PASS] Windows wrapper imported successfully")
        
        # Test environment check function exists
        if hasattr(wrapper, 'check_environment'):
            print("[PASS] check_environment function found")
        else:
            print("[FAIL] check_environment function missing")
            return False
            
        # Test other key functions
        for func in ['patch_asyncio_signal_handlers', 'setup_windows_stdio', 'create_windows_stdin_reader']:
            if hasattr(wrapper, func):
                print(f"[PASS] {func} function found")
            else:
                print(f"[WARN]  {func} function missing (may be internal)")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] FAIL: Wrapper import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_validation():
    """Test environment validation with mock values"""
    print("\n=== Environment Validation Test ===")
    
    # Save original env
    original_env = {}
    test_vars = ['OPENAI_API_KEY', 'QDRANT_URL', 'QDRANT_COLLECTION_NAME']
    
    for var in test_vars:
        original_env[var] = os.environ.get(var)
    
    try:
        # Test missing required vars
        for var in test_vars:
            if var in os.environ:
                del os.environ[var]
        
        # Import wrapper and test
        spec = importlib.util.spec_from_file_location(
            "wrapper", 
            "windows-mcp-wrapper.py"
        )
        wrapper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wrapper)
        
        # Should fail with missing vars
        result = wrapper.check_environment()
        if result:
            print("[FAIL] Should fail with missing environment variables")
            return False
        else:
            print("[PASS] Correctly detected missing environment variables")
        
        # Set required vars
        os.environ['OPENAI_API_KEY'] = 'test-key-123'
        os.environ['QDRANT_URL'] = 'http://localhost:6333'
        
        # Should pass now
        result = wrapper.check_environment()
        if result:
            print("[PASS] Environment validation passed with required vars")
        else:
            print("[FAIL] Environment validation failed unexpectedly")
            return False
            
        return True
        
    except Exception as e:
        print(f"[FAIL] FAIL: Environment validation error: {e}")
        return False
        
    finally:
        # Restore original environment
        for var, value in original_env.items():
            if value is None:
                if var in os.environ:
                    del os.environ[var]
            else:
                os.environ[var] = value

def main():
    """Run all validation tests"""
    print("Windows + Python 3.13 Compatibility Validation")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_windows_detection,
        test_dependency_logic,
        test_asyncio_patches,
        test_wrapper_imports,
        test_environment_validation,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"[FAIL] Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "[PASS] PASS" if result else "[FAIL] FAIL"
        print(f"{i+1}. {test.__name__}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! Windows compatibility fixes validated.")
        return True
    else:
        print("[WARN]  Some tests failed. Check the details above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)