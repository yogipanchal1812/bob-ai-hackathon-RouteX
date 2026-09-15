"""
conftest.py — pytest configuration for Module 4.

Adds src/optimization to the Python path so that all test imports work
without requiring an installed package.
"""

import sys
import os

# Add the parent of 'optimization' (i.e., src/) to sys.path
# so that 'from optimization.xxx import yyy' works in tests.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
