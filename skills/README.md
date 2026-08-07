# Skills

Skills are reusable instruction sets that extend the agent's capabilities. Each skill is a `SKILL.md` file in its own directory, providing specialized knowledge, workflows, and tool integrations for specific tasks.

## Skill Hub

Browse, search, and install skills from [Alfr3d Skill Hub](https://skills.alfr3d.local/).

Open source: [github.com/NewSoulOnTheBlock/alfr3d-skill-hub](https://github.com/NewSoulOnTheBlock/alfr3d-skill-hub)

## Install Skills

Install skills from multiple sources via chat (`/skill`) or terminal (`alfr3d skill`):

```bash
/skill install <name>                   # From Skill Hub
/skill install <owner>/<repo>           # From GitHub
/skill install clawhub:<name>           # From ClawHub
/skill install linkai:<code>            # From LinkAI
/skill install <url>                    # From URL (zip or SKILL.md)
```

List all available remote skills:

```bash
/skill list --remote
```

## Manage Skills

```bash
/skill list                  # List installed skills
/skill info <name>           # View skill details
/skill enable <name>         # Enable a skill
/skill disable <name>        # Disable a skill
/skill uninstall <name>      # Uninstall a skill
```

> In terminal, replace `/skill` with `alfr3d skill`.

## Skill Structure

```
skills/
  my-skill/
    SKILL.md          # Required: skill definition
    scripts/          # Optional: bundled scripts
    resources/        # Optional: reference files
```

`SKILL.md` uses YAML frontmatter:

```markdown
---
name: my-skill
description: Brief description of what the skill does
metadata: {"alfr3d":{"emoji":"🔧","requires":{"bins":["tool"],"env":["API_KEY"]}}}
---

# My Skill

Instructions, examples, and usage patterns...
```

### Frontmatter Fields

| Field | Description |
|---|---|
| `name` | Skill name (must match directory name) |
| `description` | Brief description (required) |
| `metadata.alfr3d.emoji` | Display emoji |
| `metadata.alfr3d.always` | Always include this skill (default: false) |
| `metadata.alfr3d.requires.bins` | Required binaries |
| `metadata.alfr3d.requires.env` | Required environment variables |
| `metadata.alfr3d.requires.config` | Required config paths |
| `metadata.alfr3d.os` | Supported OS (e.g., `["darwin", "linux"]`) |

## Skill Loading Order

Skills are loaded from two locations (higher precedence overrides lower):

1. **Builtin skills** (lower): `<project_root>/skills/` — shipped with the codebase
2. **Custom skills** (higher): `~/alfr3d/skills/` — installed via `alfr3d skill install` or skill creator

Skills with the same name in the custom directory override builtin ones.

## Create & Contribute

See the [Skill Creation docs](https://docs.alfr3d.local/skills/create) for details, or submit your skill to [Skill Hub](https://skills.alfr3d.local/submit).
