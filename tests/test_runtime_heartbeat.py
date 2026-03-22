from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.lib.runtime_heartbeat import RuntimeHeartbeatStore, classify_cron_event


class RuntimeHeartbeatTests(unittest.TestCase):
    def test_successful_cron_run_records_next_due(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            store = RuntimeHeartbeatStore(Path(tmp) / "heartbeats", Path(tmp) / "locks")

            store.mark_start(repo, "cron")
            payload = store.mark_success(repo, "cron", duration_seconds=2.5, summary="ok")

            cron = payload["events"]["cron"]
            self.assertEqual(cron["status"], "ok")
            self.assertIsNotNone(cron["next_due_at"])
            self.assertEqual(classify_cron_event(payload), "healthy")

    def test_failure_records_backoff(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            store = RuntimeHeartbeatStore(Path(tmp) / "heartbeats", Path(tmp) / "locks")

            payload = store.mark_failure(repo, "cron", "RuntimeError", "boom", duration_seconds=1.0)

            cron = payload["events"]["cron"]
            self.assertEqual(cron["status"], "failed")
            self.assertEqual(cron["consecutive_failures"], 1)
            self.assertEqual(cron["backoff_minutes"], 15)
            self.assertEqual(classify_cron_event(payload), "backoff")

    def test_lock_prevents_parallel_runs(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            store = RuntimeHeartbeatStore(Path(tmp) / "heartbeats", Path(tmp) / "locks")

            acquired, _ = store.acquire_lock(repo, "cron")
            self.assertTrue(acquired)
            acquired_again, payload = store.acquire_lock(repo, "cron")
            self.assertFalse(acquired_again)
            self.assertEqual(payload["event"], "cron")
