import logging

from commander_data import COMMAND
from commander_data.common import GIT

from gather.commands import add_argument

from . import ENTRY_DATA


LOGGER = logging.getLogger(__name__)


@ENTRY_DATA.register()
def status(args):
    result = args.safe_run(
        GIT.status(porcelain=None)("pyproject.toml"),
        cwd=args.env["PWD"],
    ).stdout.splitlines()
    if len(result) != 0:
        LOGGER.warning("pyproject.toml should be committed")
    else:
        LOGGER.warning("pyproject.toml is up to date")

@ENTRY_DATA.register(
    add_argument("--no-dry-run", action="store_true", default=False),
)
def commit(args):
    args.run(
        GIT.commit(message="Updating pyproject.toml")("pyproject.toml"),
        cwd=args.env["PWD"],
    )
