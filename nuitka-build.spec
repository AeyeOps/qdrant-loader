# Nuitka Build Specification for qdrant-loader
# Optimized for Windows standalone executable

[build]
# Target executable name
output = "qdrant-loader.exe"
output_mcp = "mcp-qdrant-loader.exe"

# Python version requirement
python_version = ">=3.12,<3.13"

# Compilation mode
mode = "standalone"
onefile = true
windows_console = true

# Performance optimizations
lto = true  # Link Time Optimization
clang = true  # Use Clang if available (faster)
remove_output = true  # Clean build artifacts
show_progress = true
show_memory = true

# Module configurations
follow_imports = true
follow_stdlib = false  # Don't include unused stdlib
assume_yes_for_downloads = true

# Required packages to include
include_packages = [
    "qdrant_loader",
    "qdrant_loader_mcp_server",
    "openai",
    "qdrant_client",
    "tiktoken",
    "tiktoken_ext",
    "tiktoken_ext.openai_public",
    "langchain",
    "langchain_core",
    "langchain_community",
    "pydantic",
    "structlog",
    "yaml",
    "dotenv",
    "click",
    "httpx",
    "certifi",
    "markitdown",
    "spacy",
    "nltk",
    "numpy",
    "fastapi",
    "uvicorn",
    "starlette",
    "json_rpc",
]

# Data files to include
include_data_files = [
    "packages/qdrant-loader/conf=conf",
    "packages/qdrant-loader/src/qdrant_loader=qdrant_loader",
    "packages/qdrant-loader-mcp-server/src/qdrant_loader_mcp_server=qdrant_loader_mcp_server",
]

# DLLs and binaries to include
include_dlls = [
    "libssl*",
    "libcrypto*",
]

# Plugins required
plugins = [
    "numpy",
    "multiprocessing",
    "pkg_resources",
]

# Exclude unnecessary modules (reduce size)
exclude_modules = [
    "tkinter",
    "test",
    "unittest",
    "pygame",
    "PIL",
    "matplotlib",
    "IPython",
    "jupyter",
    "_pytest",
    "pytest",
]

# Windows-specific settings
windows_icon = ""  # Add path to .ico if available
windows_company = "AeyeOps"
windows_product = "Qdrant Loader"
windows_version = "0.6.2"
windows_copyright = "Copyright 2024 AeyeOps"

# Environment variables to embed
embed_environment = {
    "PYTHONPATH": ".",
    "SSL_CERT_FILE": "certifi/cacert.pem",
}

# Build commands
[commands]
loader = "nuitka --standalone --onefile --windows-console-mode=force --output-filename=qdrant-loader.exe --include-package=qdrant_loader --include-package-data=qdrant_loader packages/qdrant-loader/src/qdrant_loader/main.py"

mcp = "nuitka --standalone --onefile --windows-console-mode=force --output-filename=mcp-qdrant-loader.exe --include-package=qdrant_loader_mcp_server --include-package-data=qdrant_loader_mcp_server packages/qdrant-loader-mcp-server/src/qdrant_loader_mcp_server/__main__.py"

# Optimization flags
[optimization]
optimization_level = 2  # O2 optimization
unstripped = false  # Strip debug symbols
experimental = ["use_pefile_recurse", "use_pefile_fullrecurse"]