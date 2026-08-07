"""Prompt section budgets — hard caps to keep system prompts lean.

Each section is truncated to a character budget after build. Budgets are
configurable via config.json ``prompt_budgets`` (chars, not tokens). Defaults
target a ~24k-char system prompt ceiling before conversation history.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

# Default character budgets (≈ tokens × 4 for mixed EN/code).
DEFAULT_BUDGETS: Dict[str, int] = {
    "soul": 3500,           # core SOUL ~2k; room if full SOUL enabled
    "tools": 3000,
    "skills": 2500,
    "memory": 2000,
    "knowledge": 2500,
    "workspace": 2500,
    "user_identity": 800,
    "context_files": 10000,  # AGENT/USER/BUSINESS/RULE/MEMORY
    "runtime": 800,
    "response_language": 400,
    "total": 28000,
}

_TRUNCATE_MARK = "\n\n…(section truncated to fit prompt budget)…\n"


def get_budgets(settings: Optional[Mapping[str, Any]] = None) -> Dict[str, int]:
    budgets = dict(DEFAULT_BUDGETS)
    try:
        cfg = settings
        if cfg is None:
            from config import conf
            cfg = conf() or {}
        raw = cfg.get("prompt_budgets") or {}
        if isinstance(raw, dict):
            for key, value in raw.items():
                if key in budgets:
                    try:
                        budgets[key] = max(200, int(value))
                    except (TypeError, ValueError):
                        pass
    except Exception:
        pass
    return budgets


def estimate_chars(sections: List[str]) -> int:
    return sum(len(s) for s in sections) + max(0, len(sections) - 1)


def apply_section_budget(lines: List[str], budget: int) -> List[str]:
    """Join section lines and truncate to budget if needed."""
    if not lines or budget <= 0:
        return lines
    text = "\n".join(lines)
    if len(text) <= budget:
        return lines
    keep = max(0, budget - len(_TRUNCATE_MARK))
    truncated = text[:keep].rstrip() + _TRUNCATE_MARK
    return [truncated]


def apply_total_budget(sections: List[str], total_budget: int) -> List[str]:
    """If the joined prompt exceeds total, drop trailing soft sections first.

    Soft sections (by content markers) are trimmed from the end of the list
    except the leading identity/soul block and the final response-language rule.
    """
    if total_budget <= 0 or estimate_chars(sections) <= total_budget:
        return sections

    # Preserve first section (usually SOUL) and last (response language).
    if len(sections) <= 2:
        joined = "\n".join(sections)
        if len(joined) <= total_budget:
            return sections
        keep = max(0, total_budget - len(_TRUNCATE_MARK))
        return [joined[:keep].rstrip() + _TRUNCATE_MARK]

    head, *middle, tail = sections
    # Drop middle sections from the end until under budget.
    while middle and estimate_chars([head, *middle, tail]) > total_budget:
        middle.pop()
    result = [head, *middle, tail]
    if estimate_chars(result) <= total_budget:
        return result

    # Last resort: hard truncate the whole prompt.
    joined = "\n".join(result)
    keep = max(0, total_budget - len(_TRUNCATE_MARK))
    return [joined[:keep].rstrip() + _TRUNCATE_MARK]
