import os
import sys
import subprocess
import shutil
import platform
import requests


def download_file(url, destination):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(destination, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def install_dependencies(config):
    """
    Install tools, create directories, and download wordlists.
    ForensiCrack v1 officially supports Debian/Kali Linux only.
    """
    print("[*] Installing dependencies for ForensiCrack...")

    # Enforce Debian/Kali-only support
    system = platform.system().lower()
    if system != "linux":
        print("[!] ForensiCrack v1 supports Debian/Kali Linux only.")
        sys.exit(1)

    # Ensure runtime dirs exist
    for path in [
        config.INPUT_DIR,
        config.OUTPUT_DIR,
        config.LOG_DIR,
        config.ARCHIVE_DIR,
        config.WORDLIST_DIR,
    ]:
        os.makedirs(path, exist_ok=True)

    _install_linux_tools()
    _install_wordlists(config)

    print("[+] Installation complete.")
    print("[!] Reminder: brockyou.txt must be placed manually into:")
    print(f"    {config.WORDLIST_DIR}")
    print("    This file is not distributed with ForensiCrack.")


def _install_linux_tools():
    print("[*] Detected Linux. Installing tools with apt-get (requires sudo)...")
    tools = ["hashcat", "john", "stegseek", "git", "build-essential"]

    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y"] + tools, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to install core tools via apt-get: {e}")

    # Install pkcrack from source if not available
    if shutil.which("pkcrack") is None:
        print("[*] Installing pkcrack from source...")
        try:
            subprocess.run(["git", "clone", "https://github.com/keyunluo/pkcrack"], check=True)
            os.chdir("pkcrack")
            subprocess.run(["make"], check=True)
            subprocess.run(["sudo", "make", "install"], check=True)
            os.chdir("..")
            shutil.rmtree("pkcrack", ignore_errors=True)
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to build/install pkcrack: {e}")


def _install_wordlists(config):
    print("[*] Downloading wordlists into:", config.WORDLIST_DIR)

    # Only passphrases.txt is downloaded automatically
    wordlists = {
        "passphrases.txt": "https://github.com/initstring/passphrase-wordlist/releases/download/v2025.1/passphrases.txt"
    }

    for filename, url in wordlists.items():
        dest = os.path.join(config.WORDLIST_DIR, filename)
        if os.path.exists(dest):
            print(f"[-] {filename} already exists, skipping download.")
            continue
        try:
            print(f"[*] Downloading {filename} from {url}")
            download_file(url, dest)
            print(f"[+] Saved {filename} to {dest}")
        except Exception as e:
            print(f"[!] Failed to download {filename}: {e}")