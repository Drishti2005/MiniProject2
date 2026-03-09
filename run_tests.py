#!/usr/bin/env python
"""
Test runner script for backend tests
Handles import paths correctly
"""

import sys
import os
import subprocess

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Run pytest with proper configuration
result = subprocess.run(
    [
        sys.executable, "-m", "pytest",
        "backend/tests/",
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ],
    cwd=project_root
)

sys.exit(result.returncode)
