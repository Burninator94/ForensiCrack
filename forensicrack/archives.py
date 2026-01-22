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
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                for zinfo in zf.infolist():
                    if zinfo.flag_bits & 0x1:
                        # Encrypted; simplistic detection
                        return "zipcrypto"  # refine later if needed
        except zipfile.BadZipFile as e:
            self.logger.error(f"Bad zip {zip_path}: {e}")
        return None

    def run_pkcrack(self, encrypted_zip: str, plaintext_zip: str, plaintext_file: str, output_zip: str) -> bool:
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
        try:
            subprocess.run(cmd, check=True)
            self.logger.info(f"pkcrack succeeded → {output_zip}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"pkcrack failed: {e}")
            return False

    def extract_to_archive_dir(self, zip_path: str) -> str:
        base = os.path.basename(zip_path)
        name, _ = os.path.splitext(base)
        out_dir = os.path.join(self.archive_dir, name)
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir, ignore_errors=True)
        os.makedirs(out_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(out_dir)
            self.logger.info(f"Extracted {zip_path} → {out_dir}")
            return out_dir
        except Exception as e:
            self.logger.error(f"Extraction failed for {zip_path}: {e}")
            return ""