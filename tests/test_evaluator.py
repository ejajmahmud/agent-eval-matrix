import unittest
from agent_eval_matrix.evaluator import MatrixEvaluator, TrajectoryStep


class TestMatrixEvaluator(unittest.TestCase):
    def setUp(self):
        self.spec = {
            "id": "code-review-01",
            "constraints": {
                "max_turns": 3,
                "required_tools": ["git_diff", "run_linter"],
                "forbidden_tools": ["git_push_force"],
                "tool_order": ["git_diff", "run_linter"]
            }
        }

    def test_successful_trajectory(self):
        steps = [
            TrajectoryStep(turn=1, action="TOOL_CALL", tool_name="git_diff"),
            TrajectoryStep(turn=2, action="TOOL_CALL", tool_name="run_linter"),
            TrajectoryStep(turn=3, action="RESPONSE", args={"msg": "Looks good"})
        ]
        evaluator = MatrixEvaluator(self.spec)
        res = evaluator.evaluate_trajectory(steps)
        self.assertTrue(res.passed)
        self.assertEqual(res.score, 100.0)

    def test_forbidden_tool_violation(self):
        steps = [
            TrajectoryStep(turn=1, action="TOOL_CALL", tool_name="git_diff"),
            TrajectoryStep(turn=2, action="TOOL_CALL", tool_name="git_push_force")
        ]
        evaluator = MatrixEvaluator(self.spec)
        res = evaluator.evaluate_trajectory(steps)
        self.assertFalse(res.passed)
        self.assertEqual(res.score, 0.0)
        self.assertTrue(any("forbidden tool" in v for v in res.violations))


if __name__ == "__main__":
    unittest.main()
