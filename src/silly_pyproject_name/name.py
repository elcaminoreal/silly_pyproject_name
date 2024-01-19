import difflib
import pathlib
import logging

from commander_data import COMMAND
from commander_data.common import GIT
from gather.commands import add_argument
import tomlkit

from . import ENTRY_DATA


LOGGER = logging.getLogger(__name__)

def _pyproject_toml(args):
    return pathlib.Path(args.env["PWD"]) / "pyproject.toml"

def _load_pyproject(pwd):
    return tomlkit.loads((pathlib.Path(pwd) / "pyproject.toml").read_text())


@ENTRY_DATA.register()
def name(args):
    name = tomlkit.loads(_pyproject_toml(args).read_text())["project"]["name"]
    LOGGER.info("Current name: %s", name)

@ENTRY_DATA.register(
    add_argument("--no-dry-run", action="store_true", default=False),
    add_argument("new_name"),
)
def rename(args):
    toml_file = _pyproject_toml(args)
    old_contents = toml_file.read_text()
    parsed = tomlkit.loads(old_contents)
    parsed["project"]["name"] = args.new_name
    new_contents = tomlkit.dumps(parsed)
    diffs = difflib.unified_diff(
        old_contents.splitlines(),
        new_contents.splitlines(),
        lineterm="",
    )
    for a_diff in diffs:
        LOGGER.info("Difference: %s", a_diff.rstrip())
    if args.no_dry_run:
        toml_file.write_text(new_contents)
    else:
        LOGGER.info("Dry run, not modifying pyproject.toml")
