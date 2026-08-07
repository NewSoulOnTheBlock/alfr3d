"""Mem0 cloud memory client (HTTP).

Integrates with Alfr3d's local MemoryManager as a second tier:
  - search: semantic recall from Mem0, merged with local hybrid search
  - add / add_messages: durable cloud store (complements MEMORY.md + SQLite)

Auth header format per Mem0 cloud docs: ``Authorization: Token <api-key>``.
Uses ``requests`` only (no mem0ai package required for lean installs).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests

from common.log import logger


@dataclass
class Mem0Memory:
    """Normalized Mem0 search hit."""
    content: str
    score: float = 0.0
    memory_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Mem0Client:
    """Thin REST client for Mem0 Platform."""

    def __init__(
        self,
        api_key: str,
        user_id: str = "alfr3d-user",
        agent_id: str = "alfr3d",
        base_url: str = "https://api.mem0.ai/v1",
        timeout: float = 20.0,
    ):
        self.api_key = (api_key or "").strip()
        self.user_id = (user_id or "alfr3d-user").strip() or "alfr3d-user"
        self.agent_id = (agent_id or "alfr3d").strip() or "alfr3d"
        self.base_url = (base_url or "https://api.mem0.ai/v1").rstrip("/")
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.api_key}",
        }

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def search(
        self,
        query: str,
        *,
        limit: int = 8,
        user_id: Optional[str] = None,
    ) -> List[Mem0Memory]:
        if not self.enabled or not (query or "").strip():
            return []
        uid = (user_id or self.user_id).strip() or self.user_id
        body = {
            "query": query,
            "user_id": uid,
            "agent_id": self.agent_id,
            "limit": max(1, min(int(limit), 50)),
        }
        try:
            resp = requests.post(
                self._url("/memories/search/"),
                headers=self._headers(),
                json=body,
                timeout=self.timeout,
            )
            # Some deployments omit trailing slash
            if resp.status_code == 404:
                resp = requests.post(
                    self._url("/memories/search"),
                    headers=self._headers(),
                    json=body,
                    timeout=self.timeout,
                )
            if resp.status_code >= 400:
                logger.warning(
                    f"[Mem0] search failed: HTTP {resp.status_code} {resp.text[:200]}"
                )
                return []
            data = resp.json()
            raw = data if isinstance(data, list) else (
                data.get("results") or data.get("memories") or []
            )
            out: List[Mem0Memory] = []
            for item in raw:
                mem = _normalize(item)
                if mem:
                    out.append(mem)
            return out
        except Exception as e:
            logger.warning(f"[Mem0] search error: {e}")
            return []

    def add(
        self,
        content: str,
        *,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        if not self.enabled or not (content or "").strip():
            return False
        return self.add_messages(
            [{"role": "user", "content": content.strip()}],
            user_id=user_id,
            metadata=metadata,
        )

    def add_messages(
        self,
        messages: List[Dict[str, str]],
        *,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        if not self.enabled or not messages:
            return False
        uid = (user_id or self.user_id).strip() or self.user_id
        body: Dict[str, Any] = {
            "messages": messages,
            "user_id": uid,
            "agent_id": self.agent_id,
        }
        if metadata:
            body["metadata"] = metadata
        try:
            resp = requests.post(
                self._url("/memories/"),
                headers=self._headers(),
                json=body,
                timeout=self.timeout,
            )
            if resp.status_code == 404:
                resp = requests.post(
                    self._url("/memories"),
                    headers=self._headers(),
                    json=body,
                    timeout=self.timeout,
                )
            if resp.status_code >= 400:
                logger.warning(
                    f"[Mem0] add failed: HTTP {resp.status_code} {resp.text[:200]}"
                )
                return False
            return True
        except Exception as e:
            logger.warning(f"[Mem0] add error: {e}")
            return False


def _normalize(value: Any) -> Optional[Mem0Memory]:
    if isinstance(value, str) and value.strip():
        return Mem0Memory(content=value.strip())
    if not isinstance(value, dict):
        return None
    content = value.get("memory") or value.get("content") or value.get("text")
    if not isinstance(content, str) or not content.strip():
        return None
    score = value.get("score")
    if not isinstance(score, (int, float)):
        score = 0.0
    mid = value.get("id") or value.get("memory_id")
    meta = value.get("metadata") if isinstance(value.get("metadata"), dict) else None
    return Mem0Memory(
        content=content.strip(),
        score=float(score),
        memory_id=str(mid) if mid else None,
        metadata=meta,
    )


def mem0_from_config(conf_get=None) -> Optional[Mem0Client]:
    """Build a Mem0Client from Alfr3d config, or None if disabled / missing key."""
    if conf_get is None:
        try:
            from config import conf
            conf_get = conf().get
        except Exception:
            conf_get = lambda _k, d=None: d  # noqa: E731

    enabled = conf_get("mem0_enabled", True)
    # Explicit false disables even if key present
    if enabled is False:
        return None

    api_key = (
        conf_get("mem0_api_key")
        or os.environ.get("MEM0_API_KEY")
        or ""
    ).strip()
    if not api_key or api_key.lower() in ("your api key", "your_api_key", "xxx"):
        return None

    user_id = (conf_get("mem0_user_id") or os.environ.get("MEM0_USER_ID") or "alfr3d-user").strip()
    agent_id = (conf_get("mem0_agent_id") or "alfr3d").strip()
    base_url = (
        conf_get("mem0_base_url")
        or os.environ.get("MEM0_BASE_URL")
        or "https://api.mem0.ai/v1"
    ).strip()

    client = Mem0Client(
        api_key=api_key,
        user_id=user_id,
        agent_id=agent_id,
        base_url=base_url,
    )
    logger.info(f"[Mem0] Cloud memory enabled (user_id={user_id}, agent_id={agent_id})")
    return client
