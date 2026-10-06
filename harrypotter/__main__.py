"""Command-line entry point: ``python -m harrypotter`` or ``harrypotter``."""

from __future__ import annotations

import argparse

from .core import THEMES, cast


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="harrypotter",
        description="Cast a spell: a wand appears and fireworks bloom.")
    parser.add_argument(
        "--spell", default="rainbow", choices=sorted(THEMES),
        help="colour theme (default: rainbow)")
    parser.add_argument(
        "--duration", type=float, default=8.0,
        help="rough show length in seconds (default: 8)")
    parser.add_argument(
        "--no-finish", action="store_true",
        help="skip the glitter finale")
    args = parser.parse_args(argv)
    cast(spell=args.spell, duration=args.duration,
         finish=None if args.no_finish else "glitter")


if __name__ == "__main__":
    main()
