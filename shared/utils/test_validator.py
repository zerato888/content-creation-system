"""Run with: python3 shared/utils/test_validator.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validator import demo

if __name__ == "__main__":
    demo()
