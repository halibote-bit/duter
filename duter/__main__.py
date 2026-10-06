"""Command-line entry point: ``python -m duter`` or ``duter``."""

from __future__ import annotations

import argparse

from .core import MOODS, summon


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="duter",
        description="Summon a sprite: a magical being appears, sparks of joy bloom, "
                    "and DUTER glows in the sky.")
    parser.add_argument(
        "--mood", default="rainbow", choices=sorted(MOODS),
        help="colour theme (default: rainbow)")
    parser.add_argument(
        "--duration", type=float, default=8.0,
        help="rough show length in seconds (default: 8)")
    parser.add_argument(
        "--no-finale", action="store_true",
        help="skip the DUTER finale")
    args = parser.parse_args(argv)
    summon(mood=args.mood, duration=args.duration,
           finale=None if args.no_finale else "sparkle")


if __name__ == "__main__":
    main()