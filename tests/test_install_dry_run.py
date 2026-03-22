import subprocess
import unittest


class InstallDryRunTests(unittest.TestCase):
    def test_install_dry_run_mentions_activation_runtime(self) -> None:
        result = subprocess.run(
            ["bash", "install.sh", "--dry-run"],
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )

        self.assertIn("activate-repo", result.stdout)
        self.assertIn("registry", result.stdout)
        self.assertNotIn("Not found (skipping): nightly_review.sh", result.stdout)
