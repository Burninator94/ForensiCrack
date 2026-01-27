import os
import zipfile
import subprocess
import logging
import shutil


class ArchiveEngine:
    def __init__(self, archive_dir: str, plaintexts_dir: str, logger: logging.Logger | None = None):
        self.archive_dir = archive_dir
        self.plaintexts_dir = plaintexts_dir
        os.makedirs(self.archive_dir, exist_ok=True)
        os.makedirs(self.plaintexts_dir, exist_ok=True)
        self.logger = logger or logging.getLogger("ForensiCrack.Archive")

    def detect_zip_encryption(self, zip_path: str) -> str | None:
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                for zinfo in zf.infolist():
                    if zinfo.flag_bits & 0x1:
                        return "zipcrypto"
        except zipfile.BadZipFile as e:
            self.logger.error(f"Bad zip {zip_path}: {e}")
        return None

    def find_matching_plaintext(self, encrypted_zip: str) -> tuple[str | None, str | None]:
        try:
            with zipfile.ZipFile(encrypted_zip, "r") as zf:
                encrypted_files = {info.filename for info in zf.infolist() if info.flag_bits & 0x1}
        except Exception as e:
            self.logger.error(f"Cannot read encrypted ZIP {encrypted_zip}: {e}")
            return None, None

        for root, _, files in os.walk(self.plaintexts_dir):
            for fname in files:
                if fname in encrypted_files:
                    full_path = os.path.join(root, fname)
                    self.logger.info(f"Found known plaintext match: {full_path} → {fname}")
                    return full_path, fname
        self.logger.warning(f"No filename match found in {self.plaintexts_dir}")
        return None, None

    def run_bkcrack(self, encrypted_zip: str, output_zip: str) -> bool:
        plaintext_path, internal_name = self.find_matching_plaintext(encrypted_zip)
        if not plaintext_path or not internal_name:
            self.logger.error("Cannot run bkcrack: no matching known plaintext")
            return False

        cmd = [
            "bkcrack",
            "-C", encrypted_zip,
            "-c", internal_name,
            "-P", plaintext_path,
            "-p", internal_name,
            "-d", output_zip
        ]
        self.logger.info(f"Running bkcrack: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info(f"bkcrack succeeded → {output_zip}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"bkcrack failed: {e.stderr}")
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