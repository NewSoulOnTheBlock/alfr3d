"""Customer-facing terminal chat — full agent harness with immutable SOUL.

Usage:
  alfr3d chat                    # interactive session
  alfr3d chat "your question"    # one-shot
  alfr3d "your question"         # same one-shot (unknown commands route here)

This path does not start the web/IM service. It loads config, boots the Agent
with SOUL.md, and answers in the terminal with streaming tool/reasoning output.
"""

from __future__ import annotations

import os
import sys
import uuid
from typing import Optional

import click

from cli.utils import ensure_sys_path, get_project_root, load_config_json

# Session id shared across REPL turns so memory and conversation persist.
DEFAULT_CLI_SESSION = "cli_chat"


# API-key config fields we accept as "a model is configured".
_MODEL_KEY_FIELDS = (
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


def _echo_err(message: str) -> None:
    # Use stdout so multi-step preflight messages stay in order for customers
    # (mixing stderr/stdout can interleave in terminals and CI captures).
    click.echo(click.style(message, fg="red"))


def _echo_dim(message: str) -> None:
    click.echo(click.style(message, fg="bright_black"))


def _echo_ok(message: str) -> None:
    click.echo(click.style(message, fg="green"))


def _is_placeholder(value: str) -> bool:
    v = (value or "").strip()
    if not v:
        return True
    lowered = v.lower()
    return lowered in {
        "your api key",
        "your_api_key",
        "sk-xxx",
        "xxx",
        "changeme",
        "replace_me",
    }


def _has_model_credentials(cfg: dict) -> bool:
    for key in _MODEL_KEY_FIELDS:
        if not _is_placeholder(str(cfg.get(key, ""))):
            return True
    # Multi custom providers
    for item in cfg.get("custom_providers") or []:
        if isinstance(item, dict) and not _is_placeholder(str(item.get("api_key", ""))):
            return True
    # Env overrides common for customers
    for env_key in (
        "OPENAI_API_KEY",
        "CLAUDE_API_KEY",
        "ANTHROPIC_API_KEY",
        "DEEPSEEK_API_KEY",
        "GEMINI_API_KEY",
    ):
        if not _is_placeholder(os.environ.get(env_key, "")):
            return True
    return False


def _ensure_config_file() -> Optional[str]:
    """Return path to config.json, creating from template when missing.

    Returns None if we cannot create a usable config (customer must intervene).
    """
    root = get_project_root()
    config_path = os.path.join(root, "config.json")
    if os.path.isfile(config_path):
        return config_path

    template = os.path.join(root, "config-template.json")
    if not os.path.isfile(template):
        _echo_err(
            "Alfr3d is not configured.\n"
            f"  Expected config at: {config_path}\n"
            "  config-template.json is also missing from this install."
        )
        return None

    try:
        import shutil

        shutil.copyfile(template, config_path)
        _echo_ok(f"Created config.json from the product template.")
        _echo_dim(f"  Path: {config_path}")
        return config_path
    except OSError as e:
        _echo_err(f"Could not create config.json: {e}")
        return None


def _preflight() -> bool:
    """Customer-facing readiness checks. Return False to abort chat."""
    config_path = _ensure_config_file()
    if not config_path:
        return False

    cfg = load_config_json()
    if not cfg:
        _echo_err(
            "config.json is empty or unreadable.\n"
            "  Add a model API key and set \"model\" / \"bot_type\" as needed."
        )
        return False

    if not _has_model_credentials(cfg):
        model = cfg.get("model") or "(unset)"
        _echo_err(
            "No model API key is configured yet.\n"
            f"  Active model setting: {model}\n"
            "  Open config.json and set the matching key, for example:\n"
            "    • open_ai_api_key     (OpenAI / compatible)\n"
            "    • claude_api_key      (Anthropic)\n"
            "    • deepseek_api_key    (DeepSeek)\n"
            "    • gemini_api_key      (Google)\n"
            "  Then run:  alfr3d chat"
        )
        return False

    if cfg.get("agent") is False:
        _echo_err(
            "Agent mode is turned off in config.json.\n"
            "  Chat requires the full agent harness (tools, memory, SOUL).\n"
            "  Set \"agent\": true and try again."
        )
        return False

    return True


def _silence_console_logging() -> None:
    """Keep the TTY clean for customers; full detail still goes to run.log."""
    import logging

    try:
        from config import conf

        level_name = str(conf().get("terminal_log_level", "ERROR")).upper()
    except Exception:
        level_name = "ERROR"
    level = getattr(logging, level_name, logging.ERROR)
    root_logger = logging.getLogger("log")
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(
            handler, logging.FileHandler
        ):
            handler.setLevel(level)


def _bootstrap_bridge():
    """Load product config and return a ready Bridge (agent-capable)."""
    ensure_sys_path()
    root = get_project_root()
    os.chdir(root)
    if root not in sys.path:
        sys.path.insert(0, root)

    from config import load_config

    load_config()
    _silence_console_logging()

    from bridge.bridge import Bridge

    return Bridge()


def _build_context(session_id: str, request_id: str, on_event):
    from bridge.context import Context, ContextType

    ctx = Context(type=ContextType.TEXT, content="")
    ctx["session_id"] = session_id
    ctx["request_id"] = request_id
    ctx["channel_type"] = "terminal"
    ctx["receiver"] = session_id
    ctx["isgroup"] = False
    ctx["on_event"] = on_event
    return ctx


def _print_banner(session_id: str, model: str) -> None:
    click.echo()
    click.echo(click.style("  Alfr3d", fg="cyan", bold=True) + click.style("  ·  personal steward", fg="bright_black"))
    click.echo(click.style(f"  Model: {model}  ·  Session: {session_id}", fg="bright_black"))
    click.echo(click.style("  Type your message.  /exit to leave  ·  /clear for a fresh thread  ·  /help", fg="bright_black"))
    click.echo()


def _print_repl_help() -> None:
    click.echo(
        "\nCommands:\n"
        "  /exit, /quit, :q     Leave the session\n"
        "  /clear                Start a fresh conversation thread\n"
        "  /help                 Show this help\n"
        "\n"
        "Anything else is sent to Alfr3d.\n"
    )


def _run_turn(bridge, prompt: str, session_id: str, clear_history: bool = False) -> int:
    """Run one agent turn. Returns process exit code (0 ok, 1 error)."""
    from channel.terminal.terminal_channel import TerminalAgentRenderer
    from bridge.reply import ReplyType

    request_id = str(uuid.uuid4())
    renderer = TerminalAgentRenderer()
    context = _build_context(session_id, request_id, renderer.handle_event)

    try:
        reply = bridge.fetch_agent_reply(
            prompt,
            context,
            on_event=renderer.handle_event,
            clear_history=clear_history,
        )
    except KeyboardInterrupt:
        renderer.finish()
        click.echo(click.style("\n⏹  Interrupted.", fg="yellow"))
        return 130
    except Exception as e:
        renderer.finish()
        # Customer-facing: short message, no stack dump.
        _echo_err(f"\nSomething went wrong while Alfr3d was working: {e}")
        _echo_dim("  Details are in run.log in the project directory.")
        return 1
    finally:
        renderer.finish()

    if reply is None:
        _echo_err("No reply was returned.")
        return 1

    # When streaming already painted the answer, avoid duplicating it.
    if not renderer._has_output:
        content = reply.content if reply.content is not None else ""
        if reply.type == ReplyType.ERROR:
            _echo_err(str(content))
            return 1
        if content:
            click.echo()
            click.echo(click.style("Alfr3d: ", fg="green", bold=True) + str(content))
            click.echo()
    else:
        click.echo()

    if reply.type == ReplyType.ERROR:
        return 1
    return 0


def run_chat(prompt: Optional[str] = None, session_id: Optional[str] = None) -> int:
    """Programmatic entry used by tests and the click command.

    Returns a process exit code.
    """
    if not _preflight():
        return 2

    session_id = (session_id or os.environ.get("ALFR3D_SESSION") or DEFAULT_CLI_SESSION).strip()
    try:
        bridge = _bootstrap_bridge()
    except Exception as e:
        _echo_err(f"Could not start Alfr3d: {e}")
        _echo_dim("  Check config.json and that dependencies are installed (pip install -r requirements.txt).")
        return 1

    from config import conf

    model = conf().get("model") or "default"

    # One-shot
    if prompt is not None and str(prompt).strip():
        if sys.stdout.isatty():
            _echo_dim(f"Alfr3d · {model}")
        return _run_turn(bridge, str(prompt).strip(), session_id)

    # Interactive REPL
    if not sys.stdin.isatty():
        # Piped input: read all, one shot
        data = sys.stdin.read().strip()
        if not data:
            _echo_err("No input provided.")
            return 2
        return _run_turn(bridge, data, session_id)

    _print_banner(session_id, model)
    clear_next = False
    while True:
        try:
            click.echo(click.style("You: ", fg="blue", bold=True), nl=False)
            line = input()
        except (EOFError, KeyboardInterrupt):
            click.echo()
            _echo_dim("Goodbye.")
            return 0

        text = (line or "").strip()
        if not text:
            continue

        lowered = text.lower()
        if lowered in {"/exit", "/quit", ":q", "exit", "quit"}:
            _echo_dim("Goodbye.")
            return 0
        if lowered in {"/help", "help"}:
            _print_repl_help()
            continue
        if lowered in {"/clear", "clear"}:
            clear_next = True
            _echo_dim("Next message starts a fresh thread.")
            continue

        code = _run_turn(bridge, text, session_id, clear_history=clear_next)
        clear_next = False
        # Non-fatal turn errors keep the REPL open for customers.
        if code not in (0, 130):
            _echo_dim("You can try again, or /exit to leave.")
        if code == 130:
            _echo_dim("Session still open — send another message or /exit.")


@click.command("chat")
@click.argument("prompt", nargs=-1, required=False)
@click.option(
    "--session",
    "-s",
    "session_id",
    default=None,
    help="Conversation session id (default: cli_chat, or ALFR3D_SESSION).",
)
def chat(prompt, session_id):
    """Talk to Alfr3d in the terminal (full agent + SOUL).

    \b
    Examples:
      alfr3d chat
      alfr3d chat "Summarize what I should do this week"
      alfr3d "What is a DUNS number?"
    """
    message = " ".join(prompt).strip() if prompt else None
    code = run_chat(prompt=message or None, session_id=session_id)
    sys.exit(code)
