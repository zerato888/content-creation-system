"""Run with: python3 shared/utils/test_key_manager.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from key_manager import demo

if __name__ == "__main__":
    demo()
