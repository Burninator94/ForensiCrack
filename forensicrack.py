#!/usr/bin/env python3
import argparse
import sys
from forensicrack.config import Config
from forensicrack.install import install_dependencies
from forensicrack.core import ForensiCrackApp
from forensicrack.logging_config import setup_logging


def parse_args():
    parser = argparse.ArgumentParser(description="ForensiCrack - DFIR Password and Stego Automation")
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install dependencies (tools, wordlists, directories)"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute ForensiCrack on evidence in input directory"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config = Config()

    if args.install:
        install_dependencies(config)
        return

    if args.execute:
        logger = setup_logging(config.LOG_DIR)
        app = ForensiCrackApp(config=config, logger=logger)
        app.execute()
        return

    print("No action specified. Use --install or --execute.")
    sys.exit(1)


if __name__ == "__main__":
    main()