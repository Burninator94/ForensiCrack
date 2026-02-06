#!/usr/bin/env python3
import argparse
import sys
import shutil
import os
from .config import Config
from .install import install_dependencies
from .app import ForensiCrackApp
from .logging_config import setup_logging
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(description="ForensiCrack - DFIR Password and Stego Automation")
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install dependencies (tools, wordlists, directories)"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update apt-based tools (hashcat, john, stegseek) and re-check non-apt ones"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute ForensiCrack on evidence in input directory"
    )
    return parser.parse_args()


def update_tools():
    print("[*] Updating apt-based tools...")
    try:
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "upgrade", "-y", "hashcat", "john", "stegseek"], check=True)
        print("[+] apt-based tools (hashcat, john, stegseek) updated.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to update apt tools: {e}")

    print("[*] Re-checking zsteg (Ruby gem)...")
    try:
        subprocess.run(["sudo", "gem", "install", "zsteg", "--no-document"], check=True)
        print("[+] zsteg updated/re-installed.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to update zsteg: {e}")

    print("[*] Re-checking bkcrack (source build)...")
    # Optional: only rebuild if needed (e.g., check version or skip if exists)
    if shutil.which("bkcrack") is None:
        print("[*] bkcrack missing - rebuilding...")
        try:
            subprocess.run(["git", "clone", "https://github.com/kimci86/bkcrack.git"], check=True)
            os.chdir("bkcrack")
            subprocess.run(["cmake", "."], check=True)
            subprocess.run(["make"], check=True)
            subprocess.run(["sudo", "make", "install"], check=True)
            os.chdir("..")
            shutil.rmtree("bkcrack", ignore_errors=True)
            print("[+] bkcrack rebuilt and installed.")
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to rebuild bkcrack: {e}")
    else:
        print("[+] bkcrack already installed (skipping rebuild).")


def main():
    args = parse_args()
    config = Config()

    if args.install:
        install_dependencies(config)
        return

    if args.update:
        update_tools()
        return

    if args.execute:
        logger = setup_logging(config.LOG_DIR)
        app = ForensiCrackApp(config=config, logger=logger)
        app.execute()
        return

    print("No action specified. Use --install, --update, or --execute.")
    sys.exit(1)


if __name__ == "__main__":
    main()
