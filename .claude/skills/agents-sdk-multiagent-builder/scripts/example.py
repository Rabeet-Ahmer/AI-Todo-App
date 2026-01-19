#!/usr/bin/env python3
"""agents-sdk-multiagent-builder helper

This script is intentionally tiny. It prints the recommended scaffold tree.
The skill itself guides Claude to generate the actual files.

Usage:
  python -X utf8 scripts/example.py --app-name my_app
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-name", default="my_app")
    args = parser.parse_args()

    app = args.app_name

    print(
        "\n".join(
            [
                "<project-root>/",
                "  pyproject.toml",
                f"  src/{app}/",
                "    __init__.py",
                "    config.py",
                "    models.py",
                "    tools.py",
                "    guardrails.py",
                "    mcp_servers.py",
                "    agents.py",
                "    runner.py",
                "  tests/",
                "    test_tools.py",
                "    test_guardrails.py",
            ]
        )
    )


if __name__ == "__main__":
    main()
