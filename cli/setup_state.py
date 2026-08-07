"""Shared setup / readiness checks for the customer CLI."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from cli.utils import get_project_root, load_config_json

# Config fields that count as "a model is ready".
MODEL_KEY_FIELDS = (
    "open_ai_api_key",
    "claude_api_key",
    "deepseek_api_key",
    "gemini_api_key",
    "dashscope_api_key",
    "zhipu_ai_api_key",
    "moonshot_api_key",
    "ark_api_key",
    "minimax_api_key",
    "mimo_api_key",
    "qianfan_api_key",
    "linkai_api_key",
    "custom_api_key",
    "baidu_wenxin_api_key",
)

PLACEHOLDER_KEYS = frozenset({
    "",
    "your api key",
    "your_api_key",
    "sk-xxx",
    "xxx",
    "changeme",
    "replace_me",
})


def is_placeholder(value: Any) -> bool:
    if value is None:
        return True
    text = str(value).strip()
    if not text:
        return True
    return text.lower() in PLACEHOLDER_KEYS


def has_model_credentials(cfg: Optional[Dict[str, Any]] = None) -> bool:
    """True when a usable model credential is configured.

    When *cfg* is passed explicitly (tests / dry-runs), only that dict is
    inspected. When *cfg* is omitted, also checks environment variables and
    local Claude/Codex CLI logins on this machine.
    """
    scan_environment = cfg is None
    cfg = cfg if cfg is not None else load_config_json()
    oauth_fields = (
        "claude_oauth_token",
        "codex_oauth_access_token",
    )
    for key in MODEL_KEY_FIELDS + oauth_fields:
        if not is_placeholder(cfg.get(key, "")):
            return True
    for item in cfg.get("custom_providers") or []:
        if isinstance(item, dict) and not is_placeholder(item.get("api_key", "")):
            return True
    if not scan_environment:
        return False
    for env_key in (
        "OPENAI_API_KEY",
        "CLAUDE_API_KEY",
        "ANTHROPIC_API_KEY",
        "CLAUDE_CODE_OAUTH_TOKEN",
        "ANTHROPIC_AUTH_TOKEN",
        "CODEX_ACCESS_TOKEN",
        "DEEPSEEK_API_KEY",
        "GEMINI_API_KEY",
    ):
        if not is_placeholder(os.environ.get(env_key, "")):
            return True
    # Local CLI logins (Claude setup-token / Codex auth.json)
    try:
        from common.oauth_credentials import (
            discover_anthropic_oauth_token,
            discover_codex_oauth,
        )
        if discover_anthropic_oauth_token():
            return True
        codex = discover_codex_oauth()
        if codex and codex.get("access_token"):
            return True
    except Exception:
        pass
    return False


def is_setup_complete(cfg: Optional[Dict[str, Any]] = None) -> bool:
    """True when the customer finished setup and can use chat productively."""
    cfg = cfg if cfg is not None else load_config_json()
    if not cfg:
        return False
    if not has_model_credentials(cfg):
        return False
    # Explicit completion marker set by `alfr3d setup`.
    if cfg.get("setup_completed_at"):
        return True
    # Legacy installs: key present is enough to chat, but we still recommend setup.
    return False


def config_path() -> str:
    return os.path.join(get_project_root(), "config.json")


def template_path() -> str:
    return os.path.join(get_project_root(), "config-template.json")
