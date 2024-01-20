"""
Showcase how to use commands.

This is a wrapper around Git commands.
"""
import argparse
import logging

from commander_data.common import GIT

from gather.commands import add_argument

from . import ENTRY_DATA


# It is recommended to use the Logger to print data.
# This allows easier understanding of where messages
# come from.
LOGGER = logging.getLogger(__name__)


@ENTRY_DATA.register()
def status(args: argparse.Namespace) -> None:  # pragma: no cover
    # Getting the *status* is safe:
    # it can be spawned even in dry run mode.
    #
    # Also, note that commands are run with
    # output/error capturing on by default,
    # and automatically converting to text.
    #
    # Commands are also automatically checked.
    # A return value is always successful.
    # In case of an error, the default traceback
    # will print out stdout/stderr to aid in
    # debugging.
    result = args.safe_run(
        # Note the use of GIT.
        # This runs "git status --porcelain pyproject.toml"
        # with a more Pythonic interface to create the command line.
        GIT.status(porcelain=None)("pyproject.toml"),
        cwd=args.env["PWD"],
    ).stdout.splitlines()

    # Since the command is precise, there's no need for further
    # analysis of the output.
    # Feedback is given via log.
    if len(result) != 0:
        LOGGER.warning("pyproject.toml should be committed")
    else:
        LOGGER.warning("pyproject.toml is up to date")


@ENTRY_DATA.register(
    # The commit command has side-effects.
    # By default, it will skip side effects --
    # `--no-dry-run` should be passed to actually
    # make changes.
    add_argument("--no-dry-run", action="store_true", default=False),
)
def commit(args: argparse.Namespace) -> None:  # pragma: no cover
    # The args.run function only runs the command in non-dry-run mode.
    # Otherwise, it will log the command and log the fact that it is skipped.
    args.run(
        GIT.commit(message="Updating pyproject.toml")("pyproject.toml"),
        cwd=args.env["PWD"],
    )
