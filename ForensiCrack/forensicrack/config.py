import os

class Config:
    """
    Centralized configuration for ForensiCrack.
    Defines all runtime directories and global paths.
    """

    # Base directory for the project (directory containing forensicrack/)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Runtime directories
    RUNTIME_DIR = os.path.join(BASE_DIR, "runtime")
    INPUT_DIR = os.path.join(RUNTIME_DIR, "input")
    OUTPUT_DIR = os.path.join(RUNTIME_DIR, "output")
    LOG_DIR = os.path.join(RUNTIME_DIR, "logs")
    ARCHIVE_DIR = os.path.join(RUNTIME_DIR, "archives")
    WORDLIST_DIR = os.path.join(RUNTIME_DIR, "wordlists")

    # Wordlist filenames (brockyou must be manually placed)
    BROCKYOU = os.path.join(WORDLIST_DIR, "brockyou.txt")
    PASSPHRASES = os.path.join(WORDLIST_DIR, "passphrases.txt")

    # Logging
    LOG_FILE = os.path.join(LOG_DIR, "forensicrack.log")

    # Supported file types (expandable)
    SUPPORTED_ARCHIVES = [".zip", ".7z"]
    SUPPORTED_STEGO = [".jpg", ".jpeg"]
    SUPPORTED_HASHES = [".hash"]

    # Hashcat binary (Debian/Kali)
    HASHCAT_BIN = "/usr/bin/hashcat"

    # John the Ripper binary
    JOHN_BIN = "/usr/sbin/john"

    # Stegseek binary
    STEGSEEK_BIN = "/usr/bin/stegseek"

    # pkcrack binary
    PKCRACK_BIN = "/usr/local/bin/pkcrack"
