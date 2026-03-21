import unittest

from scripts.lib.audit_packet import build_audit_packet


class AuditPacketTests(unittest.TestCase):
    def test_build_audit_packet_infers_departments(self) -> None:
        packet = build_audit_packet(
            repo_name="demo",
            tech_stack=["Python", "Docker"],
            docs_present=True,
            ci_present=True,
        )

        self.assertIn("architecture", packet["departments"])
        self.assertIn("engineering", packet["departments"])
        self.assertIn("project_goal_candidates", packet)
