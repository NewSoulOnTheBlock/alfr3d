"""Single source of truth for model → bot_type resolution.

Bridge and AgentLLMModel both used to maintain nearly identical if/startswith
chains. Every new provider had to be wired in multiple places. Call
``resolve_bot_type`` from both paths instead.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from common import const


# Exact model-name → bot type (before prefix matching).
_EXACT_MODEL_MAP = {
    "text-davinci-003": const.OPEN_AI,
    "wenxin": const.BAIDU,
    "wenxin-4": const.BAIDU,
    "xunfei": const.XUNFEI,
    const.QWEN: const.QWEN_DASHSCOPE,
    const.QWEN_TURBO: const.QWEN_DASHSCOPE,
    const.QWEN_PLUS: const.QWEN_DASHSCOPE,
    const.QWEN_MAX: const.QWEN_DASHSCOPE,
    const.QIANFAN: const.QIANFAN,
    const.MODELSCOPE: const.MODELSCOPE,
    const.MOONSHOT: const.MOONSHOT,
    "moonshot-v1-8k": const.MOONSHOT,
    "moonshot-v1-32k": const.MOONSHOT,
    "moonshot-v1-128k": const.MOONSHOT,
    "abab6.5-chat": const.MiniMax,
    "abab6.5": const.MiniMax,
}

# Longest-prefix first. Keep multi-char prefixes ahead of shorter ones.
_PREFIX_MAP = (
    ("mimo-", const.MIMO),
    ("minimax", const.MiniMax),
    ("moonshot", const.MOONSHOT),
    ("kimi", const.MOONSHOT),
    ("deepseek", const.DEEPSEEK),
    ("doubao", const.DOUBAO),
    ("claude", const.CLAUDEAPI),
    ("gemini", const.GEMINI),
    ("ernie", const.QIANFAN),
    ("qwen", const.QWEN_DASHSCOPE),
    ("qwq", const.QWEN_DASHSCOPE),
    ("qvq", const.QWEN_DASHSCOPE),
    ("glm", const.ZHIPU_AI),
)


def _settings(settings: Optional[Mapping[str, Any]] = None) -> Mapping[str, Any]:
    if settings is not None:
        return settings
    try:
        from config import conf
        return conf() or {}
    except Exception:
        return {}


def resolve_bot_type(
    model_name: Optional[str] = None,
    settings: Optional[Mapping[str, Any]] = None,
) -> str:
    """Resolve the bot factory key for a model name / config snapshot.

    Precedence:
      1. use_linkai + linkai_api_key → LINKAI
      2. explicit bot_type in config (including custom:*)
      3. exact model name map
      4. prefix map on lowered model name
      5. OPENAI (OpenAI-compatible default)
    """
    cfg = _settings(settings)

    if cfg.get("use_linkai") and cfg.get("linkai_api_key"):
        return const.LINKAI

    configured = cfg.get("bot_type")
    if configured and isinstance(configured, str) and configured.strip():
        return configured.strip()

    if cfg.get("use_azure_chatgpt", False):
        return const.CHATGPTONAZURE

    if model_name is None:
        model_name = cfg.get("model") or const.DEFAULT_MODEL

    if not isinstance(model_name, str):
        model_name = str(model_name) if model_name is not None else ""

    if not model_name:
        return const.OPENAI

    if model_name in _EXACT_MODEL_MAP:
        return _EXACT_MODEL_MAP[model_name]

    lowered = model_name.lower()
    if lowered == const.QIANFAN or lowered.startswith("ernie"):
        return const.QIANFAN

    for prefix, btype in _PREFIX_MAP:
        if lowered.startswith(prefix):
            return btype

    return const.OPENAI
