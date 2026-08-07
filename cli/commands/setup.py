"""Customer-facing interactive setup wizard.

Walks through model credentials, product preferences, and business intake so
Alfr3d knows *why* the user is here — not only which API key to use.

Usage:
  alfr3d setup
  alfr3d setup --force    # re-run even if already complete
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone as dt_timezone
from typing import Any, Dict, List, Optional, Tuple

import click

from cli.setup_state import (
    config_path,
    has_model_credentials,
    is_placeholder,
    is_setup_complete,
    template_path,
)
from cli.utils import ensure_sys_path, get_project_root, get_workspace_dir, load_config_json


# ---------------------------------------------------------------------------
# Provider catalog (customer-facing names → config fields)
# ---------------------------------------------------------------------------

PROVIDERS: List[Dict[str, Any]] = [
    {
        "id": "openai",
        "label": "OpenAI — API key (GPT)",
        "auth_kind": "api_key",
        "key_field": "open_ai_api_key",
        "base_field": "open_ai_api_base",
        "default_base": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
        "bot_type": "openai",
        "auth_mode": "api_key",
        "hint": "https://platform.openai.com/api-keys",
    },
    {
        "id": "openai_codex_oauth",
        "label": "OpenAI Codex — OAuth (ChatGPT / Codex CLI sign-in)",
        "auth_kind": "codex_oauth",
        "key_field": "codex_oauth_access_token",
        "base_field": "open_ai_api_base",
        "default_base": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
        "bot_type": "openai",
        "auth_mode": "codex_oauth",
        "hint": "Sign in with ChatGPT via Codex CLI, or paste an access token",
    },
    {
        "id": "claude",
        "label": "Anthropic — API key (Claude)",
        "auth_kind": "api_key",
        "key_field": "claude_api_key",
        "base_field": "claude_api_base",
        "default_base": "https://api.anthropic.com/v1",
        "default_model": "claude-sonnet-4-5",
        "bot_type": "claudeAPI",
        "auth_mode": "api_key",
        "hint": "https://console.anthropic.com/settings/keys",
    },
    {
        "id": "anthropic_oauth",
        "label": "Anthropic — OAuth / Claude setup-token (Pro·Max subscription)",
        "auth_kind": "anthropic_oauth",
        "key_field": "claude_oauth_token",
        "base_field": "claude_api_base",
        "default_base": "https://api.anthropic.com/v1",
        "default_model": "claude-sonnet-4-5",
        "bot_type": "claudeAPI",
        "auth_mode": "anthropic_oauth",
        "hint": "Run: claude setup-token   (prints sk-ant-oat01-…)",
    },
    {
        "id": "deepseek",
        "label": "DeepSeek — API key",
        "auth_kind": "api_key",
        "key_field": "deepseek_api_key",
        "base_field": "deepseek_api_base",
        "default_base": "https://api.deepseek.com/v1",
        "default_model": "deepseek-v4-flash",
        "bot_type": "deepseek",
        "auth_mode": "api_key",
        "hint": "https://platform.deepseek.com/",
    },
    {
        "id": "gemini",
        "label": "Google Gemini — API key",
        "auth_kind": "api_key",
        "key_field": "gemini_api_key",
        "base_field": "gemini_api_base",
        "default_base": "https://generativelanguage.googleapis.com",
        "default_model": "gemini-2.0-flash",
        "bot_type": "gemini",
        "auth_mode": "api_key",
        "hint": "https://aistudio.google.com/apikey",
    },
    {
        "id": "dashscope",
        "label": "Alibaba Qwen (DashScope) — API key",
        "auth_kind": "api_key",
        "key_field": "dashscope_api_key",
        "base_field": None,
        "default_base": None,
        "default_model": "qwen-plus",
        "bot_type": "qwen",
        "auth_mode": "api_key",
        "hint": "https://dashscope.console.aliyun.com/",
    },
    {
        "id": "moonshot",
        "label": "Moonshot / Kimi — API key",
        "auth_kind": "api_key",
        "key_field": "moonshot_api_key",
        "base_field": "moonshot_base_url",
        "default_base": "https://api.moonshot.cn/v1",
        "default_model": "kimi-k2",
        "bot_type": "moonshot",
        "auth_mode": "api_key",
        "hint": "https://platform.moonshot.cn/",
    },
    {
        "id": "zhipu",
        "label": "Zhipu GLM — API key",
        "auth_kind": "api_key",
        "key_field": "zhipu_ai_api_key",
        "base_field": "zhipu_ai_api_base",
        "default_base": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-4",
        "bot_type": "zhipu",
        "auth_mode": "api_key",
        "hint": "https://open.bigmodel.cn/",
    },
]


# Business intake options
BUSINESS_STATUS = [
    ("not_yet", "No — I have not started a business yet"),
    ("planning", "Not yet, but I am actively planning to start"),
    ("yes_early", "Yes — early stage (pre-revenue or just launched)"),
    ("yes_operating", "Yes — operating business with customers or revenue"),
    ("yes_established", "Yes — established business (multiple years / team)"),
]

BUSINESS_INTENT = [
    ("learn", "Learn how to start and build a business from scratch"),
    ("launch", "Launch the business I am planning"),
    ("grow", "Grow and strengthen the business I already have"),
    ("ops", "Improve day-to-day operations, systems, and organization"),
    ("finance", "Get help with books, credit, cash flow, or fundraising"),
    ("explore", "Explore options — I am not sure yet"),
]

PRIMARY_FOCUS = [
    ("formation", "Business formation, EIN, licenses, structure"),
    ("customers", "Finding customers, sales, marketing"),
    ("product", "Product or service development"),
    ("money", "Money: pricing, bookkeeping, credit, funding"),
    ("ops", "Operations, tools, and productivity"),
    ("strategy", "Strategy and decision support"),
    ("learning", "Education and skill-building"),
    ("other", "Something else (I'll describe it)"),
]


def _echo(msg: str = "") -> None:
    click.echo(msg)


def _title(msg: str) -> None:
    click.echo()
    click.echo(click.style(msg, fg="cyan", bold=True))


def _dim(msg: str) -> None:
    click.echo(click.style(msg, fg="bright_black"))


def _ok(msg: str) -> None:
    click.echo(click.style(msg, fg="green"))


def _warn(msg: str) -> None:
    click.echo(click.style(msg, fg="yellow"))


def _section(n: int, total: int, title: str) -> None:
    click.echo()
    click.echo(click.style(f"── Step {n}/{total}: {title} ", fg="cyan", bold=True) + click.style("─" * 20, fg="bright_black"))


def _ask(prompt: str, default: str = "", required: bool = False, hide: bool = False) -> str:
    while True:
        kwargs: Dict[str, Any] = {"default": default} if default else {}
        if hide:
            kwargs["hide_input"] = True
            # click only shows confirmation when hide_input and prompt asks
        value = click.prompt(prompt, **kwargs)
        value = (value or "").strip()
        if value or not required:
            return value
        _warn("  That field is required — please enter a value.")


def _choose(prompt: str, options: List[Tuple[str, str]], default_index: int = 0) -> str:
    """Present numbered choices; return the option id."""
    _echo(prompt)
    for i, (_id, label) in enumerate(options, 1):
        marker = " (default)" if i - 1 == default_index else ""
        _echo(f"  {i}) {label}{marker}")
    while True:
        raw = click.prompt(
            "  Choice",
            default=str(default_index + 1),
            show_default=True,
        ).strip()
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(options):
                return options[idx - 1][0]
        # allow matching by id substring
        lowered = raw.lower()
        for oid, label in options:
            if lowered == oid or lowered in label.lower():
                return oid
        _warn(f"  Please enter a number from 1 to {len(options)}.")


def _multi_choose(prompt: str, options: List[Tuple[str, str]], max_picks: int = 3) -> List[str]:
    _echo(prompt)
    _dim(f"  Enter numbers separated by commas (up to {max_picks}), e.g. 1,3,5")
    for i, (_id, label) in enumerate(options, 1):
        _echo(f"  {i}) {label}")
    while True:
        raw = click.prompt("  Choices", default="1").strip()
        parts = [p.strip() for p in re.split(r"[,\s]+", raw) if p.strip()]
        picked: List[str] = []
        ok = True
        for p in parts:
            if not p.isdigit() or not (1 <= int(p) <= len(options)):
                ok = False
                break
            oid = options[int(p) - 1][0]
            if oid not in picked:
                picked.append(oid)
        if ok and picked:
            return picked[:max_picks]
        _warn(f"  Please enter 1–{len(options)}, comma-separated.")


def _load_or_create_config() -> Dict[str, Any]:
    path = config_path()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    template = template_path()
    if os.path.isfile(template):
        with open(template, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    return {"agent": True, "channel_type": "web"}


def _save_config(cfg: Dict[str, Any]) -> None:
    path = config_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _mask_key(key: str) -> str:
    if not key or len(key) < 8:
        return "••••"
    return key[:4] + "…" + key[-4:]


def _collect_api_key(cfg: Dict[str, Any], provider: Dict[str, Any]) -> str:
    field = provider["key_field"]
    existing = cfg.get(field, "") or ""
    if existing and not is_placeholder(existing):
        _dim(f"  Existing credential on file: {_mask_key(existing)}")
        if click.confirm("  Keep the existing credential?", default=True):
            return existing
    _dim(f"  {provider.get('hint') or ''}")
    return _ask(f"  Enter API key for {provider['label']}", required=True, hide=True)


def _collect_anthropic_oauth(cfg: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """Import or paste Claude OAuth / setup-token."""
    from common.oauth_credentials import (
        discover_anthropic_oauth_token,
        is_anthropic_oauth_token,
    )

    existing = (
        cfg.get("claude_oauth_token")
        or cfg.get("claude_api_key")
        or ""
    )
    if existing and not is_placeholder(existing) and is_anthropic_oauth_token(str(existing)):
        _dim(f"  Existing Anthropic OAuth token on file: {_mask_key(str(existing))}")
        if click.confirm("  Keep the existing OAuth token?", default=True):
            return str(existing), {}

    discovered = discover_anthropic_oauth_token()
    if discovered:
        _ok(f"  Found Claude OAuth token on this machine: {_mask_key(discovered)}")
        if click.confirm("  Use this Claude login?", default=True):
            return discovered, {}

    _echo()
    _dim("  Anthropic OAuth options:")
    _dim("    1. Install Claude Code, sign in, then run:  claude setup-token")
    _dim("    2. Paste the sk-ant-oat01-… token here")
    _dim(f"  {provider_hint_anthropic()}")
    token = _ask("  Paste Anthropic OAuth / setup-token", required=True, hide=True)
    if not is_anthropic_oauth_token(token):
        _warn(
            "  That does not look like a setup-token (expected sk-ant-oat…). "
            "Saving anyway — Alfr3d will treat oat tokens as OAuth and others as API keys."
        )
    return token, {}


def provider_hint_anthropic() -> str:
    return "Hint: https://code.claude.com  ·  claude setup-token"


def _collect_codex_oauth(cfg: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """Import or paste OpenAI Codex / ChatGPT OAuth access token."""
    from common.oauth_credentials import discover_codex_oauth

    existing = cfg.get("codex_oauth_access_token") or ""
    if existing and not is_placeholder(existing):
        _dim(f"  Existing Codex OAuth token on file: {_mask_key(str(existing))}")
        if click.confirm("  Keep the existing Codex OAuth token?", default=True):
            return str(existing), {
                "refresh_token": cfg.get("codex_oauth_refresh_token"),
                "account_id": cfg.get("codex_oauth_account_id"),
            }

    discovered = discover_codex_oauth()
    if discovered and discovered.get("access_token"):
        src = discovered.get("source") or "local Codex CLI"
        _ok(f"  Found Codex/ChatGPT credentials ({src}): {_mask_key(discovered['access_token'])}")
        if click.confirm("  Use this Codex / ChatGPT login?", default=True):
            return discovered["access_token"], {
                "refresh_token": discovered.get("refresh_token"),
                "account_id": discovered.get("account_id"),
            }

    _echo()
    _dim("  OpenAI Codex OAuth options:")
    _dim("    1. Install Codex CLI, run `codex` and sign in with ChatGPT")
    _dim("    2. Alfr3d will read ~/.codex/auth.json when present")
    _dim("    3. Or paste a Codex / ChatGPT access token below")
    token = _ask("  Paste Codex OAuth access token (or leave empty to re-scan)", default="", hide=True)
    if not token:
        discovered = discover_codex_oauth()
        if not discovered or not discovered.get("access_token"):
            raise click.ClickException(
                "No Codex OAuth credentials found. Sign in with Codex CLI first, "
                "or paste an access token."
            )
        return discovered["access_token"], {
            "refresh_token": discovered.get("refresh_token"),
            "account_id": discovered.get("account_id"),
        }
    return token, {}


def _label_for(options: List[Tuple[str, str]], oid: str) -> str:
    for i, (x, label) in enumerate(options):
        if x == oid:
            return label
    return oid


def _write_user_md(workspace: str, profile: Dict[str, Any]) -> None:
    path = os.path.join(workspace, "USER.md")
    name = profile.get("name") or ""
    preferred = profile.get("preferred_name") or name
    occupation = profile.get("occupation") or ""
    timezone = profile.get("timezone") or ""
    email = profile.get("email") or ""

    content = f"""# USER.md - User basics

*Stable identity from `alfr3d setup`. Dynamic preferences live in MEMORY.md / BUSINESS.md.*

## Basics

- **Name**: {name}
- **Preferred name**: {preferred}
- **Occupation**: {occupation}
- **Timezone**: {timezone}

## Contact

- **Email**: {email}
- **WeChat**:
- **Other**:

## Important dates

- **Birthday**:
- **Anniversary**:

---

**Note**: Updated by Alfr3d setup on {profile.get("setup_completed_at", "")}.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _write_business_md(workspace: str, profile: Dict[str, Any]) -> None:
    path = os.path.join(workspace, "BUSINESS.md")
    status = profile.get("business_status") or ""
    intent = profile.get("business_intent") or ""
    focuses = profile.get("primary_focus") or []
    if isinstance(focuses, str):
        focuses = [focuses]
    industry = profile.get("industry") or ""
    business_name = profile.get("business_name") or ""
    stage_notes = profile.get("stage_notes") or ""
    goals = profile.get("goals") or ""
    why = profile.get("why_alfr3d") or ""

    focus_lines = "\n".join(f"- {_label_for(PRIMARY_FOCUS, f)}" for f in focuses) or "- (not specified)"

    content = f"""# BUSINESS.md - Why this person is here

*Customer profile from `alfr3d setup`. This is durable context for Alfr3d — serve them accordingly.*

## Business status

- **Have they started a business?**: {_label_for(BUSINESS_STATUS, status)}
- **What are they trying to do?**: {_label_for(BUSINESS_INTENT, intent)}
- **Business name**: {business_name or "(not named yet)"}
- **Industry / niche**: {industry or "(not specified)"}

## Primary focus areas

{focus_lines}

## Goals (next 90 days)

{goals or "_(not specified)_"}

## Why they set up Alfr3d

{why or "_(not specified)_"}

## Notes from setup

{stage_notes or "_(none)_"}

## How Alfr3d should help

- Lead with practical, structured advice appropriate to their stage.
- Prefer judgment and next steps over generic lists.
- Protect their time, attention, energy, reputation, and resources.
- Do not assume they have a business if status is not_yet or planning.
- If they are learning, teach clearly; if they are operating, optimize systems.

---

**Note**: Profile captured {profile.get("setup_completed_at", "")}. Re-run `alfr3d setup --force` to update.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _seed_memory(workspace: str, profile: Dict[str, Any]) -> None:
    """Append a short durable memory bullet if MEMORY.md exists or create lean index."""
    path = os.path.join(workspace, "MEMORY.md")
    preferred = profile.get("preferred_name") or profile.get("name") or "the user"
    status = _label_for(BUSINESS_STATUS, profile.get("business_status") or "")
    intent = _label_for(BUSINESS_INTENT, profile.get("business_intent") or "")
    bullet = (
        f"- [{datetime.now(dt_timezone.utc).date().isoformat()}] "
        f"Setup: serving {preferred}. Business status: {status}. Intent: {intent}. "
        f"See BUSINESS.md for full profile."
    )
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = f.read()
        if "See BUSINESS.md for full profile" in existing:
            return
        with open(path, "a", encoding="utf-8") as f:
            if not existing.endswith("\n"):
                f.write("\n")
            f.write("\n## From setup\n\n")
            f.write(bullet + "\n")
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write("# MEMORY.md - Long-term memory index\n\n")
            f.write("## From setup\n\n")
            f.write(bullet + "\n")


def _update_agent_relationship(workspace: str, profile: Dict[str, Any]) -> None:
    """Fill AGENT.md relationship notes when still a template placeholder."""
    path = os.path.join(workspace, "AGENT.md")
    preferred = profile.get("preferred_name") or profile.get("name") or "the user"
    note = (
        f"Serving **{preferred}**. Business context is in BUSINESS.md — "
        f"tailor advice to their stage and intent. Address them as {preferred}."
    )
    if not os.path.isfile(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return

    marker = "## 🤝 Relationship notes for this user"
    if marker in text:
        # Replace the placeholder paragraph after the heading
        pattern = re.compile(
            r"(## 🤝 Relationship notes for this user\n\n)(.*?)(\n\n---|\n---|\Z)",
            re.DOTALL,
        )
        replacement = rf"\1{note}\3"
        new_text, n = pattern.subn(replacement, text, count=1)
        if n:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_text)
            return

    # Chinese heading variant
    marker_zh = "## 🤝 与当前用户的关系备注"
    if marker_zh in text:
        pattern = re.compile(
            r"(## 🤝 与当前用户的关系备注\n\n)(.*?)(\n\n---|\n---|\Z)",
            re.DOTALL,
        )
        replacement = rf"\1{note}\3"
        new_text, n = pattern.subn(replacement, text, count=1)
        if n:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_text)


def _clear_bootstrap(workspace: str) -> None:
    bootstrap = os.path.join(workspace, "BOOTSTRAP.md")
    if os.path.isfile(bootstrap):
        try:
            os.remove(bootstrap)
        except OSError:
            pass


def _ensure_workspace() -> str:
    ensure_sys_path()
    root = get_project_root()
    if root not in sys.path:
        sys.path.insert(0, root)
    # Ensure config is readable by registry via load path
    workspace = get_workspace_dir()
    os.makedirs(workspace, exist_ok=True)
    try:
        from agent.prompt.workspace import ensure_workspace

        ensure_workspace(workspace, create_templates=True)
    except Exception:
        # Templates are best-effort during setup; files we write still land.
        pass
    return workspace


def run_setup(force: bool = False, non_interactive: bool = False) -> int:
    """Run the setup wizard. Returns process exit code."""
    if non_interactive:
        _warn("Non-interactive setup is not supported yet. Run `alfr3d setup` in a terminal.")
        return 2

    if not force and is_setup_complete():
        _ok("Setup is already complete.")
        _dim("  Run `alfr3d setup --force` to update keys or your business profile.")
        _dim("  Or start chatting:  alfr3d chat")
        return 0

    cfg = _load_or_create_config()
    total_steps = 4

    _echo()
    _echo(click.style("  Alfr3d setup", fg="cyan", bold=True) + click.style("  ·  personal steward", fg="bright_black"))
    _dim("  A few calm questions so Alfr3d can serve you properly.")
    _dim("  API keys stay on this machine in config.json. Business context goes into your workspace.")
    _echo()

    # ── Step 1: About you ─────────────────────────────────────────────
    _section(1, total_steps, "About you")
    name = _ask("  What is your name?", required=True)
    preferred = _ask("  What should Alfr3d call you?", default=name.split()[0] if name else name)
    occupation = _ask("  What do you do? (role / occupation, optional)", default="")
    email = _ask("  Email (optional, for your records only)", default="")
    user_timezone = _ask(
        "  Timezone",
        default=os.environ.get("TZ") or "America/Chicago",
    )

    # ── Step 2: Why you're here (business intake) ─────────────────────
    _section(2, total_steps, "Why you're here")
    _dim("  These answers shape how Alfr3d advises you — stage-appropriate, not generic.")

    business_status = _choose(
        "  Have you started a business?",
        BUSINESS_STATUS,
        default_index=0,
    )

    # Intent wording adapts slightly by status
    intent_default = 0
    if business_status.startswith("yes"):
        intent_default = 2  # grow
    elif business_status == "planning":
        intent_default = 1  # launch
    else:
        intent_default = 0  # learn

    business_intent = _choose(
        "  Are you looking to learn how to start, or to build/improve the one you have?",
        BUSINESS_INTENT,
        default_index=intent_default,
    )

    business_name = ""
    if business_status.startswith("yes") or business_intent in ("launch", "grow", "ops", "finance"):
        business_name = _ask("  Business name (if you have one)", default="")

    industry = _ask("  Industry or niche (e.g. HVAC, bookkeeping, SaaS)", default="")

    focuses = _multi_choose(
        "  What do you most want help with right now?",
        PRIMARY_FOCUS,
        max_picks=3,
    )

    goals = _ask(
        "  What would a good next 90 days look like? (one or two sentences)",
        default="",
    )
    why = _ask(
        "  In one sentence: why did you set up Alfr3d today?",
        default="",
    )
    stage_notes = _ask(
        "  Anything else Alfr3d should know about your situation? (optional)",
        default="",
    )

    # ── Step 3: Model / credential ────────────────────────────────────
    _section(3, total_steps, "Model access")
    _dim("  Choose how Alfr3d should authenticate with a model provider.")
    _dim("  API keys bill usage; OAuth reuses Claude Pro/Max or ChatGPT/Codex sign-in.")

    provider_options = [(p["id"], p["label"]) for p in PROVIDERS]
    default_provider_idx = 0  # OpenAI API key
    if has_model_credentials(cfg):
        for i, p in enumerate(PROVIDERS):
            field = p.get("key_field") or ""
            if field and not is_placeholder(cfg.get(field, "")):
                default_provider_idx = i
                break
            if p.get("auth_kind") == "anthropic_oauth" and (
                not is_placeholder(cfg.get("claude_oauth_token", ""))
                or (cfg.get("auth_mode") or "").startswith("anthropic")
            ):
                default_provider_idx = i
                break
            if p.get("auth_kind") == "codex_oauth" and (
                not is_placeholder(cfg.get("codex_oauth_access_token", ""))
                or (cfg.get("auth_mode") or "") in ("codex_oauth", "chatgpt_oauth")
            ):
                default_provider_idx = i
                break

    provider_id = _choose(
        "  Which provider / auth method will Alfr3d use?",
        provider_options,
        default_index=default_provider_idx,
    )
    provider = next(p for p in PROVIDERS if p["id"] == provider_id)
    auth_kind = provider.get("auth_kind") or "api_key"
    api_key = ""
    oauth_extra: Dict[str, Any] = {}

    if auth_kind == "anthropic_oauth":
        api_key, oauth_extra = _collect_anthropic_oauth(cfg)
    elif auth_kind == "codex_oauth":
        api_key, oauth_extra = _collect_codex_oauth(cfg)
    else:
        api_key = _collect_api_key(cfg, provider)

    model = _ask(
        "  Default model name",
        default=str(cfg.get("model") or provider["default_model"]),
    )

    # ── Step 4: Product preferences ───────────────────────────────────
    _section(4, total_steps, "Preferences")
    lang = _choose(
        "  Language for prompts and UI",
        [("auto", "Auto-detect"), ("en", "English"), ("zh", "Chinese")],
        default_index=0 if (cfg.get("alfr3d_lang") or "auto") == "auto" else (1 if cfg.get("alfr3d_lang") == "en" else 2),
    )
    web_password = cfg.get("web_password") or ""
    if click.confirm("  Set a password for the web console? (recommended if you expose it)", default=bool(web_password)):
        web_password = _ask("  Web console password", default=web_password, hide=True)
    else:
        web_password = web_password or ""

    enable_knowledge = click.confirm("  Enable personal knowledge base?", default=cfg.get("knowledge", True) is not False)
    enable_evolution = click.confirm(
        "  Enable self-evolution (learns from idle chats)?",
        default=cfg.get("self_evolution_enabled", True) is not False,
    )

    # ── Persist ───────────────────────────────────────────────────────
    now = datetime.now(dt_timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Persist provider credentials (API key and/or OAuth).
    auth_mode = provider.get("auth_mode") or "api_key"
    cfg["auth_mode"] = auth_mode
    cfg["model"] = model
    if provider.get("bot_type"):
        cfg["bot_type"] = provider["bot_type"]

    if auth_kind == "anthropic_oauth":
        cfg["claude_oauth_token"] = api_key
        cfg["claude_auth_mode"] = "oauth"
        # Also mirror into claude_api_key so older code paths still resolve a credential.
        cfg["claude_api_key"] = api_key
        if provider.get("base_field") and provider.get("default_base"):
            if is_placeholder(cfg.get(provider["base_field"], "")):
                cfg[provider["base_field"]] = provider["default_base"]
    elif auth_kind == "codex_oauth":
        cfg["codex_oauth_access_token"] = api_key
        cfg["openai_auth_mode"] = "codex_oauth"
        # ChatGPT/Codex OAuth access tokens are sent as Bearer like API keys.
        cfg["open_ai_api_key"] = api_key
        if oauth_extra.get("refresh_token"):
            cfg["codex_oauth_refresh_token"] = oauth_extra["refresh_token"]
        if oauth_extra.get("account_id"):
            cfg["codex_oauth_account_id"] = oauth_extra["account_id"]
        if provider.get("base_field") and provider.get("default_base"):
            if is_placeholder(cfg.get(provider["base_field"], "")):
                cfg[provider["base_field"]] = provider["default_base"]
    else:
        cfg[provider["key_field"]] = api_key
        if provider.get("base_field") and provider.get("default_base"):
            if is_placeholder(cfg.get(provider["base_field"], "")):
                cfg[provider["base_field"]] = provider["default_base"]
        # Clear conflicting OAuth-only flags when using a plain API key for these brands.
        if provider["id"] == "claude":
            cfg["claude_auth_mode"] = "api_key"
        if provider["id"] == "openai":
            cfg["openai_auth_mode"] = "api_key"

    cfg["agent"] = True
    cfg["alfr3d_lang"] = lang
    cfg["web_password"] = web_password
    cfg["knowledge"] = enable_knowledge
    cfg["self_evolution_enabled"] = enable_evolution
    if not cfg.get("channel_type"):
        cfg["channel_type"] = "web"

    customer_profile = {
        "name": name,
        "preferred_name": preferred,
        "occupation": occupation,
        "email": email,
        "timezone": user_timezone,
        "business_status": business_status,
        "business_intent": business_intent,
        "business_name": business_name,
        "industry": industry,
        "primary_focus": focuses,
        "goals": goals,
        "why_alfr3d": why,
        "stage_notes": stage_notes,
        "provider": provider_id,
        "auth_mode": auth_mode,
        "setup_completed_at": now,
    }
    cfg["customer_profile"] = customer_profile
    cfg["setup_completed_at"] = now

    _save_config(cfg)
    _ok(f"  Saved credentials and preferences → {config_path()}")

    workspace = _ensure_workspace()
    _write_user_md(workspace, customer_profile)
    _write_business_md(workspace, customer_profile)
    _seed_memory(workspace, customer_profile)
    _update_agent_relationship(workspace, customer_profile)
    _clear_bootstrap(workspace)
    _ok(f"  Saved your profile → {workspace}")
    _dim("    USER.md · BUSINESS.md · MEMORY.md")

    _echo()
    _ok("Setup complete.")
    _echo(f"  Alfr3d will address you as {preferred}.")
    _echo(f"  Focus: {_label_for(BUSINESS_INTENT, business_intent)}")
    _echo()

    # Alfred-style boot sequence after essentials are established.
    try:
        from cli.banner import print_session_line, print_startup_banner

        print_startup_banner()
        print_session_line(
            user_name=preferred,
            model=model,
            mode="Personal Steward",
        )
    except Exception:
        pass

    _echo()
    _echo("  Next:")
    _echo(click.style("    alfr3d chat", fg="green", bold=True) + "                 # talk in the terminal")
    _echo("    alfr3d chat \"What should I do this week?\"")
    _echo("    alfr3d start                 # web console + channels")
    _echo()
    _dim("  Re-run anytime:  alfr3d setup --force")
    _echo()
    return 0


@click.command("setup")
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Re-run setup even if already completed.",
)
@click.option(
    "--no-banner",
    is_flag=True,
    help="Skip the post-setup boot sequence.",
)
def setup(force: bool, no_banner: bool):
    """Interactive setup — API keys, preferences, and why you're here.

    \b
    Alfr3d will ask:
      • who you are
      • whether you have started a business
      • whether you want to learn, launch, or grow
      • what to focus on
      • which model provider and API key to use
    """
    if not click.get_text_stream("stdin").isatty():
        click.echo("Setup requires an interactive terminal. Run: alfr3d setup", err=True)
        raise SystemExit(2)
    if no_banner:
        os.environ["ALFR3D_NO_BANNER"] = "1"
    code = run_setup(force=force)
    raise SystemExit(code)
