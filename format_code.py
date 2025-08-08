#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path


def run_formatter(module_name, args):
    print(f"Running {module_name}...")
    result = subprocess.run(
        [sys.executable, "-m", module_name] + args, capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"{module_name} completed successfully.")
    else:
        print(f"{module_name} failed:\n{result.stderr}")
        sys.exit(result.returncode)


def format_code(target_dir="."):
    py_files = list(Path(target_dir).rglob("*.py"))
    if not py_files:
        print("No Python files found.")
        return

    run_formatter("isort", [target_dir])
    run_formatter("black", [target_dir])


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    format_code(target)
