"""Tests for Mem0 cloud memory integration."""

import asyncio
import unittest
from unittest.mock import MagicMock, patch

from agent.memory.mem0_client import Mem0Client, Mem0Memory, _normalize, mem0_from_config
from agent.memory.manager import MemoryManager
from agent.memory.storage import SearchResult


class TestMem0Normalize(unittest.TestCase):
    def test_normalize_shapes(self):
        self.assertEqual(_normalize("plain fact").content, "plain fact")
        m = _normalize({"memory": "likes tea", "score": 0.9, "id": "abc"})
        self.assertEqual(m.content, "likes tea")
        self.assertEqual(m.score, 0.9)
        self.assertEqual(m.memory_id, "abc")
        self.assertIsNone(_normalize({}))


class TestMem0FromConfig(unittest.TestCase):
    def test_disabled_without_key(self):
        with patch.dict("os.environ", {"MEM0_API_KEY": ""}, clear=False):
            self.assertIsNone(mem0_from_config(lambda k, d=None: d if d is not None else ""))

    def test_enabled_with_key(self):
        cfg = {
            "mem0_enabled": True,
            "mem0_api_key": "m0-test-key",
            "mem0_user_id": "user-1",
            "mem0_agent_id": "alfr3d",
        }
        client = mem0_from_config(cfg.get)
        self.assertIsNotNone(client)
        self.assertTrue(client.enabled)
        self.assertEqual(client.user_id, "user-1")

    def test_explicit_disable(self):
        cfg = {"mem0_enabled": False, "mem0_api_key": "m0-test-key"}
        self.assertIsNone(mem0_from_config(cfg.get))


class TestMem0ClientHTTP(unittest.TestCase):
    def test_search_parses_results(self):
        client = Mem0Client(api_key="m0-x", user_id="u1")
        fake = MagicMock()
        fake.status_code = 200
        fake.json.return_value = {
            "results": [
                {"memory": "User prefers bullets", "score": 0.88, "id": "1"},
            ]
        }
        with patch("agent.memory.mem0_client.requests.post", return_value=fake) as post:
            hits = client.search("preferences", limit=5)
        self.assertEqual(len(hits), 1)
        self.assertIn("bullets", hits[0].content)
        post.assert_called()
        # Auth header uses Token prefix
        headers = post.call_args.kwargs.get("headers") or post.call_args[1].get("headers")
        self.assertTrue(headers["Authorization"].startswith("Token "))

    def test_add_messages(self):
        client = Mem0Client(api_key="m0-x", user_id="u1")
        fake = MagicMock()
        fake.status_code = 200
        fake.json.return_value = {"status": "PENDING"}
        with patch("agent.memory.mem0_client.requests.post", return_value=fake):
            ok = client.add_messages([
                {"role": "user", "content": "I like short answers"},
                {"role": "assistant", "content": "Understood."},
            ])
        self.assertTrue(ok)


class TestMemoryManagerMem0Merge(unittest.TestCase):
    def test_merge_dedupes_and_includes_mem0(self):
        mm = MemoryManager.__new__(MemoryManager)
        local = [
            SearchResult("MEMORY.md", 1, 2, 0.9, "prefers dark mode", "memory"),
        ]
        remote = [
            SearchResult("mem0://cloud", 0, 0, 0.7, "prefers dark mode", "mem0"),
            SearchResult("mem0://cloud", 0, 0, 0.8, "works evenings only", "mem0"),
        ]
        merged = MemoryManager._merge_with_mem0(mm, local, remote)
        snippets = [r.snippet for r in merged]
        self.assertEqual(snippets.count("prefers dark mode"), 1)
        self.assertIn("works evenings only", snippets)

    def test_remember_exchange_calls_mem0(self):
        mm = MemoryManager.__new__(MemoryManager)
        mock_mem0 = MagicMock()
        mock_mem0.enabled = True
        mm.mem0 = mock_mem0
        mm.remember_exchange("hello", "hi there")
        mock_mem0.add_messages.assert_called_once()
        args = mock_mem0.add_messages.call_args[0][0]
        self.assertEqual(args[0]["role"], "user")
        self.assertEqual(args[1]["role"], "assistant")


class TestSetupMentionsMem0(unittest.TestCase):
    def test_setup_source_has_mem0_prompt(self):
        from pathlib import Path
        src = Path(__file__).resolve().parents[1] / "cli" / "commands" / "setup.py"
        text = src.read_text(encoding="utf-8")
        self.assertIn("Mem0", text)
        self.assertIn("mem0_api_key", text)


if __name__ == "__main__":
    unittest.main()
