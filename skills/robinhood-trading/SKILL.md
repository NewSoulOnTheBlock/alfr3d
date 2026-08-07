---
name: robinhood-trading
description: Trade equities and read portfolio/market data on Robinhood via the Robinhood Trading MCP. Use when the user asks to buy or sell a stock, place/cancel an order, check positions, balances, portfolio value, order history, or get a live stock quote.
---

# Robinhood Trading

ALFR3D can act on the user's Robinhood account through the **Robinhood Trading MCP**
(`https://agent.robinhood.com/mcp/trading`). When that MCP server is connected,
its tools appear as normal tools and you invoke them directly.

> **Requires:** the `robinhood` MCP server configured in `~/alfr3d/mcp.json` and
> authorized via OAuth. If the tools below are not available, the server is not
> connected — set it up with `alfr3d robinhood connect` (see
> `docs/tools/robinhood.mdx`). Do not fabricate results.

## Hard constraints (Robinhood-imposed)

These are enforced by Robinhood, not by you — respect them so you don't attempt
impossible actions:

- **Equities only** during the current beta (options are rolling out separately).
- **Only the dedicated "Agentic" account is tradable.** All other Robinhood
  accounts are **read-only** to the agent. Order-placing tools will only succeed
  against the Agentic account.
- Trading is bounded by whatever the user has funded into that Agentic account.

## Tools

**Read-only (safe — use freely):**

| Tool | Purpose |
| --- | --- |
| `get_accounts` | List the user's Robinhood accounts (identify the Agentic account). |
| `get_portfolio` | Portfolio value and balances. |
| `get_equity_positions` | Current stock holdings. |
| `get_equity_quotes` | Live quotes for one or more symbols. |
| `get_equity_orders` | Order history / status. |
| `search` | Look up a symbol/ticker. |

**Trade execution (real money — see the sequence below):**

| Tool | Purpose |
| --- | --- |
| `review_equity_order` | **Simulate** an order and return pre-trade warnings. Does not execute. |
| `place_equity_order` | **Places a real buy/sell** in the Agentic account. |
| `cancel_equity_order` | Cancels an open order. |

## How to trade well

Even though execution is not gated, follow this sequence — it is the pattern
Robinhood designed the tools around and it protects the user from mistakes:

1. **Confirm intent.** Restate the order in plain language: side (buy/sell),
   symbol, quantity (or dollar amount), and order type. Resolve the symbol with
   `search` if there is any ambiguity.
2. **Quote it.** Use `get_equity_quotes` so the user sees the current price and
   the approximate cost/proceeds.
3. **Review before placing.** Call `review_equity_order` and **show the user the
   simulation result and any warnings** before executing.
4. **Place it.** Call `place_equity_order` only for the exact reviewed order.
   Never round, guess, or "helpfully" adjust quantity or symbol.
5. **Confirm the result.** Report the order id/status; use `get_equity_orders` to
   verify.

**Guardrails for your own behavior:**

- Never invent tickers, prices, quantities, or order ids. If a value is unknown,
  look it up or ask.
- If the user's instruction is ambiguous (which account, how many shares, market
  vs limit), ask one clarifying question rather than assuming.
- Do not place a trade the user did not explicitly ask for. "Check my portfolio"
  is a read request, not permission to trade.
- You are not a licensed financial advisor. You may present data and execute what
  the user asks; do not give personalized investment recommendations.

## Example flows

**Check holdings:**
> "How's my portfolio doing?" → `get_portfolio` + `get_equity_positions`, then
> summarize value, day change, and top positions.

**Place an order (happy path):**
> "Buy 5 shares of AAPL." → `search` (confirm AAPL) → `get_equity_quotes` (show
> price) → `review_equity_order` (show simulation) → `place_equity_order` (5
> shares) → report status.

**Cancel:**
> "Cancel that order." → `get_equity_orders` (find the open order id) →
> `cancel_equity_order` (that id) → confirm.
