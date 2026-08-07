"""Alfr3d CLI entry point."""

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


HELP_TEXT = """Usage: alfr3d COMMAND [ARGS]...

  Alfr3d CLI - Manage your Alfr3d instance.

Commands:
  help     Show this message.
  version  Show the version.
  start    Start Alfr3d.
  stop     Stop Alfr3d.
  restart  Restart Alfr3d.
  update   Update Alfr3d and restart.
  status   Show Alfr3d running status.
  logs     View Alfr3d logs.
  skill    Manage Alfr3d skills.
  knowledge  Manage knowledge base.
  backup   Back up config and agent workspace.
  restore  Restore a Alfr3d backup.
  install-browser  Install browser tool (Playwright + Chromium).
  robinhood  Connect to the Robinhood Trading MCP.
  quickbooks  Connect to the QuickBooks Online MCP.

Tip: Memory index management lives in chat — send /memory status or
/memory rebuild-index to the running agent."""


class Alfr3dCLI(click.Group):

    def format_help(self, ctx, formatter):
        formatter.write(HELP_TEXT.strip())
        formatter.write("\n")

    def parse_args(self, ctx, args):
        if args and args[0] == 'help':
            click.echo(HELP_TEXT.strip())
            ctx.exit(0)
        return super().parse_args(ctx, args)


@click.group(cls=Alfr3dCLI, invoke_without_command=True, context_settings=dict(help_option_names=[]))
@click.pass_context
def main(ctx):
    """Alfr3d CLI - Manage your Alfr3d instance."""
    if ctx.invoked_subcommand is None:
        click.echo(HELP_TEXT.strip())


@main.command()
def version():
    """Show the version."""
    click.echo(f"alfr3d {__version__}")


@main.command(name='help')
@click.pass_context
def help_cmd(ctx):
    """Show this message."""
    click.echo(HELP_TEXT.strip())


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


if __name__ == '__main__':
    main()
