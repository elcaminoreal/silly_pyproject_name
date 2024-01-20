import contextlib
import io
import logging
import unittest
import subprocess
import tempfile
import pathlib
import textwrap

import gather.commands
import commander_data.run
from hamcrest import assert_that, contains_string

from .. import ENTRY_DATA


@contextlib.contextmanager
def save_log():
    outfile = io.StringIO()
    handler = logging.StreamHandler(outfile)
    root_logger = logging.getLogger()
    original_level = root_logger.level
    try:
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)
        yield outfile
    finally:
        root_logger.setLevel(original_level)
        root_logger.removeHandler(handler)


def parse_args(entry_data, args, orig_run=subprocess.run):
    parser = gather.commands.set_parser(collected=ENTRY_DATA.collector.collect())
    args = parser.parse_args(args)
    args.orig_run = subprocess.run
    runner = commander_data.run.Runner.from_args(args)
    args.run, args.safe_run = runner.run, runner.safe_run
    return args


class TestName(unittest.TestCase):
    def test_name(self):
        args = parse_args(ENTRY_DATA, ["name"])
        with contextlib.ExitStack() as stack:
            temp_dir = pathlib.Path(stack.enter_context(tempfile.TemporaryDirectory()))
            outfile = stack.enter_context(save_log())
            args.env = dict(PWD=temp_dir)
            (temp_dir / "pyproject.toml").write_text(
                textwrap.dedent(
                    """\
                [project]
                name = "a-name"
            """
                )
            )
            args.__gather_command__(args)
        assert_that(outfile.getvalue(), contains_string("a-name"))

    def test_rename_dry_run(self):
        args = parse_args(ENTRY_DATA, ["rename", "new-name"])
        with contextlib.ExitStack() as stack:
            temp_dir = pathlib.Path(stack.enter_context(tempfile.TemporaryDirectory()))
            outfile = stack.enter_context(save_log())
            args.env = dict(PWD=temp_dir)
            (temp_dir / "pyproject.toml").write_text(
                textwrap.dedent(
                    """\
                [project]
                name = "old-name"
            """
                )
            )
            args.__gather_command__(args)
        assert_that(outfile.getvalue(), contains_string("new-name"))

    def test_rename_no_dry_run(self):
        args = parse_args(ENTRY_DATA, ["rename", "new-name", "--no-dry-run"])
        with contextlib.ExitStack() as stack:
            temp_dir = pathlib.Path(stack.enter_context(tempfile.TemporaryDirectory()))
            stack.enter_context(save_log())
            args.env = dict(PWD=temp_dir)
            (temp_dir / "pyproject.toml").write_text(
                textwrap.dedent(
                    """\
                [project]
                name = "old-name"
            """
                )
            )
            args.__gather_command__(args)
            updated = (temp_dir / "pyproject.toml").read_text()
        assert_that(updated, contains_string("new-name"))
