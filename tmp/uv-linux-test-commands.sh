#!/bin/bash
# UV Migration - Linux Compatibility Test Script
# Run this in WSL to verify UV works on Linux

echo "=== UV Linux Compatibility Test ==="
echo "Date: $(date)"
echo "System: $(uname -a)"
echo ""

# 1. Install UV if not present
echo "1. Installing UV..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi
uv --version

# 2. Clone and setup
echo -e "\n2. Setting up test environment..."
cd /tmp
rm -rf qdrant-loader-test
git clone /mnt/c/dev/qdrant-loader qdrant-loader-test
cd qdrant-loader-test

# 3. Test UV commands
echo -e "\n3. Testing UV sync..."
uv sync --all-extras --all-packages

echo -e "\n4. Testing UV lock..."
uv lock --check

echo -e "\n5. Testing package imports..."
uv run python -c "import qdrant_loader; print(f'qdrant-loader: {qdrant_loader.__version__}')"
uv run python -c "import qdrant_loader_mcp_server; print('mcp-server: OK')"

echo -e "\n6. Testing CLI entry points..."
uv run qdrant-loader --version
uv run mcp-qdrant-loader --version

echo -e "\n7. Running quick unit tests..."
cd packages/qdrant-loader
uv run pytest tests/unit/cli/test_cli.py -v --tb=short -k "test_get_version"

echo -e "\n8. Testing build..."
uv run python -m build --version

echo -e "\n=== Summary ==="
echo "If all above commands succeeded, UV migration is Linux-compatible!"
echo "Any errors above indicate Linux-specific issues that need fixing."