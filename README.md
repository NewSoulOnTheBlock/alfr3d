**Alfr3d** is an open-source super AI assistant that proactively plans tasks, controls your computer and external services, creates and runs Skills, builds a personal knowledge base and long-term memory, and grows alongside you through self-evolution — a reference implementation of Agent Harness engineering.

Alfr3d is lightweight, easy to deploy, and built to extend. Plug in any major LLM provider and run it 24/7 on a personal computer or server, across the web and all major IM platforms.

<br/>

## 🌟 Highlights

| Capability | Description |
| :--- | :--- |
| Planning | Decomposes complex tasks and executes them step by step, looping over tools until the goal is reached |
| Memory | Three-tier architecture (context → daily → core), automatic Deep Dream distillation, hybrid keyword + vector retrieval |
| Knowledge | Auto-curates structured knowledge into a Markdown wiki, builds an evolving knowledge graph with visual browsing |
| Evolution | Self-Evolution reviews conversations automatically to improve skills, follow up on unfinished tasks, and consolidate memory and knowledge, growing through everyday use |
| Skills | One-click install from Skill Hub, GitHub, ClawHub; or create custom skills via natural-language conversation |
| Tools | Built-in file I/O, terminal, browser, scheduler, memory retrieval, web search, and 10+ more tools — with native MCP integration |
| Trading | Manage a Robinhood **Agentic portfolio** — read holdings and live quotes, and review, place, or cancel equity trades via the Robinhood Trading MCP |
| Bookkeeping | Keep the books in **QuickBooks Online** — read accounts and transactions, run reports (P&L, balance sheet, cash flow), and record or correct entries via the QuickBooks Online MCP |
| Credit | Build and repair **your own credit** — FICO-factor audit, FCRA/FDCPA dispute letters via certified mail (Lob), 30-day deadline tracking, and business-credit planning |
| Channels | Integrates with Web, WeChat, Feishu, DingTalk, WeCom, QQ, Official Accounts, Telegram, and Slack |
| Multimodal | First-class support for text, images, voice, and files — recognition, generation, and delivery |
| Models | Claude, GPT, Gemini, DeepSeek, Qwen, GLM, Kimi, MiniMax, Doubao, and more — swap providers from the Web console with one click |
| Deploy | One-line installer, unified Web console, multiple deployment modes (local, Docker, server) |

<br/>

## 🏗️ Architecture

Alfr3d is a complete **Agent Harness**: messages flow in through **Channels**; the **Agent Core** plans and reasons over memory, knowledge, and the available tools and skills; **Models** generate the response, which is sent back through the originating channel. Every layer is decoupled and independently extensible.

<br/>

## 🚀 Quick Start

Clone the repo and start Alfr3d with Docker — the image is built from source, so no external installer or CDN is required:

```bash
git clone https://github.com/NewSoulOnTheBlock/alfr3d.git
cd alfr3d
docker compose -f docker/docker-compose.yml up --build -d
```

Before starting, add a model provider key and a console password in `docker/docker-compose.yml` (for example set `CLAUDE_API_KEY` and `WEB_PASSWORD`), or edit `config.json` directly.

Once started, open `http://localhost:9899` to access the **Web console** — your one-stop hub to chat with the Agent, configure models, connect channels, and install skills.

> Deploying on a server? Set `web_host` to `0.0.0.0` in `config.json` to make the console reachable from outside, and set `web_password` to protect it. Don't forget to open port `9899` in your firewall or security group.

After installation, manage the service with the alfr3d CLI:

```bash
alfr3d start | stop | restart        # service control
alfr3d status | logs                  # status and logs
alfr3d update                         # pull latest code and restart
alfr3d skill install <name>           # install a skill
alfr3d install-browser                # install browser automation
```

> 💻 Desktop client: the **Alfr3d Desktop client** (macOS / Windows) bundles the backend, ready to use out of the box.

<br/>

## 🤖 Models

Alfr3d supports all mainstream LLM providers. **Chat, vision, image generation, ASR/TTS, and embeddings** can each be routed to a different vendor. Providers are configured directly in the Web console — no manual file editing required.

| Provider | Featured Models | Chat | Vision | Image Gen | ASR | TTS | Embedding |
| --- | --- | :-: | :-: | :-: | :-: | :-: | :-: |
| Claude | claude-opus-5 / sonnet-5 | ✅ | ✅ | | | | |
| OpenAI | gpt-5.6 series | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Gemini | gemini-3.5-flash | ✅ | ✅ | ✅ | | | |
| DeepSeek | deepseek-v4-flash / pro | ✅ | | | | | |
| Qwen | qwen3.7-plus | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| GLM | glm-5.2, glm-5v-turbo | ✅ | ✅ | | ✅ | | ✅ |
| Doubao | doubao-seed-2.1 series | ✅ | ✅ | ✅ | | | ✅ |
| Kimi | kimi-k3 | ✅ | ✅ | | | | |
| MiniMax | MiniMax-M3 | ✅ | ✅ | ✅ | | ✅ | |
| ERNIE | ernie-5.1 | ✅ | ✅ | | | | |
| MiMo | mimo-v2.5 / pro | ✅ | ✅ | | | ✅ | |
| LinkAI | One key for 100+ models | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Custom | Local models / third-party proxy | ✅ | | | | | |

<br/>

## 💬 Channels

A single Agent instance can serve multiple channels in parallel. Most channels can be onboarded right from the Web console.

| Channel | Text | Image | File | Voice | Group |
| --- | :-: | :-: | :-: | :-: | :-: |
| Web Console (default) | ✅ | ✅ | ✅ | ✅ | |
| Telegram | ✅ | ✅ | ✅ | ✅ | ✅ |
| Slack | ✅ | ✅ | ✅ | | ✅ |
| Discord | ✅ | ✅ | ✅ | | ✅ |
| WeChat | ✅ | ✅ | ✅ | ✅ | |
| Feishu / Lark | ✅ | ✅ | ✅ | ✅ | ✅ |
| DingTalk | ✅ | ✅ | ✅ | ✅ | ✅ |
| WeCom Bot | ✅ | ✅ | ✅ | ✅ | ✅ |
| QQ | ✅ | ✅ | ✅ | | ✅ |
| WeCom App | ✅ | ✅ | ✅ | ✅ | |
| WeChat Customer Service | ✅ | ✅ | ✅ | ✅ | |
| WeChat Official Account | ✅ | ✅ | | ✅ | |

*The Web console is the default channel and the unified entry point to configure models, channels, skills, memory, and more.*

<br/>

## 🧠 Memory & Knowledge Base

**Long-term memory** uses a three-tier architecture: conversation context (short-term) → daily memory (mid-term) → MEMORY.md (long-term). A nightly **Deep Dream** pass distills scattered memories into refined long-term entries and a narrative journal.

**Personal knowledge base** complements the time-ordered memory by organizing structured knowledge **by topic**. The Agent automatically curates valuable information from conversations, maintains cross-references and indexes, and the Web console offers an interactive knowledge-graph view.

<br/>

## 🔧 Tools & Skills

**Tools** are atomic capabilities the Agent uses to interact with system resources. **Skills** are higher-level workflows defined by a manifest file that compose multiple tools to accomplish complex tasks.

### Tool System

**Built-in tools** cover file I/O (`read` / `write` / `edit` / `ls`), terminal (`bash`), file sending (`send`), memory retrieval (`memory`), environment variables (`env_config`), web fetching (`web_fetch`), scheduling (`scheduler`), web search (`web_search`), vision (`vision`), and browser automation (`browser`).

**MCP protocol** integrates the open ecosystem of Model Context Protocol servers. A single `mcp.json` is enough — supports stdio / SSE transports, hot reload, and zero-code integration.

### Skills System

- **Skill Hub** — open skill marketplace: browse, search, install in one click
- **GitHub / ClawHub / URL and more** — install skills from any source
- **Conversational authoring** — generate custom skills through dialogue with `skill-creator`; turn any workflow or third-party API into a reusable skill

```bash
/skill list                   # list installed skills
/skill search <keyword>        # search the marketplace
/skill install <name>          # one-click install
```

<br/>

## 📈 Robinhood Agentic Portfolio

Putting your money to work in the market is one of the time-tested ways to grow it
— and Alfr3d can help you run a portfolio hands-off. Through Robinhood's Agentic
Trading MCP, Alfr3d connects to a dedicated, separately-funded **Agentic account**
and can read your portfolio, pull live quotes, review orders, and place or cancel
equity trades on your behalf.

Set it up in one command:

```bash
alfr3d robinhood connect --redirect-base http://YOUR_IP:9899   # running locally? omit the flag
```

Then restart, approve the OAuth login in your browser, and ask Alfr3d things like
*"how is my portfolio doing?"* or *"buy 5 shares of AAPL."* Check state any time
with `alfr3d robinhood status`. See [docs/tools/robinhood.mdx](docs/tools/robinhood.mdx)
for full setup.

- **Sandboxed by design:** agent trades only touch the dedicated Agentic account; every other Robinhood account stays read-only.
- **Equities only** during Robinhood's beta (options rolling out).

> ⚠️ **Trading involves risk, including the possible loss of principal.** Alfr3d is
> not a licensed financial advisor and does not provide investment advice; you are
> responsible for every order it places on your behalf. Only fund the Agentic
> account with what you are comfortable letting an agent trade, and review activity
> regularly.

<br/>

## 📒 QuickBooks Bookkeeping

Alfr3d can keep the books in **QuickBooks Online** through Intuit's
[QuickBooks Online MCP server](https://github.com/intuit/quickbooks-online-mcp-server).
It reads accounts, customers, vendors, and transactions, runs financial reports
(P&L, balance sheet, cash flow, trial balance, aged receivables/payables), and —
with write access — records, edits, and corrects entries.

The server is Node/stdio, so it's built into the image on demand:

```bash
docker compose -f docker/docker-compose.yml build --build-arg INSTALL_QUICKBOOKS=true
alfr3d quickbooks connect --env-file /path/to/.env   # from the Intuit OAuth handshake
alfr3d restart
```

Then ask Alfr3d things like *"run last month's P&L"* or *"log a $420 utilities
bill from City Power."* Check state with `alfr3d quickbooks status`. See
[docs/tools/quickbooks.mdx](docs/tools/quickbooks.mdx) for full setup.

- **One company per instance** in v1; write access is configurable
  (read-only → full read/write/delete).
- **~144 tools** across ~29 accounting entities; Alfr3d uses on-demand tool
  retrieval so the agent stays focused.

> ⚠️ **These are real books.** With write access, Alfr3d can create, edit, and
> **delete** records, and edits to posted transactions are hard to reverse. Alfr3d
> is not a licensed accountant and does not provide tax or audit advice; review
> its changes.

<br/>

## 💳 Credit Builder

Alfr3d can work on **your own credit**: audit your FICO profile, plan score
improvements, generate and mail **FCRA/FDCPA dispute letters as USPS certified
mail** (via [Lob](https://lob.com)), track 30-day response deadlines, and plan
business credit (DUNS → net-30 tradelines → PAYDEX → bank/SBA). It ships as a
skill with bundled Python scripts — a native port of the ElizaOS
credit-builder plugin.

```bash
# set LOB_API_KEY in docker-compose.yml (a test_ key mails nothing), then just ask:
#   "analyze my credit"  ·  "dispute the ABC collection with a debt validation letter"
#   "check my disputes"  ·  "help me build business credit"
```

- **19 letter types** across FCRA, FDCPA, FCBA, HIPAA, and negotiation.
- FICO analysis runs on the profile you provide (no bureau pull); data persists
  in `~/alfr3d/credit/`. See [docs/tools/credit-builder.mdx](docs/tools/credit-builder.mdx).

> ⚠️ **Your own credit only** — this is not a service sold to others (which would
> make you a Credit Repair Organization under CROA). It is **not legal or
> financial advice**. Only dispute items you have a good-faith basis to believe
> are inaccurate; frivolous disputes are unlawful under the FCRA. Certified
> letters cost ~$9 each and are sent autonomously — rehearse with a `test_` key.

<br/>

## ⚠️ Disclaimer

1. This project is licensed under the MIT License and is intended for technical research and learning. You are responsible for complying with applicable laws and regulations in your jurisdiction; the maintainers assume no liability for any consequences arising from use of this project.
2. **Cost & safety:** Agent mode consumes substantially more tokens than regular chat — pick models that balance quality and cost. The Agent has access to your local operating system, so only deploy it in trusted environments.
3. **Financial risk:** Any trading integration (e.g. the Robinhood Agentic Portfolio) can place real orders with real money. Trading involves risk, including the possible loss of principal. Nothing in this project constitutes financial advice, and the maintainers are not liable for any trading losses. Use the sandboxed Agentic account and only fund it with money you can afford to put at risk.
