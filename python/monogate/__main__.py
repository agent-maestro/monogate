"""Entry point for `python -m monogate <subcommand>`."""
from __future__ import annotations

import sys


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m monogate <subcommand> [options]")
        print("  capability-card --generate | --validate")
        sys.exit(1)

    subcommand = sys.argv[1]
    remaining = sys.argv[2:]

    if subcommand == "capability-card":
        from monogate.cli.capability_card import main as cap_main
        cap_main(remaining)
    else:
        print(f"Unknown subcommand: {subcommand!r}")
        print("Available: capability-card")
        sys.exit(1)


if __name__ == "__main__":
    main()
