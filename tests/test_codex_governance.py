from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.setup_codex_governance import install, GLOBAL_BEGIN, BOARD_BEGIN
from scripts.materialize_project_claude import materialize_codex_project_brain_skill


SOURCE = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "project-brain" / "SKILL.md"
BOARD = "https://chatgpt.com/space/page_0123456789abcdef0123456789abcdef"


class CodexGovernanceTests(unittest.TestCase):
    def test_local_setup_preserves_personal_rules_and_is_idempotent(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex = root / ".codex"
            skills = root / ".agents" / "skills"
            codex.mkdir()
            (codex / "AGENTS.md").write_text("# My existing instructions\nKeep the goal.\n")
            (codex / "global-agent-governance.md").write_text("# My private notes\nRetain this.\n")

            first = install(source_skill=SOURCE, codex_home=codex, skills_home=skills, board_url=BOARD)
            self.assertEqual(first["global_instructions"], "configured")
            self.assertEqual(first["project_brain_skill"], "configured")
            self.assertEqual(first["private_board_pointer"], "configured")

            agents = (codex / "AGENTS.md").read_text()
            pointer = (codex / "global-agent-governance.md").read_text()
            skill = (skills / "project-brain" / "SKILL.md").read_text()
            self.assertIn("Keep the goal.", agents)
            self.assertEqual(agents.count(GLOBAL_BEGIN), 1)
            self.assertIn("Retain this.", pointer)
            self.assertIn(BOARD, pointer)
            self.assertEqual(pointer.count(BOARD_BEGIN), 1)
            self.assertIn("name: project-brain", skill)
            self.assertNotIn(BOARD, agents)
            self.assertNotIn(BOARD, skill)
            self.assertEqual((codex / "global-agent-governance.md").stat().st_mode & 0o777, 0o600)

            second = install(source_skill=SOURCE, codex_home=codex, skills_home=skills, board_url=BOARD)
            self.assertEqual(second["global_instructions"], "configured")
            self.assertEqual((codex / "AGENTS.md").read_text(), agents)
            self.assertEqual((codex / "global-agent-governance.md").read_text(), pointer)

    def test_check_only_does_not_create_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex = root / ".codex"
            skills = root / ".agents" / "skills"
            status = install(
                source_skill=SOURCE, codex_home=codex, skills_home=skills,
                board_url=BOARD, check_only=True,
            )
            self.assertEqual(status["global_instructions"], "missing")
            self.assertEqual(status["private_board_pointer"], "not-configured")
            self.assertFalse(codex.exists())
            self.assertFalse(skills.exists())

    def test_preserves_existing_unmanaged_skill(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex = root / ".codex"
            skills = root / ".agents" / "skills"
            skill_path = skills / "project-brain" / "SKILL.md"
            skill_path.parent.mkdir(parents=True)
            skill_path.write_text("---\nname: project-brain\ndescription: Custom\n---\nKeep custom.\n")

            status = install(source_skill=SOURCE, codex_home=codex, skills_home=skills)
            self.assertEqual(status["project_brain_skill"], "preserved-custom")
            self.assertIn("Keep custom.", skill_path.read_text())

    def test_rejects_untrusted_board_url(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                install(
                    source_skill=SOURCE, codex_home=root / ".codex",
                    skills_home=root / ".agents" / "skills",
                    board_url="https://example.com/private-token",
                )
            self.assertFalse((root / ".codex").exists())

    def test_prepared_project_gets_portable_skill_without_overwriting_custom(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertTrue(materialize_codex_project_brain_skill(repo))
            target = repo / ".agents" / "skills" / "project-brain" / "SKILL.md"
            self.assertIn("name: project-brain", target.read_text())
            target.write_text("---\nname: project-brain\ndescription: custom\n---\nCustom rule.\n")
            self.assertFalse(materialize_codex_project_brain_skill(repo))
            self.assertIn("Custom rule.", target.read_text())

    def test_repo_root_adapter_points_to_portable_skill(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        self.assertTrue((repo / "AGENTS.md").exists())
        self.assertTrue(SOURCE.exists())
        self.assertIn(".agents/skills/project-brain/SKILL.md", (repo / "AGENTS.md").read_text())
