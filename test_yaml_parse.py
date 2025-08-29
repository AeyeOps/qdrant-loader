#!/usr/bin/env python
"""Test YAML parsing to debug configuration issue."""

import yaml
import json
from pathlib import Path

def test_yaml_parse():
    """Test parsing the YAML configuration file."""
    config_path = Path("test-workspace/config.yaml")
    
    print(f"Testing YAML file: {config_path}")
    print("-" * 50)
    
    # Read raw file
    with open(config_path) as f:
        raw_content = f.read()
    
    print("Raw file content:")
    print(raw_content)
    print("-" * 50)
    
    # Parse YAML
    with open(config_path) as f:
        parsed = yaml.safe_load(f)
    
    print("Parsed YAML structure:")
    print(json.dumps(parsed, indent=2))
    print("-" * 50)
    
    # Check global_config
    if "global_config" in parsed:
        print("global_config found:")
        print(json.dumps(parsed["global_config"], indent=2))
        
        # Check qdrant
        if "qdrant" in parsed["global_config"]:
            print("\nqdrant configuration found:")
            print(json.dumps(parsed["global_config"]["qdrant"], indent=2))
        else:
            print("\nWARNING: qdrant not found in global_config!")
    else:
        print("WARNING: global_config not found in parsed YAML!")
    
    print("-" * 50)
    
    # Check what happens if qdrant value is None
    qdrant_val = parsed.get("global_config", {}).get("qdrant")
    print(f"Type of qdrant value: {type(qdrant_val)}")
    print(f"qdrant value: {qdrant_val}")
    print(f"qdrant is None: {qdrant_val is None}")
    print(f"qdrant bool: {bool(qdrant_val)}")

if __name__ == "__main__":
    test_yaml_parse()