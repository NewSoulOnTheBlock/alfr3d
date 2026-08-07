---
name: quickbooks-bookkeeping
description: Do bookkeeping in QuickBooks Online — categorize transactions, reconcile, create and edit invoices/bills/journal entries, manage customers and vendors, and run financial reports (P&L, balance sheet, cash flow). Use when the user asks to update their books, record or categorize a transaction, invoice a customer, reconcile an account, close the month, or pull an accounting report.
---

# QuickBooks Bookkeeping

ALFR3D keeps the books through the **QuickBooks Online MCP** (`@qboapi/qbo-mcp-server`).
When that MCP server is connected, its tools appear as normal tools. Because it
exposes ~144 tools, ALFR3D uses on-demand tool retrieval — search for the right
tool by intent (e.g. "create invoice", "profit and loss") rather than assuming a
name.

> **Requires:** the `quickbooks` MCP server configured and authorized. If the
> tools aren't available, it isn't connected — set it up with
> `alfr3d quickbooks connect` (see `docs/tools/quickbooks.mdx`). Never fabricate
> account data, balances, or transaction ids.

## Scope & constraints

- **One company (v1).** The server is bound to a single QuickBooks company
  (`REALM_ID`). Everything you do applies to that one company's books.
- **Full read/write/delete is enabled.** You can create, update, **and delete**
  real records. Deletes and edits to posted transactions are effectively
  irreversible in a client's books — treat them as high-stakes.
- Not a CPA. You record and report what the user directs; you do not give tax,
  audit, or legal advice.

## Tool families

Tools follow predictable prefixes across ~29 entities (customer, invoice, bill,
vendor, estimate, payment, journal_entry, account, item, class, department, …):

| Prefix | Meaning | Risk |
| --- | --- | --- |
| `get_*` / `search_*` | Read a record or query a list | Safe |
| `get_*_report` / reports | P&L, balance sheet, cash flow, trial balance, general ledger, aged receivables/payables | Safe |
| `create_*` | Add a new record (invoice, bill, journal entry, customer, …) | Write |
| `update_*` | Modify an existing record | Write |
| `delete_*` | Remove a record | **Destructive** |

Reports available include `get_balance_sheet`, `get_profit_and_loss`,
`get_cash_flow`, `get_trial_balance`, `get_general_ledger`, `get_aged_receivables`,
and `get_aged_payables`.

## How to keep books well

1. **Read before you write.** Pull the current state (`get_*` / `search_*`) and
   the relevant report before changing anything, so you know the starting point.
2. **Confirm every write in plain language.** Restate what you're about to create
   or change — entity, amounts, accounts, customer/vendor, dates — and get the
   user's go-ahead.
3. **Deletes and edits to posted transactions require explicit, specific
   confirmation.** Never delete or alter a posted invoice, bill, payment, or
   journal entry unless the user names it and clearly asks. Prefer a corrective
   entry over a delete when the accounting allows it.
4. **Match, don't guess.** Resolve accounts, customers, vendors, and items by
   looking them up (`search_*`) rather than inventing ids or names.
5. **Reconcile with reports.** After a batch of changes, re-run the affected
   report (e.g. P&L or balance sheet) and summarize what moved.

**Guardrails for your own behavior:**

- Never invent account names, balances, amounts, or ids. Look them up or ask.
- If a request is ambiguous (which account, cash vs accrual, which period), ask
  one clarifying question before writing.
- "Show me my P&L" or "how do my books look" is a **read** request — do not
  create or change anything.
- Redact credentials; never echo the contents of the QuickBooks `.env`.

## Example flows

**Monthly review:**
> "How did we do last month?" → `get_profit_and_loss` for the period +
> `get_balance_sheet`, then summarize revenue, expenses, net income, and cash.

**Record a bill:**
> "Log a $420 utilities bill from City Power." → `search_vendors` (find/confirm
> the vendor) → `search_accounts` (utilities expense account) → restate the entry
> → `create_bill` → confirm the new bill id.

**Invoice a customer:**
> "Invoice Acme 10 hours at $150." → `search_customers` (Acme) → `search_items`
> (service/rate) → restate → `create_invoice` → optionally `get_invoice_pdf`.

**Correction:**
> "That invoice total is wrong." → `get_invoice` (confirm current values) →
> restate the fix → `update_invoice`. Only `delete_invoice` if the user explicitly
> wants it removed rather than corrected.
