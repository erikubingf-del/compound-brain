from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.activation_registry import ActivationRegistry


class ActivationRegistryTests(unittest.TestCase):
    def test_register_repo_records_alive_state(self) -> None:
        with TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "activated-projects.json"
            registry = ActivationRegistry(registry_path)

            record = registry.register_repo(
                repo_path="/tmp/demo",
                repo_name="demo",
                stack=["Python"],
                activation_mode="manual",
            )

            self.assertEqual(record["status"], "registered")
            stored = json.loads(registry_path.read_text())
            self.assertEqual(stored["projects"][0]["repo_name"], "demo")
