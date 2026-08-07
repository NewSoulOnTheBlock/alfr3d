"""Discover and classify Anthropic / Codex (ChatGPT) OAuth credentials.

Supports:
  - Anthropic API keys (sk-ant-api…)
  - Anthropic Claude Code setup-token / OAuth (sk-ant-oat…)
  - OpenAI API keys (sk-…)
  - OpenAI Codex / ChatGPT OAuth tokens (from ~/.codex/auth.json or paste)

These helpers are used by setup and by model bots so subscription auth and
API-key auth can coexist without customers editing raw JSON by hand.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def is_anthropic_oauth_token(token: str) -> bool:
    t = (token or "").strip()
    if not t:
        return False
    low = t.lower()
    return low.startswith("sk-ant-oat") or "oat01" in low[:20]


def is_anthropic_api_key(token: str) -> bool:
    t = (token or "").strip()
    if not t:
        return False
    return t.startswith("sk-ant-") and not is_anthropic_oauth_token(t)


def is_openai_api_key(token: str) -> bool:
    t = (token or "").strip()
    if not t:
        return False
    # Classic sk-… keys; exclude Anthropic prefixes
    return t.startswith("sk-") and not t.startswith("sk-ant-")


# ---------------------------------------------------------------------------
# Anthropic discovery
# ---------------------------------------------------------------------------

def discover_anthropic_oauth_token() -> Optional[str]:
    """Return a Claude OAuth / setup-token if one is available on this machine."""
    for env_key in (
        "CLAUDE_CODE_OAUTH_TOKEN",
        "ANTHROPIC_AUTH_TOKEN",
        "CLAUDE_OAUTH_TOKEN",
    ):
        val = (os.environ.get(env_key) or "").strip()
        if val and is_anthropic_oauth_token(val):
            return val
        # Some installs put the setup-token in ANTHROPIC_API_KEY by mistake
        if val and is_anthropic_oauth_token(val):
            return val

    # Explicit API key env that is actually an oat token
    ant = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if ant and is_anthropic_oauth_token(ant):
        return ant

    home = Path.home()
    candidates = [
        home / ".claude" / ".credentials.json",
        home / ".claude" / "credentials.json",
        home / ".config" / "claude" / ".credentials.json",
        home / ".config" / "claude-code" / ".credentials.json",
    ]
    for path in candidates:
        token = _read_anthropic_token_file(path)
        if token:
            return token
    return None


def discover_anthropic_api_key() -> Optional[str]:
    for env_key in ("ANTHROPIC_API_KEY", "CLAUDE_API_KEY"):
        val = (os.environ.get(env_key) or "").strip()
        if val and is_anthropic_api_key(val):
            return val
    return None


def _read_anthropic_token_file(path: Path) -> Optional[str]:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None

    # Common shapes
    for key in (
        "claudeAiOauth",
        "claude_ai_oauth",
        "oauth",
        "token",
        "accessToken",
        "access_token",
    ):
        node = data.get(key)
        if isinstance(node, str) and is_anthropic_oauth_token(node):
            return node.strip()
        if isinstance(node, dict):
            for sub in ("accessToken", "access_token", "token", "oauthToken"):
                val = node.get(sub)
                if isinstance(val, str) and is_anthropic_oauth_token(val):
                    return val.strip()

    # Nested: { "claude.ai": { "accessToken": "..." } }
    for v in data.values():
        if isinstance(v, dict):
            for sub in ("accessToken", "access_token", "token"):
                val = v.get(sub)
                if isinstance(val, str) and is_anthropic_oauth_token(val):
                    return val.strip()
    return None


# ---------------------------------------------------------------------------
# Codex / ChatGPT OAuth discovery
# ---------------------------------------------------------------------------

def codex_auth_paths() -> Tuple[Path, ...]:
    home = Path.home()
    return (
        home / ".codex" / "auth.json",
        home / ".config" / "codex" / "auth.json",
    )


def discover_codex_oauth() -> Optional[Dict[str, Any]]:
    """Load Codex/ChatGPT OAuth material from disk or env.

    Returns a dict with at least ``access_token``, optionally ``refresh_token``,
    ``account_id``, ``source``.
    """
    env_access = (
        os.environ.get("CODEX_ACCESS_TOKEN")
        or os.environ.get("OPENAI_CODEX_ACCESS_TOKEN")
        or ""
    ).strip()
    if env_access:
        return {
            "access_token": env_access,
            "refresh_token": (os.environ.get("CODEX_REFRESH_TOKEN") or "").strip() or None,
            "source": "env",
        }

    for path in codex_auth_paths():
        parsed = _read_codex_auth_file(path)
        if parsed:
            parsed["source"] = str(path)
            return parsed
    return None


def _read_codex_auth_file(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None

    tokens = data.get("tokens") if isinstance(data.get("tokens"), dict) else data
    access = (
        tokens.get("access_token")
        or tokens.get("accessToken")
        or data.get("access_token")
        or data.get("accessToken")
    )
    if not isinstance(access, str) or not access.strip():
        # Some files only store OPENAI_API_KEY for apikey mode
        key = data.get("OPENAI_API_KEY") or data.get("api_key")
        if isinstance(key, str) and key.strip() and is_openai_api_key(key):
            return {"access_token": key.strip(), "auth_mode": "apikey"}
        return None

    refresh = tokens.get("refresh_token") or tokens.get("refreshToken")
    account_id = (
        tokens.get("account_id")
        or tokens.get("accountId")
        or data.get("account_id")
        or data.get("accountId")
    )
    return {
        "access_token": access.strip(),
        "refresh_token": refresh.strip() if isinstance(refresh, str) else None,
        "account_id": account_id if isinstance(account_id, str) else None,
        "auth_mode": "oauth",
    }


def discover_openai_api_key() -> Optional[str]:
    for env_key in ("OPENAI_API_KEY", "OPENAI_KEY"):
        val = (os.environ.get(env_key) or "").strip()
        if val and is_openai_api_key(val):
            return val
    return None


# ---------------------------------------------------------------------------
# Effective credential for runtime
# ---------------------------------------------------------------------------

def resolve_claude_credential(conf_get) -> Tuple[Optional[str], str]:
    """Return (token, mode) where mode is 'oauth' | 'api_key' | 'none'.

    ``conf_get`` is a callable like ``conf().get``.
    """
    # Explicit OAuth field first
    oat = (conf_get("claude_oauth_token") or "").strip()
    if oat:
        return oat, "oauth"

    auth_mode = (conf_get("auth_mode") or conf_get("claude_auth_mode") or "").strip().lower()
    key = (conf_get("claude_api_key") or "").strip()

    if auth_mode in ("oauth", "anthropic_oauth", "claude_oauth", "setup_token"):
        if key:
            return key, "oauth"
        discovered = discover_anthropic_oauth_token()
        if discovered:
            return discovered, "oauth"
        return None, "none"

    if key:
        if is_anthropic_oauth_token(key):
            return key, "oauth"
        return key, "api_key"

    # Auto-discover
    discovered = discover_anthropic_oauth_token()
    if discovered:
        return discovered, "oauth"
    api = discover_anthropic_api_key()
    if api:
        return api, "api_key"
    return None, "none"


def resolve_openai_credential(conf_get) -> Tuple[Optional[str], str]:
    """Return (token, mode) for OpenAI / Codex. mode: oauth | api_key | none."""
    auth_mode = (conf_get("auth_mode") or conf_get("openai_auth_mode") or "").strip().lower()

    codex_token = (conf_get("codex_oauth_access_token") or "").strip()
    if codex_token:
        return codex_token, "oauth"

    if auth_mode in ("oauth", "codex_oauth", "chatgpt_oauth", "openai_oauth"):
        discovered = discover_codex_oauth()
        if discovered and discovered.get("access_token"):
            return discovered["access_token"], "oauth"
        key = (conf_get("open_ai_api_key") or "").strip()
        if key:
            return key, "oauth" if not is_openai_api_key(key) else "api_key"
        return None, "none"

    key = (conf_get("open_ai_api_key") or "").strip()
    if key:
        return key, "api_key"

    api = discover_openai_api_key()
    if api:
        return api, "api_key"

    discovered = discover_codex_oauth()
    if discovered and discovered.get("access_token"):
        return discovered["access_token"], discovered.get("auth_mode") or "oauth"

    return None, "none"


def anthropic_request_headers(token: str, mode: str = "api_key") -> Dict[str, str]:
    """Headers for Anthropic Messages API given a credential and mode."""
    headers = {
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    if mode == "oauth" or is_anthropic_oauth_token(token):
        headers["Authorization"] = f"Bearer {token}"
        # OAuth clients often need the beta flag for third-party / setup-token use
        headers["anthropic-beta"] = "oauth-2025-04-20"
    else:
        headers["x-api-key"] = token
    return headers
