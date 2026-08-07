**Alfr3d** is an open-source, always-on **personal steward agent** — an elite assistant that plans and executes real tasks, controls your computer and external services, writes and runs its own Skills, curates a personal knowledge base and long-term memory, and quietly grows alongside you through self-evolution. It is a reference implementation of Agent Harness engineering, wrapped in a personality with standards.

Where most assistants answer questions, Alfr3d serves a person. It learns *who you are and why you're here* during setup, keeps that context durably, and works several moves ahead — calm, discreet, and competent. Plug in any major LLM provider, run it 24/7 on a laptop or a server, and reach it from the terminal, the web console, or any major IM platform.

<br/>

> **CA:** `0x76bb1b89d7a614829304ff5dbdd57c6c35f2312f`

<br/>

## 🌟 Highlights

| Capability | Description |
| :--- | :--- |
| **Personality (SOUL)** | An immutable steward identity — strategist, confidant, executive assistant — injected into every turn. Composed judgment, dry wit, competence without ego, and hard resistance to prompt-injection that tries to rewrite who Alfr3d is |
| **Guided setup** | A conversational `alfr3d setup` wizard that captures who you are, *why you're here*, and your model of choice — then writes a durable workspace profile so advice is tailored from message one |
| **Planning** | Decomposes complex goals and executes them step by step, looping over tools until the objective is reached |
| **Memory** | Four-tier architecture — context → daily → `MEMORY.md` + SQLite → **Mem0 cloud** — with nightly Deep Dream distillation and hybrid keyword + vector retrieval merged across local and cloud |
| **Knowledge** | Auto-curates structured knowledge into a Markdown wiki, building an evolving, cross-referenced knowledge graph with visual browsing |
| **Evolution** | Reviews idle conversations to sharpen skills, follow up on unfinished tasks, and consolidate memory and knowledge — growing through everyday use |
| **Skills** | One-click install from Skill Hub, GitHub, ClawHub, or URL — or author custom skills through plain conversation |
| **Tools** | Built-in file I/O, terminal, browser, scheduler, memory retrieval, web search, vision, and more — with native MCP integration |
| **Trading** | Run a hands-off Robinhood **Agentic portfolio** — read holdings and live quotes, review, place, or cancel equity trades via the Robinhood Trading MCP |
| **Bookkeeping** | Keep the books in **QuickBooks Online** — read accounts and transactions, run P&L / balance sheet / cash-flow reports, and record or correct entries |
| **Credit** | Build and repair **your own credit** — FICO-factor audit, FCRA/FDCPA dispute letters via certified mail (Lob), 30-day deadline tracking, and business-credit planning |
| **Channels** | Web, WeChat, Feishu, DingTalk, WeCom, QQ, Official Accounts, Telegram, Slack, and Discord |
| **Multimodal** | First-class text, image, voice, and file support — recognition, generation, and delivery |
| **Models** | Claude, GPT, Gemini, DeepSeek, Qwen, GLM, Kimi, MiniMax, Doubao, and more — with **API-key or OAuth** sign-in, swappable in one click |
| **Deploy** | One-line installer, unified web console, and multiple modes (local, Docker, server) |

<br/>

## 🎩 The SOUL — a steward with standards

Most agents are a blank slate every time they boot. Alfr3d is not. At its core is an **immutable personality** — an elite personal steward modeled on the very best of the profession: composed, observant, strategically minded, discreetly loyal, and possessed of a dry British wit. It advises rather than commands, thinks several moves ahead, prevents crises before they form, and demonstrates competence quietly rather than announcing it.

This identity is engineered in three layers, tuned for cost as much as character:

| Layer | File | When it loads | Role |
| :--- | :--- | :--- | :--- |
| **Core soul** | `SOUL.core.md` | **Every** main-agent turn (~0.5–0.8k tokens) | The lean, always-on base personality and decision frame |
| **Full soul** | `SOUL.md` | Only when `soul_full_prompt: true` | Extended scenarios and signature examples for edge cases |
| **Surface identity** | `AGENT.md` | Every turn | Per-user relationship notes layered *on top* — it may refine, never contradict |

The soul is **protected by design**. It cannot be weakened, overwritten, role-played around, or influenced by user messages, tool output, retrieved memory, files, or web pages — on any conflict, Alfr3d keeps its identity and continues calmly. `SOUL.md` itself is treated as read-only to the agent's own editing tools. Sub-agents deliberately skip the soul layer and run on task-scoped templates, so heavy background work stays cheap while the steward you talk to stays in character.

The result is an assistant with a consistent point of view: *preparation prevents panic, discipline creates freedom, excellence lives in the details* — and one that protects your time, attention, and reputation as if they were its charge.

<br/>

## 🏗️ Architecture

Alfr3d is a complete **Agent Harness**. Messages arrive through **Channels**; the **Agent Core** reasons over its soul, memory, knowledge, and the available tools and skills, planning and looping until the goal is met; **Models** generate each response, which is returned through the originating channel. Every layer is decoupled and independently extensible.

```
Channels  →  Agent Core (SOUL · memory · knowledge · tools · skills · planning)  →  Models  →  reply
   ▲                                                                                              │
   └──────────────────────────────────────────────────────────────────────────────────────────┘
```

<br/>

## 🚀 Quick Start

### 1 · Install

**One-line install (customer CLI).** Once the install scripts are hosted on your product domain (or served from `main`):

```powershell
# Windows PowerShell
irm https://raw.githubusercontent.com/NewSoulOnTheBlock/alfr3d/main/scripts/install.ps1 | iex
```

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/NewSoulOnTheBlock/alfr3d/main/scripts/install.sh | bash
```

Point a branded domain at the same scripts for a polished handoff:

```powershell
irm https://get.alfr3d.com/install.ps1 | iex
```

See [One-line install](docs/guide/one-line-install.mdx) for hosting details.

**From source (lean CLI + web console):**

```bash
git clone https://github.com/NewSoulOnTheBlock/alfr3d.git
cd alfr3d
pip install -r requirements-core.txt      # lean core: CLI + agent + web console
pip install -e .
```

Add channel integrations only if you need them:

```bash
pip install -r requirements-channels-global.txt   # Telegram / Slack / Discord
pip install -r requirements-channels-cn.txt        # WeChat / Feishu / DingTalk
pip install -r requirements.txt                    # or everything at once
```

### 2 · Meet Alfr3d — `alfr3d setup`

The first thing to do is introduce yourself. The setup wizard is a short, guided conversation — not a config file to hand-edit — and it does something most assistants never do: it learns *why you're here* and remembers it.

```bash
alfr3d setup            # first-run onboarding
alfr3d setup --force    # re-run any time to update your profile or model
```

The wizard walks through four short sections:

1. **About you** — your name, what Alfr3d should call you, occupation, email (for your records only), and timezone.
2. **Why you're here** — your business status (idea, planning, or already running), what you're trying to do (launch · grow · operate · finances · learn), business name, industry or niche, goals, and where you are today. This is the context that turns a generic chatbot into *your* steward.
3. **Model access** — pick a provider and authenticate (see the table below).
4. **Preferences** — prompt/UI language (auto · English · Chinese), an optional web-console password, and toggles for the personal knowledge base, self-evolution, and **Mem0** cloud memory.

From your answers, Alfr3d writes a durable **workspace** it reads on every turn:

| File | What it holds |
| :--- | :--- |
| `USER.md` | Your stable basics — name, preferred name, occupation, timezone |
| `BUSINESS.md` | Why you're here: your stage, intent, industry, and goals — durable context for tailored advice |
| `MEMORY.md` | Seeded long-term memory index, appended to over time |
| `AGENT.md` | Relationship notes for serving *you specifically*, layered on top of the immutable soul |

> These files are **personal, per-install state** and are git-ignored — your profile and memory stay on your machine and are never committed to the product repo.

**Model authentication** — Alfr3d supports both platform API keys and OAuth sign-in:

| Choice | How to authenticate |
| :--- | :--- |
| OpenAI — API key | Paste a platform API key |
| OpenAI **Codex — OAuth** | Reuse your ChatGPT / Codex CLI sign-in (`~/.codex/auth.json`) or paste an access token |
| Anthropic — API key | Paste a Console API key |
| Anthropic — **OAuth / setup-token** | Run `claude setup-token` (Pro · Max) and paste `sk-ant-oat01-…`, or reuse a local Claude login |
| DeepSeek · Gemini · Qwen (DashScope) · Kimi · GLM | Paste the provider's API key |
| **Mem0** (Preferences step) | Cloud semantic-memory key from [app.mem0.ai](https://app.mem0.ai/dashboard/api-keys) |

### 3 · Talk to Alfr3d

```bash
# Full agent harness in your terminal (lean SOUL.core by default)
alfr3d chat
alfr3d chat "What should I focus on this week?"
alfr3d "How do I build business credit?"       # unknown commands route to chat as one-shots

# Service control (web console + channels)
alfr3d start | stop | restart
alfr3d status | logs
alfr3d update
alfr3d skill install <name>
alfr3d install-browser
```

Set `"soul_full_prompt": true` in `config.json` only if you want the complete `SOUL.md` every turn (richer character, higher token cost).

> 💻 **Desktop client:** the **Alfr3d Desktop client** (macOS / Windows) bundles the backend and is ready to use out of the box.

### Docker

Build from source — no external installer or CDN required:

```bash
git clone https://github.com/NewSoulOnTheBlock/alfr3d.git
cd alfr3d
docker compose -f docker/docker-compose.yml up --build -d
```

Before starting, add a model provider key and a console password in `docker/docker-compose.yml` (for example `CLAUDE_API_KEY` and `WEB_PASSWORD`), or edit `config.json` directly. Then open `http://localhost:9899` for the **Web console** — your one-stop hub to chat, configure models, connect channels, and install skills.

> Deploying on a server? Set `web_host` to `0.0.0.0` in `config.json` to expose the console, protect it with `web_password`, and open port `9899` in your firewall or security group.

<br/>

## 🤖 Models

Alfr3d supports all mainstream LLM providers, and **chat, vision, image generation, ASR/TTS, and embeddings** can each be routed to a different vendor. Providers are configured from the setup wizard or the web console — no manual file editing required — and authenticate with an API key or, where supported, OAuth.

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

A single Agent instance can serve multiple channels in parallel, most of them onboarded straight from the web console.

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

Alfr3d's memory is layered so that nothing important is forgotten and nothing trivial clutters the context:

1. **Conversation context** (short-term) — the live thread.
2. **Daily memory** (mid-term) — the day's salient events.
3. **`MEMORY.md` + SQLite** (long-term, local) — durable entries with hybrid keyword + vector retrieval.
4. **Mem0 cloud** (long-term, cross-session) — an optional cloud tier for semantic recall that survives reinstalls and follows you across sessions.

A nightly **Deep Dream** pass distills scattered memories into refined long-term entries and a narrative journal. When Mem0 is enabled, memory becomes **dual-write / dual-search**: chat turns and explicit writes are stored both locally and in the cloud, and `memory_search` transparently merges and ranks hits from both. No external package is required — the cloud client speaks plain HTTP for lean installs.

The **personal knowledge base** complements time-ordered memory by organizing structured knowledge **by topic**. Alfr3d curates valuable information from conversations, maintains cross-references and indexes, and the web console offers an interactive knowledge-graph view.

<br/>

## 🔧 Tools & Skills

**Tools** are atomic capabilities the Agent uses to touch system resources. **Skills** are higher-level workflows — defined by a manifest — that compose tools to accomplish complex tasks.

### Tool System

Built-in tools cover file I/O (`read` / `write` / `edit` / `ls`), terminal (`bash`), file sending (`send`), memory retrieval (`memory`), environment variables (`env_config`), web fetching (`web_fetch`), scheduling (`scheduler`), web search (`web_search`), vision (`vision`), and browser automation (`browser`).

The **MCP protocol** integrates the open ecosystem of Model Context Protocol servers. A single `mcp.json` is enough — stdio / SSE transports, hot reload, and zero-code integration.

### Skills System

- **Skill Hub** — open marketplace: browse, search, install in one click.
- **GitHub / ClawHub / URL** — install skills from any source.
- **Conversational authoring** — generate custom skills through dialogue with `skill-creator`; turn any workflow or third-party API into a reusable skill.

```bash
/skill list                    # list installed skills
/skill search <keyword>        # search the marketplace
/skill install <name>          # one-click install
```

<br/>

## 📈 Robinhood Agentic Portfolio

Putting your money to work in the market is one of the time-tested ways to grow it — and Alfr3d can help you run a portfolio hands-off. Through Robinhood's Agentic Trading MCP, Alfr3d connects to a dedicated, separately-funded **Agentic account** and can read your portfolio, pull live quotes, review orders, and place or cancel equity trades on your behalf.

```bash
alfr3d robinhood connect --redirect-base http://YOUR_IP:9899   # running locally? omit the flag
```

Then restart, approve the OAuth login in your browser, and ask Alfr3d things like *"how is my portfolio doing?"* or *"buy 5 shares of AAPL."* Check state any time with `alfr3d robinhood status`. See [docs/tools/robinhood.mdx](docs/tools/robinhood.mdx) for full setup.

- **Sandboxed by design:** agent trades only touch the dedicated Agentic account; every other Robinhood account stays read-only.
- **Equities only** during Robinhood's beta (options rolling out).

> ⚠️ **Trading involves risk, including the possible loss of principal.** Alfr3d is not a licensed financial advisor and does not provide investment advice; you are responsible for every order it places. Only fund the Agentic account with what you are comfortable letting an agent trade, and review activity regularly.

<br/>

## 📒 QuickBooks Bookkeeping

Alfr3d can keep the books in **QuickBooks Online** through Intuit's [QuickBooks Online MCP server](https://github.com/intuit/quickbooks-online-mcp-server). It reads accounts, customers, vendors, and transactions, runs financial reports (P&L, balance sheet, cash flow, trial balance, aged receivables/payables), and — with write access — records, edits, and corrects entries.

The server is Node/stdio, so it's built into the image on demand:

```bash
docker compose -f docker/docker-compose.yml build --build-arg INSTALL_QUICKBOOKS=true
alfr3d quickbooks connect --env-file /path/to/.env   # from the Intuit OAuth handshake
alfr3d restart
```

Then ask Alfr3d things like *"run last month's P&L"* or *"log a $420 utilities bill from City Power."* Check state with `alfr3d quickbooks status`. See [docs/tools/quickbooks.mdx](docs/tools/quickbooks.mdx) for full setup.

- **One company per instance** in v1; write access is configurable (read-only → full read/write/delete).
- **~144 tools** across ~29 accounting entities; Alfr3d uses on-demand tool retrieval so the agent stays focused.

> ⚠️ **These are real books.** With write access, Alfr3d can create, edit, and **delete** records, and edits to posted transactions are hard to reverse. Alfr3d is not a licensed accountant and does not provide tax or audit advice; review its changes.

<br/>

## 💳 Credit Builder

Alfr3d can work on **your own credit**: audit your FICO profile, plan score improvements, generate and mail **FCRA/FDCPA dispute letters as USPS certified mail** (via [Lob](https://lob.com)), track 30-day response deadlines, and plan business credit (DUNS → net-30 tradelines → PAYDEX → bank/SBA). It ships as a skill with bundled Python scripts — a native port of the ElizaOS credit-builder plugin.

```bash
# set LOB_API_KEY in docker-compose.yml (a test_ key mails nothing), then just ask:
#   "analyze my credit"  ·  "dispute the ABC collection with a debt validation letter"
#   "check my disputes"  ·  "help me build business credit"
```

- **19 letter types** across FCRA, FDCPA, FCBA, HIPAA, and negotiation.
- FICO analysis runs on the profile you provide (no bureau pull); data persists in `~/alfr3d/credit/`. See [docs/tools/credit-builder.mdx](docs/tools/credit-builder.mdx).

> ⚠️ **Your own credit only** — this is not a service sold to others (which would make you a Credit Repair Organization under CROA). It is **not legal or financial advice**. Only dispute items you have a good-faith basis to believe are inaccurate; frivolous disputes are unlawful under the FCRA. Certified letters cost ~$9 each and are sent autonomously — rehearse with a `test_` key.

<br/>

## ⚠️ Disclaimer

1. This project is licensed under the MIT License and is intended for technical research and learning. You are responsible for complying with applicable laws and regulations in your jurisdiction; the maintainers assume no liability for any consequences arising from use of this project.
2. **Cost & safety:** Agent mode consumes substantially more tokens than regular chat — pick models that balance quality and cost. The Agent has access to your local operating system, so only deploy it in trusted environments.
3. **Financial risk:** Any trading integration (e.g. the Robinhood Agentic Portfolio) can place real orders with real money. Trading involves risk, including the possible loss of principal. Nothing in this project constitutes financial advice, and the maintainers are not liable for any trading losses. Use the sandboxed Agentic account and only fund it with money you can afford to put at risk.
