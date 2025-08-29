#!/usr/bin/env python
"""Test Settings model loading to debug configuration issue."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path("packages/qdrant-loader/src")))

import yaml
import json
from qdrant_loader.config import Settings

def test_settings_load():
    """Test loading configuration into Settings model."""
    config_path = Path("test-workspace/config.yaml")
    
    print(f"Testing Settings loading from: {config_path}")
    print("-" * 50)
    
    # Parse YAML
    with open(config_path) as f:
        config_data = yaml.safe_load(f)
    
    print("Config data keys:", list(config_data.keys()))
    print("Global config keys:", list(config_data.get("global_config", {}).keys()))
    
    # Check if qdrant exists
    qdrant_config = config_data.get("global_config", {}).get("qdrant")
    print(f"Qdrant config exists: {qdrant_config is not None}")
    print(f"Qdrant config: {qdrant_config}")
    print("-" * 50)
    
    # Try to create Settings directly
    try:
        print("Attempting to create Settings with parsed data...")
        settings = Settings(**config_data)
        print("SUCCESS: Settings created!")
        print(f"Settings.global_config.qdrant: {settings.global_config.qdrant}")
    except Exception as e:
        print(f"ERROR creating Settings: {e}")
        print(f"Error type: {type(e)}")
    
    print("-" * 50)
    
    # Try with the load_from_file method
    try:
        print("Attempting Settings.load_from_file...")
        # Set environment for config path
        os.environ["QDRANT_LOADER_CONFIG"] = str(config_path)
        settings = Settings.load_from_file(
            config_path=config_path,
            env_path=Path("test-workspace/.env")
        )
        print("SUCCESS: Settings loaded from file!")
        print(f"Settings.global_config.qdrant: {settings.global_config.qdrant}")
    except Exception as e:
        print(f"ERROR loading from file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_settings_load()