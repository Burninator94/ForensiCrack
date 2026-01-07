import os
from dataclasses import dataclass


@dataclass
class Config:
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    RUNTIME_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runtime")

    def __post_init__(self):
        self.INPUT_DIR = os.path.join(self.RUNTIME_DIR, "input")
        self.OUTPUT_DIR = os.path.join(self.RUNTIME_DIR, "output")
        self.LOG_DIR = os.path.join(self.RUNTIME_DIR, "logs")
        self.ARCHIVE_DIR = os.path.join(self.RUNTIME_DIR, "archive")
        self.WORDLIST_DIR = os.path.join(self.RUNTIME_DIR, "wordlists")

        # Known plaintext (for pkcrack) - you can adjust paths/names as needed
        self.KNOWN_PLAINTEXT_ZIP = os.path.join(self.RUNTIME_DIR, "archive", "plaintext.zip")
        self.KNOWN_PLAINTEXT_FILE = "plaintextfile.txt"  # inside that ZIP

        # Hashcat modes
        self.ZIP_AES_MODE = 13600
        self.SEVENZIP_AES_MODE = 11600

        # Create directories if they don't exist
        for path in [
            self.RUNTIME_DIR,
            self.INPUT_DIR,
            self.OUTPUT_DIR,
            self.LOG_DIR,
            self.ARCHIVE_DIR,
            self.WORDLIST_DIR,
        ]:
            os.makedirs(path, exist_ok=True)