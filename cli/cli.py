"""Alfr3d CLI entry point — customer-facing product surface."""

import click
from cli import __version__
from cli.commands.skill import skill
from cli.commands.process import start, stop, restart, self_restart, update, status, logs
from cli.commands.context import context
from cli.commands.install import install_browser
from cli.commands.knowledge import knowledge
from cli.commands.backup import backup_command, restore_command
from cli.commands.robinhood import robinhood
from cli.commands.quickbooks import quickbooks
from cli.commands.chat import chat


HELP_TEXT = """Usage: alfr3d COMMAND [ARGS]...

  Alfr3d — personal steward CLI.

Talk to Alfr3d:
  chat [PROMPT]   Interactive session, or one-shot with a prompt
  alfr3d "…"      Same as chat (any unknown first word is treated as a prompt)

Service:
  start           Start Alfr3d (web console and channels)
  stop            Stop Alfr3d
  restart         Restart Alfr3d
  update          Update Alfr3d and restart
  status          Show running status
  logs            View logs

Capabilities:
  skill           Manage skills
  knowledge       Manage the knowledge base
  backup          Back up config and agent workspace
  restore         Restore a backup
  install-browser Install browser automation (Playwright + Chromium)
  robinhood       Connect Robinhood Trading MCP
  quickbooks      Connect QuickBooks Online MCP

Other:
  help            Show this message
  version         Show the version

Examples:
  alfr3d chat
  alfr3d chat "What should I focus on this week?"
  alfr3d "How do I build business credit?"
  alfr3d start

Tip: In a running session, memory commands are also available in chat
(e.g. /memory status)."""


# Built-in commands that must not be treated as freeform chat prompts.
_KNOWN_COMMANDS = frozenset({
    "help",
    "version",
    "chat",
    "start",
    "stop",
    "restart",
    "self-restart",
    "update",
    "status",
    "logs",
    "skill",
    "knowledge",
    "backup",
    "restore",
    "install-browser",
    "robinhood",
    "quickbooks",
    "context",
})


class Alfr3dCLI(click.Group):
    """Click group with Alfred-style freeform prompts for customers."""

    def format_help(self, ctx, formatter):
        formatter.write(HELP_TEXT.strip())
        formatter.write("\n")

    def parse_args(self, ctx, args):
        if args and args[0] == "help":
            click.echo(HELP_TEXT.strip())
            ctx.exit(0)

        # `alfr3d "what is a DUNS number?"` or `alfr3d how do I …`
        # → route to the chat command when the first token is not a real command.
        if args:
            first = args[0]
            if first not in _KNOWN_COMMANDS and not first.startswith("-"):
                args = ["chat", *args]

        return super().parse_args(ctx, args)


@click.group(
    cls=Alfr3dCLI,
    invoke_without_command=True,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.pass_context
def main(ctx):
    """Alfr3d — personal steward CLI."""
    if ctx.invoked_subcommand is None:
        click.echo(HELP_TEXT.strip())


@main.command()
def version():
    """Show the version."""
    click.echo(f"alfr3d {__version__}")


@main.command(name="help")
@click.pass_context
def help_cmd(ctx):
    """Show this message."""
    click.echo(HELP_TEXT.strip())


main.add_command(chat)
main.add_command(skill)
main.add_command(start)
main.add_command(stop)
main.add_command(restart)
main.add_command(self_restart)
main.add_command(update)
main.add_command(status)
main.add_command(logs)
main.add_command(context)
main.add_command(knowledge)
main.add_command(backup_command)
main.add_command(restore_command)
main.add_command(install_browser)
main.add_command(robinhood)
main.add_command(quickbooks)


if __name__ == "__main__":
    main()
