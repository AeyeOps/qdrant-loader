#!/usr/bin/env python3
"""Simple test script for Nuitka compilation."""

import sys
import os

def main():
    print("Nuitka test executable running!")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Arguments: {sys.argv}")
    return 0

if __name__ == "__main__":
    sys.exit(main())