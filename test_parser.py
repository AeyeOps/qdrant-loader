#!/usr/bin/env python
"""Test the parser issue with global vs global_config."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path("packages/qdrant-loader/src")))

import yaml
from qdrant_loader.config.validator import ConfigValidator
from qdrant_loader.config.parser import MultiProjectConfigParser

def test_parser():
    """Test the MultiProjectConfigParser."""
    config_path = Path("test-workspace/config.yaml")
    
    print(f"Testing parser with: {config_path}")
    print("-" * 50)
    
    # Parse YAML
    with open(config_path) as f:
        config_data = yaml.safe_load(f)
    
    print("Config keys:", list(config_data.keys()))
    
    # Test what parser is looking for
    print(f"config_data.get('global'): {config_data.get('global')}")
    print(f"config_data.get('global_config'): {config_data.get('global_config')}")
    print("-" * 50)
    
    # Try parsing
    try:
        validator = ConfigValidator()
        parser = MultiProjectConfigParser(validator)
        parsed = parser.parse(config_data, skip_validation=True)
        print("Parsing succeeded!")
        print(f"Global config qdrant: {parsed.global_config.qdrant}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parser()