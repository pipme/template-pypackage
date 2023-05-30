import datetime
import os
import shlex
import subprocess
import sys
from contextlib import contextmanager
from typing import List

import pytest

_DEPENDENCY_FILE = "pyproject.toml"


@contextmanager
def inside_dir(dirpath):
    """
    Execute code from inside the given directory
    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


@contextmanager
def bake_in_temp_dir(cookies, *args, **kwargs):
    """
    Delete the temporal directory that is created when executing the tests
    :param cookies: pytest_cookies.Cookies,
        cookie to be baked and its temporal files will be removed
    """
    result = cookies.bake(*args, **kwargs)
    yield result


def run_inside_dir(commands, dirpath):
    """
    Run a command from inside a given directory, returning the exit status
    :param commands: Commands that will be executed
    :param dirpath: String, path of the directory the command is being run.
    """
    with inside_dir(dirpath):
        for command in commands:
            subprocess.check_call(shlex.split(command))


def check_output_inside_dir(command, dirpath):
    """Run a command from inside a given directory, returning the command output"""
    with inside_dir(dirpath):
        return subprocess.check_output(shlex.split(command))


def execute(
    command: List[str], dirpath: str, timeout=30, supress_warning=True
):
    """Run command inside given directory and returns output

    if there's stderr, then it may raise exception according to supress_warning
    """
    with inside_dir(dirpath):
        proc = subprocess.Popen(
            command, stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )

    out, err = proc.communicate(timeout=timeout)
    out = out.decode("utf-8")
    err = err.decode("utf-8")

    if err and not supress_warning:
        raise RuntimeError(err)
    else:
        print(err)
        return out


def test_year_compute_in_license_file(cookies):
    with bake_in_temp_dir(cookies) as result:
        license_file_path = result.project_path.joinpath("LICENSE")
        now = datetime.datetime.now()
        assert str(now.year) in license_file_path.read_text()


def project_info(result):
    """Get toplevel dir, project_name_slug, and project dir from baked cookies"""
    project_path = str(result.project_path)
    project_name_slug = os.path.split(project_path)[-1]
    project_dir = os.path.join(project_path, project_name_slug)
    return project_path, project_name_slug, project_dir


def test_bake_with_defaults(cookies):
    with bake_in_temp_dir(cookies) as result:
        assert result.project_path.is_dir()
        assert result.exit_code == 0
        assert result.exception is None

        found_toplevel_files_dirs = [
            f.name for f in result.project_path.rglob("*")
        ]
        assert _DEPENDENCY_FILE in found_toplevel_files_dirs
        assert "python_project" in found_toplevel_files_dirs
        assert "tests" in found_toplevel_files_dirs

        mkdocs_yml = os.path.join(result._project_dir, "mkdocs.yml")
        with open(mkdocs_yml, "r") as f:
            lines = f.readlines()
            assert "  - Home: index.md\n" in lines


def test_bake_without_author_file(cookies):
    with bake_in_temp_dir(
        cookies, extra_context={"create_author_file": "n"}
    ) as result:
        found_toplevel_files = [
            f.name for f in result.project_path.rglob("*") if f.is_file()
        ]
        assert "AUTHORS.md" not in found_toplevel_files
        doc_files = [
            f.name
            for f in result.project_path.joinpath("docs").rglob("*")
            if f.is_file()
        ]
        assert "authors.md" not in doc_files

        # make sure '-authors: authors.md' not appeared in mkdocs.yml
        mkdocs_yml = os.path.join(result._project_dir, "mkdocs.yml")
        with open(mkdocs_yml, "r") as f:
            lines = f.readlines()
            assert "  - authors: authors.md\n" not in lines


@pytest.mark.parametrize(
    "license_info",
    [
        ("MIT", "MIT "),
        (
            "BSD-3-Clause",
            "Redistributions of source code must retain the "
            + "above copyright notice, this",
        ),
        ("ISC", "ISC License"),
        ("Apache-2.0", "Licensed under the Apache License, Version 2.0"),
        ("GPL-3.0-only", "GNU GENERAL PUBLIC LICENSE"),
    ],
)
def test_bake_selecting_license(cookies, license_info):
    license, target_string = license_info
    with bake_in_temp_dir(
        cookies, extra_context={"license": license}
    ) as result:
        assert (
            target_string
            in result.project_path.joinpath("LICENSE").read_text()
        )
        assert (
            license
            in result.project_path.joinpath(_DEPENDENCY_FILE).read_text()
        )


def test_bake_no_license(cookies):
    with bake_in_temp_dir(cookies, extra_context={"license": "no"}) as result:
        found_toplevel_files = [
            f.name for f in result.project_path.rglob("*") if f.is_file()
        ]
        assert _DEPENDENCY_FILE in found_toplevel_files
        assert "LICENSE" not in found_toplevel_files
        assert (
            "License"
            not in result.project_path.joinpath("README.md").read_text()
        )
        assert (
            "license"
            not in result.project_path.joinpath(_DEPENDENCY_FILE).read_text()
        )


@pytest.mark.parametrize(
    "args",
    [
        ({"command_line_interface": "no"}, False),
        ({"command_line_interface": "click"}, True),
    ],
)
def test_bake_with_no_console_script(cookies, args):
    context, is_present = args
    result = cookies.bake(extra_context=context)
    project_path, project_name_slug, project_dir = project_info(result)
    found_project_files = os.listdir(project_dir)
    assert ("cli.py" in found_project_files) == is_present


def test_bake_with_console_script_cli(cookies):
    context = {"command_line_interface": "click"}
    result = cookies.bake(extra_context=context)
    project_path, project_name_slug, project_dir = project_info(result)
    module_path = os.path.join(project_dir, "cli.py")

    out = execute(
        [
            sys.executable,
            module_path,
        ],
        project_dir,
    )
    assert project_name_slug in out

    out = execute([sys.executable, module_path, "--help"], project_dir)

    assert "Show this message and exit." in out
