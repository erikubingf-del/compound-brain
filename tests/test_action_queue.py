import unittest

from scripts.lib.action_queue import rank_actions


class ActionQueueTests(unittest.TestCase):
    def test_rank_actions_prefers_high_alignment_and_confidence(self) -> None:
        ranked = rank_actions(
            [
                {
                    "title": "rewrite docs",
                    "goal_alignment": 4,
                    "probability": 0.9,
                    "urgency": 3,
                    "cost": 2,
                },
                {
                    "title": "add gated activation",
                    "goal_alignment": 9,
                    "probability": 0.8,
                    "urgency": 8,
                    "cost": 3,
                },
            ]
        )

        self.assertEqual(ranked[0]["title"], "add gated activation")
