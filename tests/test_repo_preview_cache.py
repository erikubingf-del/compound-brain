from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.lib.repo_preview_cache import RepoPreviewCache


class RepoPreviewCacheTests(unittest.TestCase):
    def test_upsert_preview_stores_goal_departments_and_commit(self) -> None:
        with TemporaryDirectory() as tmp:
            cache = RepoPreviewCache(Path(tmp) / "repo-previews.json")

            preview = cache.upsert_preview(
                repo_path="/tmp/demo",
                repo_name="demo",
                inferred_goal="Ship demo",
                departments=["engineering", "research"],
                risks=["Missing tests"],
                next_actions=["Prepare brain"],
                confidence=0.78,
                last_commit="abc123",
            )

            self.assertEqual(preview["repo_name"], "demo")
            self.assertEqual(preview["departments"], ["engineering", "research"])
            self.assertEqual(preview["last_commit"], "abc123")

