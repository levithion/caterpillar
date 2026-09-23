#!/usr/bin/env python3
"""Train ML models from sensor CSV history."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.ml.train import train_all

if __name__ == "__main__":
    meta = train_all(force="--force" in sys.argv)
    print("Training complete:")
    for k, v in meta.items():
        print(f"  {k}: {v}")
