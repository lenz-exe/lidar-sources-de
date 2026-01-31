import os
import subprocess
import sys
from typing import List


def get_directories(path: str) -> List[str]:
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

def run_checks_formats_tests_local():
    src_path = "src"
    directories = get_directories(src_path)

    mypy_targets = " ".join(os.path.join(src_path, d) for d in directories)
    mypy_command = f"poetry run mypy {mypy_targets}"

    commands = [
        "poetry run ruff format",
        "poetry run ruff format --check",
        "poetry run ruff check",
        mypy_command,
        "poetry run pytest",
    ]

    for cmd in commands:
        print(f"\nRunning command: {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            sys.exit(result.returncode)


def run_checks_tests_local():
    src_path = "src"
    directories = get_directories(src_path)

    mypy_targets = " ".join(os.path.join(src_path, d) for d in directories)
    mypy_command = f"poetry run mypy {mypy_targets}"

    commands = [
        "poetry run ruff format --check",
        "poetry run ruff check --output-format=gitlab --output-file report_ruff.json",
        mypy_command,
        "poetry run pytest --junitxml=report_pytest.xml",
    ]
    for cmd in commands:
        print(f"\nRunning command: {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            sys.exit(result.returncode)
