"""alfr3d quickbooks - Connect ALFR3D to the QuickBooks Online MCP for bookkeeping.

The QuickBooks Online MCP server (@qboapi/qbo-mcp-server) is a Node/ESM server
that speaks MCP over **stdio**, so it must be built into the image
(`--build-arg INSTALL_QUICKBOOKS=true`). It authenticates to Intuit itself using
credentials in a **.env file resolved relative to the built module**, and it
rotates the refresh token back into that .env. So this command keeps the real
.env on the mounted volume (survives restarts) and symlinks it into the server
directory, rather than passing secrets through mcp.json (which would go stale
after the first token rotation).
"""

import json
import os
import posixpath

import click

QUICKBOOKS_SERVER_NAME = "quickbooks"
REQUIRED_ENV_KEYS = (
    "QUICKBOOKS_CLIENT_ID",
    "QUICKBOOKS_CLIENT_SECRET",
    "QUICKBOOKS_REFRESH_TOKEN",
    "QUICKBOOKS_REALM_ID",
    "QUICKBOOKS_ENVIRONMENT",
)


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def _server_home() -> str:
    return os.environ.get("QUICKBOOKS_MCP_HOME") or "/opt/quickbooks-mcp"


def _server_entry() -> str:
    # POSIX path: this is written into mcp.json and run by `node` inside the
    # Linux container, so it must use forward slashes even if `connect` is
    # invoked from a Windows shell.
    return posixpath.join(_server_home(), "dist", "index.js")


def _workspace_dir() -> str:
    """Agent workspace (the mounted volume under Docker); where the .env persists."""
    try:
        from cli.utils import get_workspace_dir
        return get_workspace_dir()
    except Exception:
        return os.path.expanduser("~/alfr3d")


def _persisted_env_path() -> str:
    return os.path.join(_workspace_dir(), "quickbooks.env")


def _mcp_config_path() -> str:
    try:
        from common import state_dir
        return str(state_dir.mcp_config_file(base=_workspace_dir()))
    except Exception:
        return os.path.join(_workspace_dir(), "mcp.json")


def _config_json_path() -> str:
    from cli.utils import get_project_root
    data_dir = os.environ.get("ALFR3D_DATA_DIR")
    root = os.path.expanduser(data_dir) if data_dir else get_project_root()
    return os.path.join(root, "config.json")


# ---------------------------------------------------------------------------
# Small IO helpers
# ---------------------------------------------------------------------------

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


def _parse_env_file(path: str) -> dict:
    result = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip().strip('"').strip("'")
    return result


def _write_env_file(path: str, values: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    lines = [f"{k}={v}" for k, v in values.items()]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    try:
        os.chmod(path, 0o600)  # secrets — restrict to owner
    except OSError:
        pass


def _link_env_into_server(persisted: str) -> list:
    """Symlink the server's expected .env locations to the persisted file.

    The compiled server resolves .env relative to itself; we cover both the
    package root and dist/ so token rotation writes through to the volume.
    Returns a list of human-readable notes about what happened.
    """
    notes = []
    home = _server_home()
    for target in (posixpath.join(home, ".env"), posixpath.join(home, "dist", ".env")):
        try:
            parent = os.path.dirname(target)
            if not os.path.isdir(parent):
                notes.append(f"skip {target} (server not built here)")
                continue
            if os.path.islink(target) or os.path.exists(target):
                os.remove(target)
            os.symlink(persisted, target)
            notes.append(f"linked {target} -> {persisted}")
        except OSError as e:
            notes.append(f"could not link {target}: {e}")
    return notes


def _ensure_utf8_output() -> None:
    import sys
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def _t():
    _ensure_utf8_output()
    from cli.utils import get_cli_language
    get_cli_language()
    from common import i18n
    return i18n.t


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@click.group(name="quickbooks", invoke_without_command=True)
@click.pass_context
def quickbooks(ctx):
    """Connect ALFR3D to the QuickBooks Online MCP for bookkeeping."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@quickbooks.command()
@click.option("--env-file", "env_file", default=None, metavar="PATH",
              help="Path to a .env produced by the server's `npm run auth` handshake. "
                   "If given, its values are used directly.")
@click.option("--client-id", default=None, help="QUICKBOOKS_CLIENT_ID (Intuit app).")
@click.option("--client-secret", default=None, help="QUICKBOOKS_CLIENT_SECRET (Intuit app).")
@click.option("--realm-id", default=None, help="QUICKBOOKS_REALM_ID (company id).")
@click.option("--refresh-token", default=None, help="QUICKBOOKS_REFRESH_TOKEN (from the OAuth handshake).")
@click.option("--environment", type=click.Choice(["production", "sandbox"]), default="production",
              show_default=True, help="QUICKBOOKS_ENVIRONMENT.")
def connect(env_file, client_id, client_secret, realm_id, refresh_token, environment):
    """Configure the QuickBooks MCP server and store its credentials."""
    t = _t()

    # 1. Resolve credentials (from --env-file, or the individual flags).
    if env_file:
        if not os.path.exists(env_file):
            click.echo(click.style(t("找不到 env 文件：{}", "env file not found: {}").format(env_file), fg="red"))
            raise SystemExit(1)
        values = _parse_env_file(env_file)
        values.setdefault("QUICKBOOKS_ENVIRONMENT", environment)
    else:
        missing = [n for n, v in [
            ("--client-id", client_id), ("--client-secret", client_secret),
            ("--realm-id", realm_id), ("--refresh-token", refresh_token),
        ] if not v]
        if missing:
            click.echo(click.style(t(
                "缺少凭据参数：{}（或改用 --env-file）",
                "Missing credential options: {} (or use --env-file instead)",
            ).format(", ".join(missing)), fg="red"))
            raise SystemExit(1)
        values = {
            "QUICKBOOKS_CLIENT_ID": client_id,
            "QUICKBOOKS_CLIENT_SECRET": client_secret,
            "QUICKBOOKS_REFRESH_TOKEN": refresh_token,
            "QUICKBOOKS_REALM_ID": realm_id,
            "QUICKBOOKS_ENVIRONMENT": environment,
        }

    missing_keys = [k for k in REQUIRED_ENV_KEYS if not values.get(k)]
    if missing_keys:
        click.echo(click.style(t(
            "凭据不完整，缺少：{}", "Incomplete credentials, missing: {}",
        ).format(", ".join(missing_keys)), fg="red"))
        raise SystemExit(1)

    # 2. Persist the .env on the mounted volume (survives restarts + token rotation).
    persisted = _persisted_env_path()
    _write_env_file(persisted, values)
    click.echo(click.style(t("✅ 已写入凭据：{}", "✅ Wrote credentials: {}").format(persisted), fg="green"))

    # 3. Symlink it into the server's expected .env location(s).
    for note in _link_env_into_server(persisted):
        click.echo(f"   {note}")

    # 4. Merge the stdio server entry into mcp.json (no secrets here — the .env owns them).
    mcp_path = _mcp_config_path()
    cfg = _read_json(mcp_path)
    servers = cfg.get("mcpServers")
    if not isinstance(servers, dict):
        servers = {}
        cfg["mcpServers"] = servers
    servers[QUICKBOOKS_SERVER_NAME] = {"command": "node", "args": [_server_entry()]}
    _write_json(mcp_path, cfg)
    click.echo(click.style(t("✅ 已写入 MCP 配置：{}", "✅ Wrote MCP config: {}").format(mcp_path), fg="green"))

    # 5. Enable on-demand MCP tool retrieval — the QB server exposes 144 tools.
    config_path = _config_json_path()
    app_cfg = _read_json(config_path)
    if not app_cfg.get("mcp_tool_retrieval_enabled"):
        app_cfg["mcp_tool_retrieval_enabled"] = True
        _write_json(config_path, app_cfg)
        click.echo(click.style(t(
            "✅ 已开启 mcp_tool_retrieval_enabled（QuickBooks 有 144 个工具）",
            "✅ Enabled mcp_tool_retrieval_enabled (QuickBooks exposes 144 tools)",
        ), fg="green"))

    # 6. Warn if the server binary isn't present (image built without INSTALL_QUICKBOOKS).
    if not os.path.exists(_server_entry()):
        click.echo("")
        click.echo(click.style(t(
            "⚠️ 未找到已构建的服务器：{}\n"
            "   请用 --build-arg INSTALL_QUICKBOOKS=true 重新构建镜像。",
            "⚠️ Built server not found at: {}\n"
            "   Rebuild the image with --build-arg INSTALL_QUICKBOOKS=true.",
        ).format(_server_entry()), fg="yellow"))

    click.echo("")
    click.echo(click.style(t(
        "⚠️ 完整读/写/删除已启用：ALFR3D 可以在真实账套中创建、修改、删除记录。删除不可逆——请谨慎。",
        "⚠️ Full read/write/DELETE is enabled: ALFR3D can create, edit, and DELETE records "
        "in real books. Deletes are irreversible — use with care.",
    ), fg="yellow"))
    click.echo(t("重启后生效：alfr3d restart", "Restart to apply:  alfr3d restart"))
    click.echo(t("查看状态：alfr3d quickbooks status", "Check status:  alfr3d quickbooks status"))


@quickbooks.command()
def status():
    """Show QuickBooks MCP configuration and readiness."""
    t = _t()
    import sys

    mcp_path = _mcp_config_path()
    servers = _read_json(mcp_path).get("mcpServers", {})
    configured = isinstance(servers, dict) and QUICKBOOKS_SERVER_NAME in servers

    env_present = os.path.exists(_persisted_env_path())
    server_built = os.path.exists(_server_entry())
    retrieval_on = bool(_read_json(_config_json_path()).get("mcp_tool_retrieval_enabled"))

    env_mode = "-"
    if env_present:
        try:
            env_mode = _parse_env_file(_persisted_env_path()).get("QUICKBOOKS_ENVIRONMENT", "-")
        except Exception:
            env_mode = "-"

    def mark(ok):
        return click.style("✔", fg="green") if ok else click.style("✖", fg="red")

    click.echo(f"{mark(configured)} " + t("已配置 (mcp.json): {}", "Configured (mcp.json): {}").format(mcp_path if configured else t("否", "no")))
    click.echo(f"{mark(env_present)} " + t("凭据 (.env): {}", "Credentials (.env): {}").format(_persisted_env_path() if env_present else t("否", "no")))
    click.echo(f"{mark(server_built)} " + t("服务器已构建: {}", "Server built: {}").format(_server_entry() if server_built else t("否 — 用 INSTALL_QUICKBOOKS=true 重建镜像", "no — rebuild image with INSTALL_QUICKBOOKS=true")))
    click.echo(f"{mark(retrieval_on)} " + t("按需工具检索: {}", "On-demand tool retrieval: {}").format(t("已开启", "on") if retrieval_on else t("关闭", "off")))
    click.echo("  " + t("环境: {}", "Environment: {}").format(env_mode))
    if not configured:
        click.echo("")
        click.echo(t("运行 `alfr3d quickbooks connect` 开始配置。", "Run `alfr3d quickbooks connect` to set it up."))


@quickbooks.command()
def disconnect():
    """Remove the QuickBooks MCP server from mcp.json."""
    t = _t()

    mcp_path = _mcp_config_path()
    cfg = _read_json(mcp_path)
    servers = cfg.get("mcpServers", {})
    if not isinstance(servers, dict) or QUICKBOOKS_SERVER_NAME not in servers:
        click.echo(t("QuickBooks MCP 未配置，无需移除。", "QuickBooks MCP is not configured; nothing to remove."))
        return

    servers.pop(QUICKBOOKS_SERVER_NAME, None)
    _write_json(mcp_path, cfg)
    click.echo(click.style(t("✅ 已从 mcp.json 移除 QuickBooks MCP。", "✅ Removed QuickBooks MCP from mcp.json."), fg="green"))
    click.echo(click.style(t(
        "注意：凭据文件 {} 仍保留。如需彻底断开，请删除该文件，并在 Intuit 开发者后台撤销应用授权。",
        "Note: the credentials file {} is left in place. To fully disconnect, delete it "
        "and revoke the app's access in the Intuit developer portal.",
    ).format(_persisted_env_path()), fg="yellow"))
