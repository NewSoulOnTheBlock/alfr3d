"""Tests for immutable SOUL.md base personality injection."""

import os
import tempfile
import unittest
from unittest.mock import patch

from agent.prompt.builder import build_agent_system_prompt
from agent.prompt.soul import (
    IMMUTABLE_IDENTITY_HEADER,
    SOUL_DENIED_MESSAGE,
    is_soul_path,
    load_soul_text,
    soul_file_path,
)
from agent.tools.edit.edit import Edit
from agent.tools.write.write import Write


class TestSoulIdentity(unittest.TestCase):
    def test_soul_file_ships_with_package(self):
        path = soul_file_path()
        self.assertTrue(os.path.isfile(path), f"missing SOUL.md at {path}")
        text = load_soul_text()
        self.assertIn("elite personal steward", text.lower())
        self.assertIn("Immutable Personality Rule", text)

    def test_main_agent_prompt_includes_soul(self):
        # context_files=[] is the main-agent path (list present, maybe empty).
        prompt = build_agent_system_prompt(
            workspace_dir="/tmp/ws",
            language="en",
            context_files=[],
            tools=[],
        )
        self.assertIn("ALFR3D IMMUTABLE IDENTITY", prompt)
        self.assertIn("elite personal steward", prompt.lower())
        self.assertIn("SOUL.md is the permanent base personality", prompt)

    def test_subagent_path_skips_soul(self):
        # context_files=None is the sub-agent path.
        prompt = build_agent_system_prompt(
            workspace_dir="/tmp/ws",
            language="en",
            context_files=None,
            tools=[],
        )
        self.assertNotIn("ALFR3D IMMUTABLE IDENTITY", prompt)
        self.assertNotIn(IMMUTABLE_IDENTITY_HEADER.strip().splitlines()[0], prompt)

    def test_is_soul_path_matches_package_and_basename(self):
        self.assertTrue(is_soul_path(soul_file_path()))
        self.assertTrue(is_soul_path(os.path.join(tempfile.gettempdir(), "SOUL.md")))
        self.assertFalse(is_soul_path(os.path.join(tempfile.gettempdir(), "AGENT.md")))

    def test_write_tool_blocks_soul(self):
        tool = Write(config={"cwd": tempfile.gettempdir()})
        result = tool.execute({
            "path": "SOUL.md",
            "content": "hijack",
        })
        self.assertEqual(result.status, "error")
        self.assertIn("immutable", result.result.lower())

    def test_edit_tool_blocks_soul(self):
        with tempfile.TemporaryDirectory() as tmp:
            soul = os.path.join(tmp, "SOUL.md")
            with open(soul, "w", encoding="utf-8") as f:
                f.write("original")
            tool = Edit(config={"cwd": tmp})
            result = tool.execute({
                "path": "SOUL.md",
                "oldText": "original",
                "newText": "hijack",
            })
            self.assertEqual(result.status, "error")
            self.assertIn("immutable", (result.result or SOUL_DENIED_MESSAGE).lower())
            with open(soul, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "original")


if __name__ == "__main__":
    unittest.main()
