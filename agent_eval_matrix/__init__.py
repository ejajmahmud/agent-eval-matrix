"""
Agent Eval Matrix
Deterministic multi-turn agent evaluation framework.
"""

from .evaluator import MatrixEvaluator, EvaluationResult, TrajectoryStep

__version__ = "0.1.0"
__all__ = ["MatrixEvaluator", "EvaluationResult", "TrajectoryStep"]
