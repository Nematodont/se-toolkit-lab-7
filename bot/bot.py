"""LMS Telegram bot entry point.

Supports two modes:
  --test "/command"  : calls handlers directly and prints response to stdout
  (no flags)         : starts the Telegram bot via aiogram
"""

import argparse
import sys

from handlers import route_command


def main() -> None:
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        help="Run a command through handlers and print the response (no Telegram)",
    )
    args = parser.parse_args()

    if args.test:
        response = route_command(args.test)
        print(response)
        sys.exit(0)

    # Telegram mode (placeholder — Task 1 scaffold)
    print("Telegram mode not yet implemented. Use --test mode for now.")
    sys.exit(1)


if __name__ == "__main__":
    main()
