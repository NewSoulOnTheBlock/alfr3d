"""Tier A leanness: SOUL core, budgets, provider registry, MCP default."""

import os
import tempfile
import unittest
from unittest.mock import patch

from agent.prompt.budgets import (
    DEFAULT_BUDGETS,
    apply_section_budget,
    apply_total_budget,
    estimate_chars,
    get_budgets,
)
from agent.prompt.soul import (
    build_soul_section,
    load_soul_core_text,
    load_soul_text,
    use_full_soul,
)
from common import const
from models.provider_registry import resolve_bot_type


class TestSoulTiers(unittest.TestCase):
    def test_core_is_much_smaller_than_full(self):
        core = load_soul_core_text()
        full = load_soul_text()
        self.assertLess(len(core), len(full) * 0.45)
        self.assertIn("elite personal steward", core.lower())
        self.assertIn("Competence without ego", core)

    def test_default_section_uses_core(self):
        with patch.dict(os.environ, {"ALFR3D_SOUL_FULL": "0"}, clear=False):
            # Clear cached conf path — use env
            load_soul_core_text.cache_clear()
            section = "\n".join(build_soul_section("en", full=False))
            self.assertIn("SOUL.core", section)
            self.assertNotIn("Signature Responses", section)

    def test_full_flag_injects_full_soul(self):
        section = "\n".join(build_soul_section("en", full=True))
        self.assertIn("elite personal steward", section.lower())
        # Full file has signature examples section
        self.assertTrue(
            "Signature" in section or "Preferred One-Liners" in section or len(section) > 8000
        )


class TestPromptBudgets(unittest.TestCase):
    def test_section_budget_truncates(self):
        lines = ["x" * 5000]
        out = apply_section_budget(lines, 1000)
        text = "\n".join(out)
        self.assertLessEqual(len(text), 1000 + 50)
        self.assertIn("truncated", text.lower())

    def test_total_budget_drops_middle(self):
        sections = ["HEAD", "M1" * 2000, "M2" * 2000, "TAIL"]
        out = apply_total_budget(sections, 500)
        joined = "\n".join(out)
        self.assertIn("HEAD", joined)
        self.assertIn("TAIL", joined)
        self.assertLessEqual(estimate_chars(out), 500 + 80)

    def test_default_budgets_present(self):
        b = get_budgets({})
        for key in DEFAULT_BUDGETS:
            self.assertIn(key, b)


class TestProviderRegistry(unittest.TestCase):
    def test_prefix_and_exact(self):
        self.assertEqual(resolve_bot_type("claude-sonnet-4-5", {}), const.CLAUDEAPI)
        self.assertEqual(resolve_bot_type("deepseek-v4-flash", {}), const.DEEPSEEK)
        self.assertEqual(resolve_bot_type("gpt-4o", {}), const.OPENAI)
        self.assertEqual(resolve_bot_type("gemini-2.0-flash", {}), const.GEMINI)
        self.assertEqual(resolve_bot_type("kimi-k2", {}), const.MOONSHOT)
        self.assertEqual(resolve_bot_type("mimo-v2", {}), const.MIMO)
        self.assertEqual(resolve_bot_type("qwen-plus", {}), const.QWEN_DASHSCOPE)

    def test_explicit_bot_type_wins(self):
        self.assertEqual(
            resolve_bot_type("gpt-4o", {"bot_type": "claudeAPI"}),
            "claudeAPI",
        )

    def test_linkai_override(self):
        self.assertEqual(
            resolve_bot_type("gpt-4o", {"use_linkai": True, "linkai_api_key": "k"}),
            const.LINKAI,
        )


class TestMcpRetrievalDefault(unittest.TestCase):
    def test_config_default_true(self):
        from config import available_setting
        self.assertTrue(available_setting.get("mcp_tool_retrieval_enabled"))


class TestLazyTools(unittest.TestCase):
    def test_lazy_specs_defined(self):
        from agent.tools import LAZY_TOOL_SPECS, load_lazy_tool_class
        self.assertIn("BrowserTool", LAZY_TOOL_SPECS)
        self.assertIn("Vision", LAZY_TOOL_SPECS)
        self.assertIn("WebSearch", LAZY_TOOL_SPECS)
        # load should not crash even if heavy deps missing
        cls = load_lazy_tool_class("BrowserTool")
        # May be None or a class depending on env
        self.assertTrue(cls is None or isinstance(cls, type))


if __name__ == "__main__":
    unittest.main()
