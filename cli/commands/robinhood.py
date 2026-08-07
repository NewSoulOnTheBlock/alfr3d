"""alfr3d robinhood - Connect ALFR3D to the Robinhood Trading MCP.

Turnkey setup for end users: writes/merges the Robinhood server entry into the
agent's ``mcp.json`` (preserving any other servers), optionally sets the OAuth
callback base for server deployments, and prints the remaining human step
(the Robinhood OAuth login, which cannot be automated).
"""

import json
import os

import click

ROBINHOOD_SERVER_NAME = "robinhood"
ROBINHOOD_MCP_URL = "https://agent.robinhood.com/mcp/trading"


# ---------------------------------------------------------------------------
# Path resolution (matches how the running app resolves these files)
# ---------------------------------------------------------------------------

def _mcp_config_path() -> str:
    """Path to the agent's mcp.json, resolved the same way the app does.

    Falls back to ~/alfr3d/mcp.json if the registry can't be loaded (e.g. no
    config yet), so ``connect`` still works on a fresh install.
    """
    try:
        from cli.utils import get_workspace_dir
        from common import state_dir
        return str(state_dir.mcp_config_file(base=get_workspace_dir()))
    except Exception:
        return os.path.join(os.path.expanduser("~/alfr3d"), "mcp.json")


def _config_json_path() -> str:
    """Path to config.json, matching config.get_data_root() resolution."""
    from cli.utils import get_project_root
    data_dir = os.environ.get("ALFR3D_DATA_DIR")
    root = os.path.expanduser(data_dir) if data_dir else get_project_root()
    return os.path.join(root, "config.json")


def _oauth_token_path() -> str:
    return os.path.join(os.path.expanduser("~/.alfr3d"), "mcp_oauth.json")


def _read_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _ensure_utf8_output() -> None:
    """Make emoji/checkmarks safe on non-UTF-8 consoles (e.g. Windows cp1252).

    No-op where stdout is already UTF-8 (the Docker/Linux default). Uses
    errors="replace" so output degrades gracefully rather than crashing.
    """
    import sys
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def _t():
    """Return the i18n translator, bootstrapping sys.path/language first."""
    _ensure_utf8_output()
    from cli.utils import get_cli_language
    get_cli_language()
    from common import i18n
    return i18n.t


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@click.group(name="robinhood", invoke_without_command=True)
@click.pass_context
def robinhood(ctx):
    """Connect ALFR3D to the Robinhood Trading MCP."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@robinhood.command()
@click.option(
    "--redirect-base",
    default=None,
    metavar="URL",
    help="OAuth callback base for server deploys, e.g. http://YOUR_IP:9899. "
         "Sets mcp_oauth_redirect_base in config.json.",
)
def connect(redirect_base):
    """Add the Robinhood MCP server and print the login step."""
    t = _t()

    mcp_path = _mcp_config_path()
    cfg = _read_json(mcp_path)
    servers = cfg.get("mcpServers")
    if not isinstance(servers, dict):
        servers = {}
        cfg["mcpServers"] = servers

    existing = servers.get(ROBINHOOD_SERVER_NAME)
    entry = {"type": "streamable-http", "url": ROBINHOOD_MCP_URL}
    if existing == entry:
        click.echo(click.style(
            t("✅ Robinhood MCP 已配置（未改动）：{}", "✅ Robinhood MCP already configured (no change): {}").format(mcp_path),
            fg="green",
        ))
    else:
        servers[ROBINHOOD_SERVER_NAME] = entry
        _write_json(mcp_path, cfg)
        click.echo(click.style(
            t("✅ 已写入 Robinhood MCP 配置：{}", "✅ Wrote Robinhood MCP config: {}").format(mcp_path),
            fg="green",
        ))

    if redirect_base:
        config_path = _config_json_path()
        app_cfg = _read_json(config_path)
        app_cfg["mcp_oauth_redirect_base"] = redirect_base.rstrip("/")
        _write_json(config_path, app_cfg)
        click.echo(click.style(
            t("✅ 已设置 mcp_oauth_redirect_base = {}", "✅ Set mcp_oauth_redirect_base = {}").format(redirect_base.rstrip("/")),
            fg="green",
        ))

    click.echo("")
    click.echo(t("下一步（需要你在浏览器中完成）：", "Next steps (you complete these in a browser):"))
    click.echo(t(
        "  1. 确保已开通 Robinhood 智能体交易并已向专用 Agentic 账户注资。",
        "  1. Enable Robinhood agentic trading and fund the dedicated Agentic account.",
    ))
    click.echo(t(
        "  2. 重启 ALFR3D：alfr3d restart",
        "  2. Restart ALFR3D:  alfr3d restart",
    ))
    click.echo(t(
        "  3. 在日志中找到授权链接：alfr3d logs   （或 docker compose logs -f | grep -i mcp）",
        "  3. Find the authorization link in the logs:  alfr3d logs   (or: docker compose logs -f | grep -i mcp)",
    ))
    click.echo(t(
        "  4. 在浏览器打开该链接，登录 Robinhood 并授权 Agentic 账户。",
        "  4. Open that link, log into Robinhood, and approve the Agentic account.",
    ))
    click.echo(t(
        "  5. 验证（只读）：让 ALFR3D “列出我的账户和投资组合价值”。",
        "  5. Verify (read-only): ask ALFR3D to \"list my accounts and portfolio value\".",
    ))
    if not redirect_base:
        click.echo("")
        click.echo(click.style(t(
            "提示：服务器部署请加 --redirect-base http://你的IP:9899 并开放 9899 端口。",
            "Tip: for server deploys, re-run with --redirect-base http://YOUR_IP:9899 and open port 9899.",
        ), fg="yellow"))


@robinhood.command()
def status():
    """Show whether Robinhood MCP is configured and authorized."""
    t = _t()

    mcp_path = _mcp_config_path()
    servers = _read_json(mcp_path).get("mcpServers", {})
    configured = isinstance(servers, dict) and ROBINHOOD_SERVER_NAME in servers

    tokens = _read_json(_oauth_token_path())
    authorized = isinstance(tokens, dict) and ROBINHOOD_SERVER_NAME in tokens

    redirect_base = _read_json(_config_json_path()).get("mcp_oauth_redirect_base") or t("(未设置)", "(not set)")

    def mark(ok):
        return click.style("✔", fg="green") if ok else click.style("✖", fg="red")

    click.echo(f"{mark(configured)} " + t("已配置 (mcp.json): {}", "Configured (mcp.json): {}").format(mcp_path if configured else t("否", "no")))
    click.echo(f"{mark(authorized)} " + t("已授权 (OAuth token): {}", "Authorized (OAuth token): {}").format(
        t("是", "yes") if authorized else t("否 — 重启后在日志中打开授权链接", "no — restart, then open the auth link from the logs")))
    click.echo("  " + t("OAuth 回调地址 (mcp_oauth_redirect_base): {}", "OAuth callback base (mcp_oauth_redirect_base): {}").format(redirect_base))
    if not configured:
        click.echo("")
        click.echo(t("运行 `alfr3d robinhood connect` 开始配置。", "Run `alfr3d robinhood connect` to set it up."))


@robinhood.command()
def disconnect():
    """Remove the Robinhood MCP server from mcp.json."""
    t = _t()

    mcp_path = _mcp_config_path()
    cfg = _read_json(mcp_path)
    servers = cfg.get("mcpServers", {})
    if not isinstance(servers, dict) or ROBINHOOD_SERVER_NAME not in servers:
        click.echo(t("Robinhood MCP 未配置，无需移除。", "Robinhood MCP is not configured; nothing to remove."))
        return

    servers.pop(ROBINHOOD_SERVER_NAME, None)
    _write_json(mcp_path, cfg)
    click.echo(click.style(t("✅ 已从 mcp.json 移除 Robinhood MCP。", "✅ Removed Robinhood MCP from mcp.json."), fg="green"))
    click.echo(click.style(t(
        "注意：这不会撤销 Robinhood 端的授权。请在 Robinhood 账户设置中撤销访问权限，"
        "并按需删除 ~/.alfr3d/mcp_oauth.json 中的 robinhood 令牌。",
        "Note: this does not revoke access on Robinhood's side. Revoke access in your "
        "Robinhood account settings, and optionally delete the robinhood token from ~/.alfr3d/mcp_oauth.json.",
    ), fg="yellow"))
