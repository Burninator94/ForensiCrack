import os


class Config:
    """
    Centralized configuration for ForensiCrack.
    Defines all runtime directories and global paths.
    """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    RUNTIME_DIR = os.path.join(BASE_DIR, "runtime")
    INPUT_DIR = os.path.join(RUNTIME_DIR, "input")
    OUTPUT_DIR = os.path.join(RUNTIME_DIR, "output")
    LOG_DIR = os.path.join(RUNTIME_DIR, "logs")
    ARCHIVE_DIR = os.path.join(RUNTIME_DIR, "archives")
    WORDLIST_DIR = os.path.join(RUNTIME_DIR, "wordlists")

    # Wordlist filenames
    BROCKYOU = os.path.join(WORDLIST_DIR, "brockyou.txt")
    PASSPHRASES = os.path.join(WORDLIST_DIR, "passphrases.txt")

    LOG_FILE = os.path.join(LOG_DIR, "forensicrack.log")

    SUPPORTED_ARCHIVES = [".zip", ".7z"]
    SUPPORTED_STEGO = [".jpg", ".jpeg"]
    SUPPORTED_HASHES = [".hash"]

    # Known plaintext for pkcrack (create these manually if needed)
    KNOWN_PLAINTEXT_ZIP = os.path.join(RUNTIME_DIR, "archive", "plaintext.zip")
    KNOWN_PLAINTEXT_FILE = "plaintextfile.txt"  # filename inside the ZIP

    # Hashcat modes (moved here from cracking_hashcat.py for central access)
    ZIP_AES_MODE = 13600
    SEVENZIP_AES_MODE = 11600

    # Create directories on init
    def __post_init__(self):
        for path in [
            self.RUNTIME_DIR,
            self.INPUT_DIR,
            self.OUTPUT_DIR,
            self.LOG_DIR,
            self.ARCHIVE_DIR,
            self.WORDLIST_DIR,
        ]:
            os.makedirs(path, exist_ok=True)