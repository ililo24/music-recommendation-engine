"""Legacy model I/O helpers.

Removed from ``ml/`` during the Phase 0 refactor because ``ml/`` must be
pure (no file I/O). Preserved here per CONVENTION.md rule 9 until the
storage interface (later phase) replaces them.
"""

import os
import sys
from pathlib import Path

import joblib

# Allow imports when the legacy/ directory is on the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from musicrec.ml.evaluation import ModelEvaluator


def load_model_evaluator(model_path):
    """Load a trained model from disk and wrap it in a ModelEvaluator."""
    model = joblib.load(model_path)

    # Extract model name from path
    model_name = Path(model_path).stem

    return ModelEvaluator(model, model_name)
