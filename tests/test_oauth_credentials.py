"""Tests for Anthropic OAuth + Codex OAuth credential helpers."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from common.oauth_credentials import (
    anthropic_request_headers,
    discover_anthropic_oauth_token,
    discover_codex_oauth,
    is_anthropic_api_key,
    is_anthropic_oauth_token,
    is_openai_api_key,
    resolve_claude_credential,
    resolve_openai_credential,
)


class TestTokenClassification(unittest.TestCase):
    def test_anthropic_shapes(self):
        self.assertTrue(is_anthropic_oauth_token("sk-ant-oat01-abcdef"))
        self.assertFalse(is_anthropic_oauth_token("sk-ant-api03-abcdef"))
        self.assertTrue(is_anthropic_api_key("sk-ant-api03-abcdef"))
        self.assertFalse(is_anthropic_api_key("sk-ant-oat01-abcdef"))

    def test_openai_key(self):
        self.assertTrue(is_openai_api_key("sk-proj-abc123"))
        self.assertFalse(is_openai_api_key("sk-ant-api03-x"))


class TestAnthropicHeaders(unittest.TestCase):
    def test_api_key_header(self):
        h = anthropic_request_headers("sk-ant-api03-x", "api_key")
        self.assertEqual(h.get("x-api-key"), "sk-ant-api03-x")
        self.assertNotIn("Authorization", h)

    def test_oauth_header(self):
        h = anthropic_request_headers("sk-ant-oat01-x", "oauth")
        self.assertTrue(h.get("Authorization", "").startswith("Bearer "))
        self.assertNotIn("x-api-key", h)


class TestResolveClaude(unittest.TestCase):
    def test_prefers_oauth_field(self):
        cfg = {
            "claude_oauth_token": "sk-ant-oat01-from-field",
            "claude_api_key": "sk-ant-api03-other",
        }
        token, mode = resolve_claude_credential(cfg.get)
        self.assertEqual(token, "sk-ant-oat01-from-field")
        self.assertEqual(mode, "oauth")

    def test_detects_oat_in_api_key_field(self):
        cfg = {"claude_api_key": "sk-ant-oat01-mirrored"}
        token, mode = resolve_claude_credential(cfg.get)
        self.assertEqual(mode, "oauth")
        self.assertEqual(token, "sk-ant-oat01-mirrored")

    def test_api_key_mode(self):
        cfg = {"claude_api_key": "sk-ant-api03-plain", "claude_auth_mode": "api_key"}
        token, mode = resolve_claude_credential(cfg.get)
        self.assertEqual(mode, "api_key")
        self.assertEqual(token, "sk-ant-api03-plain")


class TestDiscoverCodex(unittest.TestCase):
    def test_reads_auth_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            auth = Path(tmp) / "auth.json"
            auth.write_text(
                json.dumps({
                    "tokens": {
                        "access_token": "codex-access-xyz",
                        "refresh_token": "codex-refresh-xyz",
                        "account_id": "acct-1",
                    }
                }),
                encoding="utf-8",
            )
            with patch(
                "common.oauth_credentials.codex_auth_paths",
                return_value=(auth,),
            ):
                found = discover_codex_oauth()
            self.assertIsNotNone(found)
            self.assertEqual(found["access_token"], "codex-access-xyz")
            self.assertEqual(found["refresh_token"], "codex-refresh-xyz")

    def test_resolve_openai_codex_mode(self):
        cfg = {
            "auth_mode": "codex_oauth",
            "codex_oauth_access_token": "codex-tok",
        }
        token, mode = resolve_openai_credential(cfg.get)
        self.assertEqual(token, "codex-tok")
        self.assertEqual(mode, "oauth")


class TestSetupProviderCatalog(unittest.TestCase):
    def test_oauth_providers_listed(self):
        from cli.commands.setup import PROVIDERS
        ids = {p["id"] for p in PROVIDERS}
        self.assertIn("anthropic_oauth", ids)
        self.assertIn("openai_codex_oauth", ids)
        self.assertIn("claude", ids)
        self.assertIn("openai", ids)
        anth = next(p for p in PROVIDERS if p["id"] == "anthropic_oauth")
        self.assertEqual(anth["auth_kind"], "anthropic_oauth")
        codex = next(p for p in PROVIDERS if p["id"] == "openai_codex_oauth")
        self.assertEqual(codex["auth_kind"], "codex_oauth")


if __name__ == "__main__":
    unittest.main()
