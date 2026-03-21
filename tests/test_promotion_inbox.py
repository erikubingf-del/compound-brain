from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.lib.promotion_inbox import PromotionInbox


class PromotionInboxTests(unittest.TestCase):
    def test_submit_candidate_writes_global_review_entry(self) -> None:
        with TemporaryDirectory() as tmp:
            inbox = PromotionInbox(Path(tmp) / "promotions")

            record = inbox.submit_candidate(
                source_repo="demo",
                title="Approval-gated refactoring",
                summary="Reusable approval pattern",
                target_kind="skills",
            )

            self.assertEqual(record["status"], "pending-review")

