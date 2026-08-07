"""Tests for customer-facing alfr3d chat CLI routing and preflight."""

import os
import tempfile
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from cli.cli import main, _KNOWN_COMMANDS
from cli.commands import chat as chat_mod


class TestCliChatRouting(unittest.TestCase):
    def test_known_commands_include_chat(self):
        self.assertIn("chat", _KNOWN_COMMANDS)
        self.assertIn("start", _KNOWN_COMMANDS)

    def test_freeform_prompt_routes_to_chat(self):
        runner = CliRunner()
        with patch("cli.commands.chat.run_chat", return_value=0) as run_chat:
            result = runner.invoke(main, ["What", "is", "a", "DUNS", "number?"])
        self.assertEqual(result.exit_code, 0, result.output)
        run_chat.assert_called_once()
        kwargs = run_chat.call_args.kwargs
        # freeform becomes one joined prompt
        self.assertEqual(kwargs.get("prompt") or run_chat.call_args.args[0], "What is a DUNS number?")

    def test_chat_subcommand_one_shot(self):
        runner = CliRunner()
        with patch("cli.commands.chat.run_chat", return_value=0) as run_chat:
            result = runner.invoke(main, ["chat", "Hello", "Alfr3d"])
        self.assertEqual(result.exit_code, 0, result.output)
        run_chat.assert_called_once()
        args, kwargs = run_chat.call_args
        prompt = kwargs.get("prompt")
        if prompt is None and args:
            prompt = args[0]
        self.assertEqual(prompt, "Hello Alfr3d")

    def test_help_lists_chat(self):
        runner = CliRunner()
        result = runner.invoke(main, ["help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("chat", result.output.lower())
        self.assertIn("personal steward", result.output.lower())


class TestChatPreflight(unittest.TestCase):
    def test_missing_credentials_fails_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = os.path.join(tmp, "config.json")
            with open(config_path, "w", encoding="utf-8") as f:
                f.write('{"agent": true, "model": "gpt-4o", "open_ai_api_key": ""}')

            with patch("cli.commands.chat.get_project_root", return_value=tmp), \
                 patch("cli.commands.chat.load_config_json", return_value={
                     "agent": True,
                     "model": "gpt-4o",
                     "open_ai_api_key": "",
                 }):
                # Force config "exists" path without creating from template
                ok = chat_mod._preflight()
            self.assertFalse(ok)

    def test_has_model_credentials_detects_key(self):
        self.assertTrue(chat_mod._has_model_credentials({"open_ai_api_key": "sk-test"}))
        self.assertFalse(chat_mod._has_model_credentials({"open_ai_api_key": "YOUR API KEY"}))
        self.assertFalse(chat_mod._has_model_credentials({}))


if __name__ == "__main__":
    unittest.main()
