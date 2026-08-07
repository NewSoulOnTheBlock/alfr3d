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
| Channels | Integrates with Web, WeChat, Feishu, DingTalk, WeCom, QQ, Official Accounts, Telegram, and Slack |
| Multimodal | First-class support for text, images, voice, and files — recognition, generation, and delivery |
| Models | Claude, GPT, Gemini, DeepSeek, Qwen, GLM, Kimi, MiniMax, Doubao, and more — swap providers from the Web console with one click |
| Deploy | One-line installer, unified Web console, multiple deployment modes (local, Docker, server) |

<br/>

## 🏗️ Architecture

Alfr3d is a complete **Agent Harness**: messages flow in through **Channels**; the **Agent Core** plans and reasons over memory, knowledge, and the available tools and skills; **Models** generate the response, which is sent back through the originating channel. Every layer is decoupled and independently extensible.

<br/>

## 🚀 Quick Start

A one-line installer takes care of dependencies, configuration, and startup:

**Linux / macOS:**

```bash
bash <(curl -fsSL https://cdn.link-ai.tech/code/alfr3d/run.sh)
```

**Windows (PowerShell):**

```powershell
irm https://cdn.link-ai.tech/code/alfr3d/run.ps1 | iex
```

**Docker:**

```bash
curl -O https://cdn.link-ai.tech/code/alfr3d/docker-compose.yml
docker compose up -d
```

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

## 🏷 Changelog

> **2026.07.29:** v2.1.5 — Workspace with file preview, core tool improvements (file search, write-time validation, background commands), context compaction (`/compact`), one-click prompt optimization, security hardening.

> **2026.07.20:** v2.1.4 — Desktop experience improvements, MCP OAuth authorization, Lark channel enhancements, scheduler improvements and data backup, new models.

> **2026.07.08:** v2.1.3 — Desktop client for macOS / Windows, knowledge base document management, on-demand MCP tool retrieval, Traditional Chinese support, new models.

> **2026.06.18:** v2.1.2 — Web console upgrades (scheduled task management, knowledge base categories, multiple custom model providers), Self-Evolution improvements, new models (kimi-k2.7-code, glm-5.2), security hardening and refinements.

> **2026.06.09:** v2.1.1 — Self-Evolution, Web console upgrades (message management, parallel sessions), cross-platform MCP enhancements with concurrent calls, new models (MiniMax-M3, qwen3.7-plus), Python 3.13 support.

> **2026.06.01:** v2.1.0 — Internationalization, new channels (Telegram, Discord, Slack, WeChat Customer Service), CLI interaction upgrades, streamlined one-line install, MCP Streamable HTTP support, new models (claude-opus-4-8, MiMo).

> **2026.05.22:** v2.0.9 — Model management, MCP protocol support, persistent browser sessions, new models (gpt-5.5, gemini-3.5-flash, qwen3.7-max), deployment hardening.

> **2026.05.06:** v2.0.8 — Feishu channel overhaul (voice, streaming, QR onboarding), DeepSeek V4 and Baidu Qianfan support, scheduler tool upgrades.

> **2026.04.22:** v2.0.7 — Built-in image generation (GPT Image 2, Nano Banana), new models (Kimi K2.6, Claude Opus 4.7, GLM 5.1), memory and knowledge enhancements.

> **2026.04.14:** v2.0.6 — Knowledge base, Deep Dream memory distillation, smart context compression, multi-session Web console.

> **2026.04.01:** v2.0.5 — Alfr3d CLI, Skill Hub open source, browser tool, WeCom Bot QR onboarding.

> **2026.02.03:** v2.0.0 — Major upgrade to a super Agent assistant with multi-step task planning, long-term memory, and the Skills framework.

<br/>

## ⚠️ Disclaimer

1. This project is licensed under the MIT License and is intended for technical research and learning. You are responsible for complying with applicable laws and regulations in your jurisdiction; the maintainers assume no liability for any consequences arising from use of this project.
2. **Cost & safety:** Agent mode consumes substantially more tokens than regular chat — pick models that balance quality and cost. The Agent has access to your local operating system, so only deploy it in trusted environments.
3. Alfr3d is a pure open-source project and does not participate in, authorize, or issue any cryptocurrency.
