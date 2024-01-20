import argparse
import difflib
import pathlib
import logging

from gather.commands import add_argument
import tomlkit

from . import ENTRY_DATA


LOGGER = logging.getLogger(__name__)


def _pyproject_toml(args: argparse.Namespace) -> pathlib.Path:
    return pathlib.Path(args.env["PWD"]) / "pyproject.toml"


# This commands reads, and logs, the name.
@ENTRY_DATA.register()
def name(args: argparse.Namespace) -> None:
    name = tomlkit.loads(_pyproject_toml(args).read_text())["project"][
        "name"
    ]  # type: ignore
    # Regular output can be logged at "INFO" levels.
    LOGGER.info("Current name: %s", name)


# This command modifies the name.
# It will only effect the modification
# if explicitly requested via --no-dry-run.
@ENTRY_DATA.register(
    add_argument("--no-dry-run", action="store_true", default=False),
    add_argument("new_name"),
)
def rename(args: argparse.Namespace) -> None:
    toml_file = _pyproject_toml(args)
    old_contents = toml_file.read_text()
    parsed = tomlkit.loads(old_contents)
    parsed["project"]["name"] = args.new_name  # type: ignore
    new_contents = tomlkit.dumps(parsed)
    diffs = difflib.unified_diff(
        old_contents.splitlines(),
        new_contents.splitlines(),
        lineterm="",
    )
    # This logs the diffs. The end-user can see what will
    # change.
    for a_diff in diffs:
        LOGGER.info("Difference: %s", a_diff.rstrip())
    # Explicitly check no-dry-run before writing the file.
    # Otherwise, clearly log that the actual side-effect is skipped.
    if args.no_dry_run:
        toml_file.write_text(new_contents)
    else:
        LOGGER.info("Dry run, not modifying pyproject.toml")
