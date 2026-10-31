# Ensures the service root is on sys.path so `pytest` (not just
# `python -m pytest`) can import the `app` package from a clean checkout.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
