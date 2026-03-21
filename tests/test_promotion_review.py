from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.promotion_inbox import PromotionInbox
from scripts.lib.promotion_review import review_pending_candidates


class PromotionReviewTests(unittest.TestCase):
    def test_review_pending_candidates_writes_review_note_and_updates_status(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "promotions"
            inbox = PromotionInbox(root)
            record = inbox.submit_candidate(
                source_repo="demo",
                title="Approval-gated refactoring",
                summary="Reusable approval pattern",
                target_kind="skills",
            )

            result = review_pending_candidates(root)

            self.assertEqual(result["reviewed_count"], 1)
            updated = json.loads((root / f"{record['id']}.json").read_text())
            self.assertEqual(updated["status"], "review-generated")
            self.assertTrue(any(path.name.endswith(".md") for path in (root / "reviews").glob("*.md")))

