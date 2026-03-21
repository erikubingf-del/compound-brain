import unittest

from scripts.architecture_radar import rank_findings


class ArchitectureRadarTests(unittest.TestCase):
    def test_rank_findings_prefers_goal_useful_patterns(self) -> None:
        ranked = rank_findings(
            [
                {
                    "title": "flashy demo",
                    "goal_fit": 2,
                    "architecture_fit": 3,
                    "confidence": 0.4,
                },
                {
                    "title": "gated planner loop",
                    "goal_fit": 9,
                    "architecture_fit": 8,
                    "confidence": 0.8,
                },
            ]
        )

        self.assertEqual(ranked[0]["title"], "gated planner loop")
