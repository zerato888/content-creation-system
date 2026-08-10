"""Run with: python3 shared/memory-system/test_framework.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from framework import demo

if __name__ == "__main__":
    demo()
