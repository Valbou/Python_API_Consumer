#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
from pathlib import Path
from subprocess import CompletedProcess, run  # nosec
from typing import Callable

from colorama import Back, Fore, Style


def run_app(
    interpreter: str, path_project: Path, app_name: str, app_method: Callable, *args
) -> int:
    print(f"\n{Back.BLUE+Fore.WHITE}Run {app_name}...{Style.RESET_ALL}")
    commands: list = app_method(interpreter, path_project, *args)
    process: CompletedProcess = run(commands)  # nosec
    if process.returncode > 0:
        print(f"{Back.RED} {app_name} FAILED {Style.RESET_ALL}")
    else:
        print(f"{Back.GREEN+Fore.BLACK} {app_name} PASSED {Style.RESET_ALL}")
    return process.returncode


def isort_commands(interpreter: str, folder: Path) -> list:
    return [
        interpreter,
        "-m",
        "isort",
        # "--check",  # Option to avoid write
        folder,
    ]


def black_commands(interpreter: str, folder: Path) -> list:
    return [
        interpreter,
        "-m",
        "black",
        "--check",  # Option to avoid write
        folder,
    ]


def flake_commands(interpreter: str, folder: Path) -> list:
    return [
        interpreter,
        "-m",
        "flake8",
        folder,
    ]


def bandit_commands(interpreter: str, folder: Path) -> list:
    return [
        interpreter,
        "-m",
        "bandit",
        "-r",
        folder,
    ]


def unittest_commands(interpreter: str, folder: Path, app_name: str) -> list:
    return [interpreter, "-m", "unittest"]


def coverage_commands(interpreter: str, folder: Path, app_name: str) -> list:
    return [interpreter, "-m", "coverage", "run", "-m", "unittest"]


def check_coverage_report(interpreter: str) -> int:
    process = run(  # nosec
        [interpreter, "-m", "coverage", "report"],
        capture_output=True,
    )
    print(process.stdout.decode())
    if process.returncode == 0:
        print(f"{Back.GREEN+Fore.BLACK} Coverage report PASSED {Style.RESET_ALL}")
        return 0
    else:
        print(
            f"{Back.RED} Coverage FAIL {Style.RESET_ALL}",
            "Coverage seems too low !",
            sep="\n",
            file=sys.stderr,
        )
        return 1


def check_git_branch_name() -> int:
    process = run(  # nosec
        ["/bin/git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True
    )
    branch_name = process.stdout
    if re.match(
        r"(^(feat|fix|doc|test|perf|refacto)([-\w]+)-#([\d]+)$)|(^master$)|(^dev$)",
        branch_name.decode(),
    ):
        print(f"{Back.GREEN+Fore.BLACK} Branch name PASSED {Style.RESET_ALL}")
        return 0
    else:
        print(f"{Back.RED} Branch name FAIL {Style.RESET_ALL}", file=sys.stderr)
        print(
            "Please rename your branch with 'bug' or 'feature'"
            " prefix separed by hyphen and followed by some words in snake case",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    path_project = Path(os.getcwd())
    path_venv = path_project.parent
    interpreter = os.path.join(path_venv, "bin", "python3")

    to_run = [
        ("Isort", isort_commands),
        ("Black", black_commands),
        ("Flake8", flake_commands),
        ("Bandit", bandit_commands),
        ("Coverage", coverage_commands, "api_consumer"),
    ]

    exit_score = 0
    print(f"{Back.WHITE+Fore.BLACK} Start pre-commit checks {Style.RESET_ALL}")

    for app in to_run:
        exit_score += run_app(interpreter, path_project, *app)

    exit_score += check_coverage_report(interpreter)
    # exit_score += check_git_branch_name()

    if exit_score > 0:
        print(f"\n\n{Back.RED} {exit_score} checks FAILS {Style.RESET_ALL}")
    else:
        print(f"\n\n{Back.GREEN+Fore.BLACK} Checks SUCCESS {Style.RESET_ALL}")

    print("Treatment result", exit_score)
    sys.exit(exit_score)
