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
            self.logger.info(f"Running Hashcat: {' '.join(cmd)}")

            try:
                # Capture bytes safely (no text=True)
                result = subprocess.run(cmd, check=True, capture_output=True)

                # Decode with fallback to prevent crashes
                stdout_str = result.stdout.decode('utf-8', errors='replace')
                stderr_str = result.stderr.decode('utf-8', errors='replace')

                # Log only if there's meaningful content
                if stdout_str.strip():
                    self.logger.debug(f"Hashcat stdout:\n{stdout_str.strip()}")
                if stderr_str.strip():
                    self.logger.debug(f"Hashcat stderr:\n{stderr_str.strip()}")

                self.logger.info(f"Hashcat completed on {hashfile} with {wordlist}")

                # Success criterion: potfile has content (cracked hashes appended)
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    self.logger.info(f"Hashcat succeeded → potfile updated: {output_path}")
                    return True
                else:
                    self.logger.info("No passwords cracked this run (potfile empty)")

            except subprocess.CalledProcessError as e:
                # Handle non-zero exit gracefully
                stdout_str = e.stdout.decode('utf-8', errors='replace') if e.stdout else ""
                stderr_str = e.stderr.decode('utf-8', errors='replace') if e.stderr else ""

                self.logger.warning(f"Hashcat failed (exit code {e.returncode}): {stderr_str.strip()}")
                if stdout_str.strip():
                    self.logger.debug(f"Hashcat stdout on failure:\n{stdout_str.strip()}")

            except Exception as e:
                self.logger.error(f"Unexpected error running Hashcat: {e}")

        self.logger.warning(f"Hashcat exhausted all wordlists for {hashfile}")
        return False

    def resolve_hashcat_mode(self, evidence, file_identifier, zip_info=None):
        if evidence.known_hash_algo:
            algo = evidence.known_hash_algo.lower()
            mode = self.KNOWN_HASH_MAP.get(algo)
            if mode is not None:
                return mode

        if evidence.known_encryption_algo:
            enc = evidence.known_encryption_algo.lower()
            mode = self.KNOWN_ENCRYPTION_MAP.get(enc)
            if mode is not None:
                return mode

        ext = evidence.ext

        if file_identifier.is_pdf(ext):
            return 10700  # Default modern PDF

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
            elif zip_info in ("zipcrypto", None):
                return "USE_PKCRACK"

        # Fallback prompt
        mode_str = input(
            f"Unknown mode for {evidence.path}. Enter Hashcat mode (integer) or blank to skip: "
        ).strip()
        if not mode_str:
            return None
        try:
            return int(mode_str)
        except ValueError:
            self.logger.error("Invalid mode entered.")
            return None
