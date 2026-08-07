"""Tests for alfr3d setup wizard persistence and readiness."""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from cli.cli import main
from cli.commands import setup as setup_mod
from cli.setup_state import has_model_credentials, is_setup_complete


class TestSetupState(unittest.TestCase):
    def test_setup_complete_requires_marker_and_key(self):
        self.assertFalse(is_setup_complete({}))
        self.assertFalse(is_setup_complete({"open_ai_api_key": "sk-test"}))
        self.assertTrue(
            is_setup_complete({
                "open_ai_api_key": "sk-test",
                "setup_completed_at": "2026-01-01T00:00:00Z",
            })
        )

    def test_placeholder_keys_rejected(self):
        self.assertFalse(has_model_credentials({"open_ai_api_key": "YOUR API KEY"}))
        self.assertTrue(has_model_credentials({"deepseek_api_key": "sk-live-abc"}))


class TestSetupPersistence(unittest.TestCase):
    def test_writes_user_and_business_profiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = {
                "name": "Ada Example",
                "preferred_name": "Ada",
                "occupation": "Founder",
                "email": "ada@example.com",
                "timezone": "America/Chicago",
                "business_status": "planning",
                "business_intent": "launch",
                "business_name": "Example Co",
                "industry": "bookkeeping",
                "primary_focus": ["formation", "money"],
                "goals": "Form the LLC and open a business bank account.",
                "why_alfr3d": "I want a calm steward while I start.",
                "stage_notes": "Side project evenings only.",
                "setup_completed_at": "2026-08-07T12:00:00Z",
            }
            setup_mod._write_user_md(tmp, profile)
            setup_mod._write_business_md(tmp, profile)
            setup_mod._seed_memory(tmp, profile)

            user = open(os.path.join(tmp, "USER.md"), encoding="utf-8").read()
            business = open(os.path.join(tmp, "BUSINESS.md"), encoding="utf-8").read()
            memory = open(os.path.join(tmp, "MEMORY.md"), encoding="utf-8").read()

            self.assertIn("Ada Example", user)
            self.assertIn("Ada", user)
            self.assertIn("Have they started a business?", business)
            self.assertIn("planning", business.lower())
            self.assertIn("Launch the business", business)
            self.assertIn("Example Co", business)
            self.assertIn("bookkeeping", business)
            self.assertIn("BUSINESS.md", memory)

    def test_save_config_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "config.json")
            with patch("cli.commands.setup.config_path", return_value=path):
                cfg = {"agent": True, "model": "gpt-4o"}
                setup_mod._save_config(cfg)
                loaded = json.load(open(path, encoding="utf-8"))
            self.assertEqual(loaded["model"], "gpt-4o")

    def test_help_lists_setup(self):
        runner = CliRunner()
        result = runner.invoke(main, ["help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("setup", result.output.lower())
        self.assertIn("api key", result.output.lower() + "api keys")


class TestBusinessLoadedInWorkspace(unittest.TestCase):
    def test_business_in_default_context_files(self):
        from agent.prompt.workspace import (
            DEFAULT_BUSINESS_FILENAME,
            load_context_files,
        )

        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, DEFAULT_BUSINESS_FILENAME), "w", encoding="utf-8") as f:
                f.write("# BUSINESS.md\n\n- **Industry**: HVAC\n")
            files = load_context_files(tmp)
            names = [f.path for f in files]
            self.assertIn(DEFAULT_BUSINESS_FILENAME, names)
            business = next(f for f in files if f.path == DEFAULT_BUSINESS_FILENAME)
            self.assertIn("HVAC", business.content)


if __name__ == "__main__":
    unittest.main()
