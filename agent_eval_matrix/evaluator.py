"""
Deterministic Agent Trajectory Evaluation Engine.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class TrajectoryStep:
    turn: int
    action: str  # e.g., "THINK", "TOOL_CALL", "RESPONSE"
    tool_name: Optional[str] = None
    args: Dict[str, Any] = field(default_factory=dict)
    tokens_used: int = 0


@dataclass
class EvaluationResult:
    scenario_id: str
    passed: bool
    score: float  # 0.0 to 100.0
    violations: List[str]
    total_turns: int
    total_tokens: int


class MatrixEvaluator:
    def __init__(self, scenario_spec: Dict[str, Any]):
        """
        scenario_spec structure:
        {
          "id": "scenario-01",
          "name": "Database Schema Migration",
          "constraints": {
             "max_turns": 5,
             "required_tools": ["db_check_connection", "apply_migration"],
             "forbidden_tools": ["drop_database", "raw_exec"],
             "tool_order": ["db_check_connection", "apply_migration"]
          }
        }
        """
        self.spec = scenario_spec
        self.constraints = scenario_spec.get("constraints", {})

    def evaluate_trajectory(self, steps: List[TrajectoryStep]) -> EvaluationResult:
        violations: List[str] = []
        score = 100.0

        max_turns = self.constraints.get("max_turns")
        if max_turns is not None and len(steps) > max_turns:
            excess = len(steps) - max_turns
            violations.append(f"Turn count exceeded max limit of {max_turns} (took {len(steps)} steps)")
            score -= min(30.0, excess * 10.0)

        # Tool calls tracking
        invoked_tools = [s.tool_name for s in steps if s.action == "TOOL_CALL" and s.tool_name]

        # Check required tools
        required_tools = self.constraints.get("required_tools", [])
        for req in required_tools:
            if req not in invoked_tools:
                violations.append(f"Missing mandatory tool call: '{req}'")
                score -= 30.0

        # Check forbidden tools
        forbidden_tools = self.constraints.get("forbidden_tools", [])
        for forb in forbidden_tools:
            if forb in invoked_tools:
                violations.append(f"Security violation: invoked forbidden tool '{forb}'")
                score = 0.0

        # Check tool ordering
        tool_order = self.constraints.get("tool_order", [])
        if tool_order:
            order_idx = 0
            for tool in invoked_tools:
                if order_idx < len(tool_order) and tool == tool_order[order_idx]:
                    order_idx += 1
            if order_idx < len(tool_order):
                violations.append(f"Tools executed out of required sequence: expected order {tool_order}")
                score -= 25.0

        final_score = max(0.0, round(score, 1))
        passed = (len(violations) == 0 and final_score >= 80.0)

        total_tokens = sum(s.tokens_used for s in steps)

        return EvaluationResult(
            scenario_id=self.spec.get("id", "unknown"),
            passed=passed,
            score=final_score,
            violations=violations,
            total_turns=len(steps),
            total_tokens=total_tokens
        )
