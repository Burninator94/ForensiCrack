import os
import zipfile
import subprocess
import logging
import shutil


class ArchiveEngine:
    def __init__(self, archive_dir: str, logger: logging.Logger | None = None):
        self.archive_dir = archive_dir
        os.makedirs(self.archive_dir, exist_ok=True)
        self.logger = logger or logging.getLogger("ForensiCrack.Archive")

    def detect_zip_encryption(self, zip_path: str) -> str | None:
        """
        Very basic heuristic: if any ZipInfo flag bit 0 (encrypted) set.
        Distinguishing ZipCrypto vs AES properly is more involved; here we assume:
        - If encrypted and not obviously AES, treat as ZipCrypto.
        """
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                for zinfo in zf.infolist():
                    if zinfo.flag_bits & 0x1:
                        # Encrypted, but Python's zipfile doesn't expose AES detail.
                        # We'll default to ZipCrypto assumption; you can later refine with external tools.
                        return "zipcrypto"
        except zipfile.BadZipFile as e:
            self.logger.error(f"Bad zip file {zip_path}: {e}")
        return None

    def run_pkcrack(self, encrypted_zip: str, plaintext_zip: str, plaintext_file: str, output_zip: str) -> bool:
        """
        Run pkcrack on a ZipCrypto archive using known plaintext.
        """
        out_dir = os.path.dirname(output_zip)
        os.makedirs(out_dir, exist_ok=True)

        cmd = [
            "pkcrack",
            "-C", encrypted_zip,
            "-c", plaintext_file,
            "-P", plaintext_zip,
            "-p", plaintext_file,
            "-d", output_zip
        ]
        self.logger.info(f"Running pkcrack: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode == 0:
            self.logger.info(f"pkcrack succeeded on {encrypted_zip}")
            return True

        self.logger.warning(f"pkcrack failed on {encrypted_zip}")
        return False

    def extract_to_archive_dir(self, zip_path: str) -> str:
        """
        Extract zip to a dedicated subdirectory under archive_dir.
        """
        base = os.path.basename(zip_path)
        name, _ = os.path.splitext(base)
        out_dir = os.path.join(self.archive_dir, name)
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(out_dir)
                self.logger.info(f"Extracted {zip_path} to {out_dir}")
        except zipfile.BadZipFile as e:
            self.logger.error(f"Failed to extract {zip_path}: {e}")
        return out_dir