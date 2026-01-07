import os
import subprocess
import logging


class HashcatEngine:
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("ForensiCrack.Hashcat")

        self.KNOWN_HASH_MAP = {
            "ntlm": 1000,
            "netntlmv1": 5500,
            "netntlmv2": 5600,
            "sha512crypt": 1800,
            "sha256crypt": 7400,
            "md5crypt": 500,
            "pdf14": 10500,
            "pdf17": 10700,
            "pdf20": 10710,
            "office2007": 9400,
            "office2010": 9500,
            "office2013": 9600,
        }

        self.KNOWN_ENCRYPTION_MAP = {
            "zipcrypto": "USE_PKCRACK",
            "aes-zip": 13600,
            "aes": 13600,
            "aes-7zip": 11600,
            "7zip-aes": 11600,
            "office2007": 9400,
            "office2010": 9500,
            "office2013": 9600,
            "pdf14": 10500,
            "pdf17": 10700,
            "pdf20": 10710,
        }

    def crack_hashfile(self, hashfile: str, hash_type_code: int, wordlists: list[str], output_path: str) -> bool:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        for wordlist in wordlists:
            cmd = [
                "hashcat",
                "-m", str(hash_type_code),
                "-a", "0",
                hashfile,
                wordlist,
                "--outfile", output_path,
                "--outfile-format", "2",
                "--force",
            ]
            self.logger.info(f"Running hashcat: {' '.join(cmd)}")
            result = subprocess.run(cmd)
            if result.returncode == 0:
                self.logger.info(f"Hashcat succeeded on {hashfile} with {wordlist}")
                return True

        self.logger.warning(f"Hashcat failed for {hashfile}")
        return False

    def resolve_hashcat_mode(self, evidence, file_identifier, zip_info=None):
        # 1. User-supplied hash algorithm
        if evidence.known_hash_algo:
            algo = evidence.known_hash_algo.lower()
            mode = self.KNOWN_HASH_MAP.get(algo)
            if mode:
                return mode

        # 2. User-supplied encryption algorithm
        if evidence.known_encryption_algo:
            enc = evidence.known_encryption_algo.lower()
            mode = self.KNOWN_ENCRYPTION_MAP.get(enc)
            if mode:
                return mode

        ext = evidence.ext

        # 3. Infer from file type
        if file_identifier.is_pdf(ext):
            # Default to modern PDF 1.7 if unsure
            return 10700

        office_class = file_identifier.classify_office(ext)
        if office_class == "office2013":
            return 9600
        elif office_class == "office2007":
            return 9400

        if ext == ".7z":
            return 11600

        if ext == ".zip" and zip_info:
            if zip_info == "aes":
                return 13600
            elif zip_info == "zipcrypto":
                return "USE_PKCRACK"

        # 4. Unknown → ask user
        mode = input(
            f"Unknown hash/encryption for {evidence.path}. "
            f"Enter Hashcat mode number (or blank to abort): "
        ).strip()
        if not mode:
            return None
        try:
            return int(mode)
        except ValueError:
            self.logger.error("Invalid Hashcat mode entered.")
            return None