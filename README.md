**Alfr3d** is an open-source super AI assistant that proactively plans tasks, controls your computer and external services, creates and runs Skills, builds a personal knowledge base and long-term memory, and grows alongside you through self-evolution — a reference implementation of Agent Harness engineering.

Alfr3d is lightweight, easy to deploy, and built to extend. Plug in any major LLM provider and run it 24/7 on a personal computer or server, across the web and all major IM platforms.

<p align="center">
  <a href="https://alfr3d.local/">🌐 Website</a> &nbsp;·&nbsp;
  <a href="https://docs.alfr3d.local/intro/index">📖 Docs</a> &nbsp;·&nbsp;
  <a href="https://docs.alfr3d.local/guide/quick-start">🚀 Quick Start</a> &nbsp;·&nbsp;
  <a href="https://skills.alfr3d.local/">🧩 Skill Hub</a> &nbsp;·&nbsp;
  <a href="https://alfr3d.local/download/">💻 Download</a> &nbsp;·&nbsp;
  <a href="https://link-ai.tech/alfr3d/create">☁️ Try Online</a>
</p>

<br/>

## 🌟 Highlights

| Capability | Description |
| :--- | :--- |
| [Planning](https://docs.alfr3d.local/intro/architecture) | Decomposes complex tasks and executes them step by step, looping over tools until the goal is reached |
| [Memory](https://docs.alfr3d.local/memory/index) | Three-tier architecture (context → daily → core), automatic Deep Dream distillation, hybrid keyword + vector retrieval |
| [Knowledge](https://docs.alfr3d.local/knowledge/index) | Auto-curates structured knowledge into a Markdown wiki, builds an evolving knowledge graph with visual browsing |
| [Evolution](https://docs.alfr3d.local/memory/self-evolution) | Self-Evolution reviews conversations automatically to improve skills, follow up on unfinished tasks, and consolidate memory and knowledge, growing through everyday use |
| [Skills](https://docs.alfr3d.local/skills/index) | One-click install from [Skill Hub](https://skills.alfr3d.local/), GitHub, ClawHub; or create custom skills via natural-language conversation |
| [Tools](https://docs.alfr3d.local/tools/index) | Built-in file I/O, terminal, browser, scheduler, memory retrieval, web search, and 10+ more tools — with native MCP integration |
| [Channels](https://docs.alfr3d.local/channels/index) | Integrates with Web, WeChat, Feishu, DingTalk, WeCom, QQ, Official Accounts, Telegram, and Slack |
| Multimodal | First-class support for text, images, voice, and files — recognition, generation, and delivery |
| [Models](https://docs.alfr3d.local/models/index) | Claude, GPT, Gemini, DeepSeek, Qwen, GLM, Kimi, MiniMax, Doubao, and more — swap providers from the Web console with one click |
| [Deploy](https://docs.alfr3d.local/guide/quick-start) | One-line installer, unified Web console, multiple deployment modes (local, Docker, server) |

<br/>

## 🏗️ Architecture

<img src="https://cdn.jsdelivr.net/gh/NewSoulOnTheBlock/alfr3d-assets@main/architecture/en/architecture.png" alt="Alfr3d Architecture" width="750"/>

Alfr3d is a complete **Agent Harness**: messages flow in through **Channels**; the **Agent Core** plans and reasons over memory, knowledge, and the available tools and skills; **Models** generate the response, which is sent back through the originating channel. Every layer is decoupled and independently extensible.

Read more in [Architecture](https://docs.alfr3d.local/intro/architecture).

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

> 📖 Detailed guides: [Quick Start](https://docs.alfr3d.local/guide/quick-start) · [Install from Source](https://docs.alfr3d.local/guide/manual-install) · [Upgrade](https://docs.alfr3d.local/guide/upgrade)

After installation, manage the service with the [alfr3d CLI](https://docs.alfr3d.local/cli/index):

```bash
alfr3d start | stop | restart        # service control
alfr3d status | logs                  # status and logs
alfr3d update                         # pull latest code and restart
alfr3d skill install <name>           # install a skill
alfr3d install-browser                # install browser automation
```

> 💻 Desktop client: download the **[Alfr3d Desktop client](https://alfr3d.local/download/)** (macOS / Windows) — the backend is bundled, ready to use out of the box.

<br/>

## 🤖 Models

Alfr3d supports all mainstream LLM providers. **Chat, vision, image generation, ASR/TTS, and embeddings** can each be routed to a different vendor. Providers are configured directly in the Web console — no manual file editing required.

| Provider | Featured Models | Chat | Vision | Image Gen | ASR | TTS | Embedding |
| --- | --- | :-: | :-: | :-: | :-: | :-: | :-: |
| [Claude](https://docs.alfr3d.local/models/claude) | claude-opus-5 / sonnet-5 | ✅ | ✅ | | | | |
| [OpenAI](https://docs.alfr3d.local/models/openai) | gpt-5.6 series | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| [Gemini](https://docs.alfr3d.local/models/gemini) | gemini-3.5-flash | ✅ | ✅ | ✅ | | | |
| [DeepSeek](https://docs.alfr3d.local/models/deepseek) | deepseek-v4-flash / pro | ✅ | | | | | |
| [Qwen](https://docs.alfr3d.local/models/qwen) | qwen3.7-plus | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| [GLM](https://docs.alfr3d.local/models/glm) | glm-5.2, glm-5v-turbo | ✅ | ✅ | | ✅ | | ✅ |
| [Doubao](https://docs.alfr3d.local/models/doubao) | doubao-seed-2.1 series | ✅ | ✅ | ✅ | | | ✅ |
| [Kimi](https://docs.alfr3d.local/models/kimi) | kimi-k3 | ✅ | ✅ | | | | |
| [MiniMax](https://docs.alfr3d.local/models/minimax) | MiniMax-M3 | ✅ | ✅ | ✅ | | ✅ | |
| [ERNIE](https://docs.alfr3d.local/models/qianfan) | ernie-5.1 | ✅ | ✅ | | | | |
| [MiMo](https://docs.alfr3d.local/models/mimo) | mimo-v2.5 / pro | ✅ | ✅ | | | ✅ | |
| [LinkAI](https://docs.alfr3d.local/models/linkai) | One key for 100+ models | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| [Custom](https://docs.alfr3d.local/models/custom) | Local models / third-party proxy | ✅ | | | | | |

> For details on each provider, see the [Models overview](https://docs.alfr3d.local/models/index).

<br/>

## 💬 Channels

A single Agent instance can serve multiple channels in parallel. Most channels can be onboarded right from the Web console.

| Channel | Text | Image | File | Voice | Group |
| --- | :-: | :-: | :-: | :-: | :-: |
| [Web Console](https://docs.alfr3d.local/channels/web) (default) | ✅ | ✅ | ✅ | ✅ | |
| [Telegram](https://docs.alfr3d.local/channels/telegram) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [Slack](https://docs.alfr3d.local/channels/slack) | ✅ | ✅ | ✅ | | ✅ |
| [Discord](https://docs.alfr3d.local/channels/discord) | ✅ | ✅ | ✅ | | ✅ |
| [WeChat](https://docs.alfr3d.local/channels/weixin) | ✅ | ✅ | ✅ | ✅ | |
| [Feishu / Lark](https://docs.alfr3d.local/channels/feishu) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [DingTalk](https://docs.alfr3d.local/channels/dingtalk) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [WeCom Bot](https://docs.alfr3d.local/channels/wecom-bot) | ✅ | ✅ | ✅ | ✅ | ✅ |
| [QQ](https://docs.alfr3d.local/channels/qq) | ✅ | ✅ | ✅ | | ✅ |
| [WeCom App](https://docs.alfr3d.local/channels/wecom) | ✅ | ✅ | ✅ | ✅ | |
| [WeChat Customer Service](https://docs.alfr3d.local/channels/wechat-kf) | ✅ | ✅ | ✅ | ✅ | |
| [WeChat Official Account](https://docs.alfr3d.local/channels/wechatmp) | ✅ | ✅ | | ✅ | |

> See the [Channels overview](https://docs.alfr3d.local/channels/index) for setup details.

<img src="https://cdn.jsdelivr.net/gh/NewSoulOnTheBlock/alfr3d-assets@main/screenshots/en/web-console-chat.png" alt="Alfr3d Web Console" width="800"/>

*The Web console is the default channel and the unified entry point to configure models, channels, skills, memory, and more.*

<br/>

## 🧠 Memory & Knowledge Base

**Long-term memory** uses a three-tier architecture: conversation context (short-term) → daily memory (mid-term) → MEMORY.md (long-term). A nightly **Deep Dream** pass distills scattered memories into refined long-term entries and a narrative journal. See [Long-term Memory](https://docs.alfr3d.local/memory/index) · [Deep Dream](https://docs.alfr3d.local/memory/deep-dream).

**Personal knowledge base** complements the time-ordered memory by organizing structured knowledge **by topic**. The Agent automatically curates valuable information from conversations, maintains cross-references and indexes, and the Web console offers an interactive knowledge-graph view. See [Personal Knowledge Base](https://docs.alfr3d.local/knowledge/index).

<table>
  <tr>
    <td width="50%">
      <img src="https://cdn.jsdelivr.net/gh/NewSoulOnTheBlock/alfr3d-assets@main/screenshots/en/web-console-memory.png" alt="Long-term Memory" />
      <p align="center"><em>Long-term Memory · Three-tier architecture + Deep Dream</em></p>
    </td>
    <td width="50%">
      <img src="https://cdn.jsdelivr.net/gh/NewSoulOnTheBlock/alfr3d-assets@main/screenshots/en/web-console-knowledge.png" alt="Personal Knowledge Base" />
      <p align="center"><em>Knowledge Base · Auto-curated Markdown wiki</em></p>
    </td>
  </tr>
</table>

<br/>

## 🔧 Tools & Skills

**Tools** are atomic capabilities the Agent uses to interact with system resources. **Skills** are higher-level workflows defined by a manifest file that compose multiple tools to accomplish complex tasks.

### Tool System

**Built-in tools** cover file I/O (`read` / `write` / `edit` / `ls`), terminal (`bash`), file sending (`send`), memory retrieval (`memory`), environment variables (`env_config`), web fetching (`web_fetch`), scheduling (`scheduler`), web search (`web_search`), vision (`vision`), and browser automation (`browser`).

**MCP protocol** integrates the open ecosystem of [Model Context Protocol](https://modelcontextprotocol.io) servers. A single `mcp.json` is enough — supports stdio / SSE transports, hot reload, and zero-code integration.

Learn more: [Tools overview](https://docs.alfr3d.local/tools/index) · [MCP integration](https://docs.alfr3d.local/tools/mcp).

### Skills System

- **[Skill Hub](https://skills.alfr3d.local/)** — open skill marketplace: browse, search, install in one click
- **GitHub / ClawHub / URL and more** — install skills from any source
- **Conversational authoring** — generate custom skills through dialogue with `skill-creator`; turn any workflow or third-party API into a reusable skill

```bash
/skill list                   # list installed skills
/skill search <keyword>        # search the marketplace
/skill install <name>          # one-click install
```

Learn more: [Skills overview](https://docs.alfr3d.local/skills/index) · [Creating Skills](https://docs.alfr3d.local/skills/create).

<br/>

## 🏷 Changelog

> **2026.07.29:** [v2.1.5](https://github.com/NewSoulOnTheBlock/alfr3d/releases/tag/2.1.5) — Workspace with file preview, core tool improvements (file search, write-time validation, background commands), context compaction (`/compact`), one-click prompt optimization, security hardening.

> **2026.07.20:** [v2.1.4](https://github.com/NewSoulOnTheBlock/alfr3d/releases/tag/2.1.4) — Desktop experience improvements, MCP OAuth authorization, Lark channel enhancements, scheduler improvements and data backup, new models.

> **2026.07.08:** [v2.1.3](https://github.com/NewSoulOnTheBlock/alfr3d/releases/tag/2.1.3) — [Desktop client](https://alfr3d.local/download/) for macOS / Windows, knowledge base document management, on-demand MCP tool retrieval, Traditional Chinese support, new models.

> **2026.06.18:** [v2.1.2](https://github.com/NewSoulOnTheBlock/alfr3d/releases/tag/2.1.2) — Web console upgrades (scheduled task management, knowledge base categories, multiple custom model providers), Self-Evolution improvements, new models (kimi-k2.7-code, glm-5.2), security hardening and refinements.

> **2026.06.09:** [v2.1.1](https://github.com/NewSoulOnTheBlock/alfr3d/releases/tag/2.1.1) — Self-Evolution, Web console upgrades (message management, parallel sessions), cross-platform MCP enhancements with concurrent calls, new models (MiniMax-M3, qwen3.7-plus), Python 3.13 support.

> **2026.06.01:** [v2.1.0](https://github.com/NewSoulOnTheBlock/alfr3d/releases/tag/2.1.0) — Internationalization, new channels (Telegram, Discord, Slack, WeChat Customer Service), CLI interaction upgrades, streamlined one-line install, MCP Streamable HTTP support, new models (claude-opus-4-8, MiMo).

> **2026.05.22:** [v2.0.9](https://github.com/NewSoulOnTheBlock/alfr3d/releases/tag/2.0.9) — Model management, MCP protocol support, persistent browser sessions, new models (gpt-5.5, gemini-3.5-flash, qwen3.7-max), deployment hardening.

> **2026.05.06:** [v2.0.8](https://github.com/NewSoulOnTheBlock/alfr3d/releases/tag/2.0.8) — Feishu channel overhaul (voice, streaming, QR onboarding), DeepSeek V4 and Baidu Qianfan support, scheduler tool upgrades.

> **2026.04.22:** [v2.0.7](https://github.com/NewSoulOnTheBlock/alfr3d/releases/tag/2.0.7) — Built-in image generation (GPT Image 2, Nano Banana), new models (Kimi K2.6, Claude Opus 4.7, GLM 5.1), memory and knowledge enhancements.

> **2026.04.14:** [v2.0.6](https://github.com/NewSoulOnTheBlock/alfr3d/releases/tag/2.0.6) — Knowledge base, Deep Dream memory distillation, smart context compression, multi-session Web console.

> **2026.04.01:** [v2.0.5](https://github.com/NewSoulOnTheBlock/alfr3d/releases/tag/2.0.5) — Alfr3d CLI, Skill Hub open source, browser tool, WeCom Bot QR onboarding.

> **2026.02.03:** [v2.0.0](https://github.com/NewSoulOnTheBlock/alfr3d/releases/tag/2.0.0) — Major upgrade to a super Agent assistant with multi-step task planning, long-term memory, and the Skills framework.

Full history: [Release Notes](https://docs.alfr3d.local/releases/overview)

<br/>

## 🤝 Community & Support

[File an issue](https://github.com/NewSoulOnTheBlock/alfr3d/issues) on GitHub, or scan the QR code below to join our WeChat community:

<img width="130" src="https://img-1317903499.cos.ap-guangzhou.myqcloud.com/docs/open-community.png">

<br/>

## 🔗 Related Projects

- **[Alfr3d Skill Hub](https://github.com/NewSoulOnTheBlock/alfr3d-skill-hub)** — open skill marketplace for AI Agents; works with Alfr3d, OpenClaw, Claude Code, and more
- **[bot-on-anything](https://github.com/NewSoulOnTheBlock/bot-on-anything)** — lightweight LLM application framework with integrations for Slack, Telegram, Discord, Gmail, and more
- **[AgentMesh](https://github.com/MinimalFuture/AgentMesh)** — open-source multi-agent framework for solving complex problems through team collaboration

<br/>

## 🏢 Enterprise Services

[**LinkAI**](https://link-ai.tech/) is an all-in-one AI Agent platform for enterprises and developers, offering managed hosting and enterprise-grade support for Alfr3d:

- **🚀 Zero-deployment hosted runtime** — spin up a [Alfr3d online assistant](https://link-ai.tech/alfr3d/create) in under a minute, no server required
- **🧠 Agent infrastructure** — unified access to LLMs, knowledge bases, databases, skills, and workflows; plug-and-play building blocks that extend what Alfr3d can do
- **🏢 Team & enterprise features** — workspaces, role-based access, audit logs, and private deployment for production use cases

For enterprise inquiries: sales@simple-future.tech or [scan the QR code](https://cdn.link-ai.tech/consultant.jpg) to reach our team on WeChat.

<br/>

## 🛠️ Development & Contributing

All kinds of contributions are welcome — new features, bug fixes, performance improvements, docs, or sharing your own skills on the [Skill Hub](https://skills.alfr3d.local/submit). See [CONTRIBUTING.md](/CONTRIBUTING.md) to get started, then open an Issue to discuss or send a PR directly.

⭐ Star the project to show your support, and Watch → Custom → Releases to get notified of new versions. PRs and Issues are always welcome.

## 🌟 Contributors

![alfr3d contributors](https://contrib.rocks/image?repo=NewSoulOnTheBlock/alfr3d&max=1000)

<br/>

## ⚠️ Disclaimer

1. This project is licensed under the [MIT License](/LICENSE) and is intended for technical research and learning. You are responsible for complying with applicable laws and regulations in your jurisdiction; the maintainers assume no liability for any consequences arising from use of this project.
2. **Cost & safety:** Agent mode consumes substantially more tokens than regular chat — pick models that balance quality and cost. The Agent has access to your local operating system, so only deploy it in trusted environments.
3. Alfr3d is a pure open-source project and does not participate in, authorize, or issue any cryptocurrency.

<br/>

## 📌 Project Renaming Notice

This project was previously named `alfr3d` and is now officially **Alfr3d**. The old GitHub URL redirects automatically; existing users may optionally run `git remote set-url origin https://github.com/NewSoulOnTheBlock/alfr3d.git` to update the local remote.
