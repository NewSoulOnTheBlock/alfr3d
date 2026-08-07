# Robinhood Trading MCP Integration for ALFR3D — Design Spec

- **Date:** 2026-08-07
- **Status:** Approved (design); ready for implementation planning
- **Repo:** `NewSoulOnTheBlock/alfr3d`, branch `feature/robinhood-mcp`
- **Author:** brainstormed with the operator (`kelby`)

## 1. Goal

Give ALFR3D the ability to connect to and autonomously use the Robinhood
Trading MCP server at `https://agent.robinhood.com/mcp/trading`. The instance
runs under Docker on a remote server. The integration ships as a **reusable repo
capability** (committed example config, an agent skill, and operator docs), not
just a one-off local config.

**One-line definition of done:** *ALFR3D, running on the server, connects to the
Robinhood MCP after the operator completes the OAuth login, and can invoke the
Robinhood tools (a read-only tool is used to prove connectivity).* 

## 2. Trade-execution posture (decided)

**Full autonomous.** All Robinhood tools — including `place_equity_order` and
`cancel_equity_order` — are exposed flat to the model with **no confirmation
gate**. The model may place and cancel real orders on its own.

**Accepted risk & backstop:** With no gate, ALFR3D can execute a buy/sell from
model output alone (including a wrong ticker or quantity). The blast radius is
bounded by **Robinhood's own design**: agent trades are confined to a dedicated,
separately-funded "Agentic account"; all other Robinhood accounts remain
read-only to the agent. Risk is therefore limited to what the operator funds into
that account.

This posture was chosen deliberately over the two safer alternatives that were
offered (read-only, and hard-gated execution). A future gate remains cheap to add
(§7).

## 3. What the Robinhood MCP exposes

Authoritative list is obtained from a `tools/list` call after OAuth; the expected
surface (Robinhood agentic-trading beta) is:

**Read-only (portfolio & market data):**
- `get_accounts` — list Robinhood accounts
- `get_portfolio` — portfolio value / balances
- `get_equity_positions` — current stock holdings
- `get_equity_quotes` — live quotes for symbols
- `get_equity_orders` — order history
- `search` — symbol/ticker lookup
- watchlist read/management

**Trade execution:**
- `review_equity_order` — simulates an order and returns pre-trade warnings (no execution)
- `place_equity_order` — places a real buy/sell
- `cancel_equity_order` — cancels an open order

**Constraints (Robinhood-imposed):**
- Equities only during beta (options rolling out).
- Only the dedicated Agentic account is tradable; other accounts are read-only.
- OAuth-authenticated. Recommended sequence: `review_equity_order` → human review → `place_equity_order`.

## 4. Architecture (what the codebase already provides)

alfr3d already has a complete MCP subsystem, so **connecting requires no new
connection code**:

- **Config-driven loading:** alfr3d reads `~/alfr3d/mcp.json` (Claude-Desktop /
  Cursor-compatible format) at startup; missing file = no MCP tools, no error.
  (`docs/tools/mcp.mdx`.)
- **Remote transport:** `type: "streamable-http"` + `url` is supported.
- **Built-in OAuth:** on a `401`, alfr3d starts a standard OAuth flow
  automatically — server deployments **print the authorization link to the log**;
  tokens persist in `~/.alfr3d/mcp_oauth.json` and refresh on expiry.
  (`agent/tools/mcp/mcp_oauth.py`.)
- **Single execution choke point:** every MCP tool call flows through
  `MCPClient.call_tool()` (`agent/tools/mcp/mcp_client.py:175`) via a `tools/call`
  JSON-RPC request. (Relevant only for the future gate in §7.)
- **Precedent for config-driven safety controls:** `mcp_stdio_command_allowlist`
  in `mcp_client.py` shows the existing pattern a future gate would mirror.

## 5. Deliverables

### 5.1 Connection config (committed example)
An example file `mcp.robinhood.example.json` at the repo root (and an equivalent
snippet in the docs) that the operator merges into their host `./alfr3d/mcp.json`:

```json
{
  "mcpServers": {
    "robinhood": {
      "type": "streamable-http",
      "url": "https://agent.robinhood.com/mcp/trading"
    }
  }
}
```

If Robinhood's OAuth requires an explicit `scope`, add the `scope` field
(discovered at first authorization). The live `~/alfr3d/mcp.json` is operator
runtime config and is **not** committed.

### 5.2 Agent skill — `skills/robinhood-trading/SKILL.md`
Standard skill format (`name`, `description`, body). Teaches ALFR3D:
- The available Robinhood tools and when to use each.
- Robinhood's constraints (equities-only beta; only the Agentic account is
  tradable; other accounts read-only).
- The `review_equity_order → place_equity_order` best-practice sequence as
  guidance (not enforced, per the autonomous posture).
- Example flows: check portfolio, pull a quote, review then place an order,
  cancel an open order.

The skill `description` triggers on trading/portfolio/stock intents.

### 5.3 Operator docs — `docs/tools/robinhood.mdx`
Registered in `docs/docs.json` navigation. Covers:
- Prerequisite: enable Robinhood agentic trading + fund the Agentic account.
- Add the `mcp.json` entry.
- Server OAuth: set `mcp_oauth_redirect_base` in `config.json`
  (e.g. `http://YOUR_IP:9899`), open port `9899`, keep the web console running,
  open the logged authorization link, approve in browser.
- Persisting tokens across restarts (mount for `~/.alfr3d/`).
- Verifying with a read-only tool.
- A safety note describing the autonomous posture and how to add a gate later.

## 6. OAuth flow (server deploy) & division of labor

1. Operator sets `mcp_oauth_redirect_base` and ensures port `9899` is reachable.
2. alfr3d loads the `robinhood` server → RH returns `401` → alfr3d prints the
   authorization link to the Docker logs.
3. **Operator** opens the link, logs into Robinhood, approves the Agentic-account
   scope. Tokens are written to `~/.alfr3d/mcp_oauth.json`; the server comes online.

**Division of labor:** the build and documentation are automatable; the Robinhood
OAuth login is **operator-performed**. The assistant will not enter financial
credentials or authenticate on the operator's behalf, and will not execute
`place_equity_order` as a verification step.

## 7. Future gate (documented, not built)

If per-order confirmation is later desired, insert it at
`MCPClient.call_tool()` (`mcp_client.py:175`): intercept a configurable set of
tool names (e.g. `place_equity_order`, `cancel_equity_order`) and require an
explicit operator confirmation before issuing `tools/call`. Drive it from a
`config.json` flag (e.g. `mcp_tool_confirm` / `mcp_tool_blocklist`) that mirrors
the existing `mcp_stdio_command_allowlist` pattern. Not implemented now.

## 8. Verification / success criteria

In order:
1. **Config parses:** the example config is valid JSON and matches the documented
   `mcp.json` schema (unit-level check, no network).
2. **Docs registered:** `robinhood.mdx` is present and referenced in `docs.json`.
3. **Skill loads:** `skills/robinhood-trading/SKILL.md` has valid frontmatter and
   is discoverable by the skill loader.
4. **Server connects (operator-gated):** after the operator's OAuth login,
   `[MCP] Server 'robinhood'` loads and its tools are retrieved.
5. **Read-only proof:** a read-only tool (e.g. `get_accounts` or
   `get_equity_quotes`) returns a real response. **No trade is placed.**

## 9. Risks & tradeoffs

- **Autonomous execution risk:** model can place/cancel real trades unprompted.
  Mitigated only by Robinhood's separate-funded Agentic account and the operator's
  funding discipline. Future gate (§7) is the escape hatch.
- **OAuth on a remote server:** requires correct `mcp_oauth_redirect_base`, an
  open port `9899`, and a persisted `~/.alfr3d/` volume, or tokens are lost on
  restart and re-auth is needed.
- **Beta API drift:** the Robinhood tool surface is beta (options rolling out);
  tool names/params may change. The skill/docs may need updates; the connection
  config should not.
- **Scope unknowns:** if RH requires a specific OAuth `scope`, first-auth will
  reveal it; the config gains a `scope` field.

## Appendix — Sources

- Robinhood agentic trading: https://robinhood.com/us/en/agentic-trading/
- Robinhood newsroom (open to agents): https://robinhood.com/us/en/newsroom/robinhood-is-now-open-to-agents/
- alfr3d MCP docs: `docs/tools/mcp.mdx`
- MCP execution choke point: `agent/tools/mcp/mcp_client.py:175`
