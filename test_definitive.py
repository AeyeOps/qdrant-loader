#!/usr/bin/env python
"""Definitive test to determine correct YAML structure."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path("packages/qdrant-loader/src")))

import yaml
import json
from qdrant_loader.config import Settings
from qdrant_loader.config.validator import ConfigValidator
from qdrant_loader.config.parser import MultiProjectConfigParser

def test_both_structures():
    """Test both 'global' and 'global_config' to see which works."""
    
    # Test case 1: Using 'global' (what parser expects)
    yaml_with_global = """
global:
  qdrant:
    url: "http://localhost:6333"
    api_key: null
    collection_name: "test_collection"

projects:
  test-project:
    display_name: "Test Project"
    description: "Test"
    sources:
      localfile:
        test:
          base_url: "file:///test"
"""
    
    # Test case 2: Using 'global_config' (what template shows)
    yaml_with_global_config = """
global_config:
  qdrant:
    url: "http://localhost:6333"
    api_key: null
    collection_name: "test_collection"

projects:
  test-project:
    display_name: "Test Project"
    description: "Test"
    sources:
      localfile:
        test:
          base_url: "file:///test"
"""
    
    print("=" * 60)
    print("TESTING YAML STRUCTURE")
    print("=" * 60)
    
    # Test 'global' structure
    print("\n1. Testing with 'global:' key (what parser expects):")
    print("-" * 40)
    try:
        data = yaml.safe_load(yaml_with_global)
        validator = ConfigValidator()
        parser = MultiProjectConfigParser(validator)
        parsed = parser.parse(data, skip_validation=True)
        
        print(f"SUCCESS: Parsing succeeded!")
        print(f"   global_config.qdrant = {parsed.global_config.qdrant}")
        
        # Try creating Settings
        settings = Settings(
            global_config=parsed.global_config,
            projects_config=parsed.projects_config
        )
        print(f"SUCCESS: Settings created successfully!")
        print(f"   URL: {settings.global_config.qdrant.url}")
        
    except Exception as e:
        print(f"FAILED: {e}")
    
    # Test 'global_config' structure
    print("\n2. Testing with 'global_config:' key (what template shows):")
    print("-" * 40)
    try:
        data = yaml.safe_load(yaml_with_global_config)
        validator = ConfigValidator()
        parser = MultiProjectConfigParser(validator)
        parsed = parser.parse(data, skip_validation=True)
        
        print(f"SUCCESS: Parsing succeeded!")
        print(f"   global_config.qdrant = {parsed.global_config.qdrant}")
        
        # Try creating Settings
        settings = Settings(
            global_config=parsed.global_config,
            projects_config=parsed.projects_config
        )
        print(f"SUCCESS: Settings created successfully!")
        print(f"   URL: {settings.global_config.qdrant.url}")
        
    except Exception as e:
        print(f"FAILED: {e}")
    
    print("\n" + "=" * 60)
    print("CONCLUSION:")
    print("=" * 60)
    print("\nThe parser expects YAML key: 'global:'")
    print("The Settings class has Python attribute: 'global_config'")
    print("\nThis means:")
    print("- YAML file should use: global:")
    print("- Python code refers to it as: settings.global_config")
    print("\nThe template and README need to be fixed to use 'global:'")

if __name__ == "__main__":
    test_both_structures()