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
    print("[*] Installing dependencies for ForensiCrack...")

    system = platform.system().lower()
    if system != "linux":
        print("[!] ForensiCrack v1 supports Debian/Kali Linux only.")
        sys.exit(1)

    for path in [
        config.INPUT_DIR,
        config.OUTPUT_DIR,
        config.LOG_DIR,
        config.ARCHIVE_DIR,
        config.WORDLIST_DIR,
        config.PLAINTEXTS_DIR,
    ]:
        os.makedirs(path, exist_ok=True)

    _install_linux_tools()
    _install_wordlists(config)

    print("[+] Installation complete.")
    print("[!] Reminder: brockyou.txt must be downloaded and placed manually into:")
    print(f"    {config.WORDLIST_DIR}")
    print("    Download link: https://mega.nz/file/cr5HGACC#ANXlTyu8sdlIUizcIX418sa1C2M4Ame_3bjxU9xXGfY")
    print("[!] Reminder: RockYou2021.txt must be downloaded and placed manually into:")
    print(f"    {config.WORDLIST_DIR}")
    print("    Download link: https://mega.nz/folder/aDpmxCiD#f_pSJ0vV698-Ev1mbyYNAQ")


def _install_linux_tools():
    print("[*] Installing tools with apt-get (requires sudo)...")
    tools = ["hashcat", "john", "stegseek", "git", "build-essential", "cmake", "ruby-full"]

    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y"] + tools, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to install core tools: {e}")

    # zsteg
    try:
        subprocess.run(["sudo", "gem", "install", "zsteg"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to install zsteg: {e}")

    # bkcrack
    if shutil.which("bkcrack") is None:
        print("[*] Installing bkcrack from source...")
        try:
            subprocess.run(["git", "clone", "https://github.com/kimci86/bkcrack.git"], check=True)
            os.chdir("bkcrack")
            subprocess.run(["cmake", "."], check=True)
            subprocess.run(["make"], check=True)
            subprocess.run(["sudo", "make", "install"], check=True)
            os.chdir("..")
            shutil.rmtree("bkcrack", ignore_errors=True)
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to build/install bkcrack: {e}")


def _install_wordlists(config):
    print("[*] Downloading wordlists into:", config.WORDLIST_DIR)

    wordlists = {
        "passphrases.txt": "https://github.com/initstring/passphrase-wordlist/releases/download/v2025.1/passphrases.txt"
    }

    for filename, url in wordlists.items():
        dest = os.path.join(config.WORDLIST_DIR, filename)
        if os.path.exists(dest):
            print(f"[-] {filename} already exists, skipping.")
            continue
        try:
            print(f"[*] Downloading {filename}")
            download_file(url, dest)
            print(f"[+] Saved {filename}")
        except Exception as e:
            print(f"[!] Download failed: {e}")
