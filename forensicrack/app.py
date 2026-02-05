import os
import logging
import subprocess
from typing import List
import os
import logging
import subprocess
import shutil
from typing import List

from config import Config
from models import EvidenceFile
from file_id import FileIdentifier
from wordlists import WordlistManager
from steg import StegEngine
from steg_zsteg import ZstegEngine
from cracking_hashcat import HashcatEngine
from cracking_john import JohnEngine
from archives import ArchiveEngine


class ForensiCrackApp:
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.file_id = FileIdentifier()
        self.wordlist_mgr = WordlistManager(self.config.WORDLIST_DIR)
        self.steg_engine = StegEngine(logger)
        self.zsteg_engine = ZstegEngine(logger)
        self.hashcat_engine = HashcatEngine(logger)
        self.john_engine = JohnEngine(logger)
        self.archive_engine = ArchiveEngine(
            self.config.ARCHIVE_DIR, self.config.PLAINTEXTS_DIR, logger
        )
        self.processed_count = 0
        self.success_count = 0

    def execute(self):
        self.logger.info("ForensiCrack execution started")
        wordlists = self.wordlist_mgr.escalating_lists()
        if not wordlists:
            self.logger.error("No wordlists found in %s. Aborting.", self.config.WORDLIST_DIR)
            return

        self.logger.info("Using wordlists: %s", wordlists)

        for filename in os.listdir(self.config.INPUT_DIR):
            path = os.path.join(self.config.INPUT_DIR, filename)
            if not os.path.isfile(path):
                continue

            evidence = EvidenceFile(path=path)
            (
                evidence.file_type,
                evidence.mime_type,
                evidence.is_graphic,
                evidence.is_archive,
                evidence.is_text,  # now available
            ) = self.file_id.identify(path)

            self.logger.info("Processing: %s (%s)", evidence.name, evidence.ext)

            success = False

            if evidence.is_graphic:
                stego_output_dir = self.config.STEGO_OUTPUT_DIR
                if evidence.ext in {".jpg", ".jpeg"}:
                    success = self.steg_engine.run(path, wordlists, stego_output_dir)
                    if not success:
                        self.logger.info(
                            "Stegseek failed - falling back to zsteg for %s", evidence.name
                        )
                        success = self.zsteg_engine.run(path, stego_output_dir)
                elif evidence.ext in {".png", ".bmp"}:
                    success = self.zsteg_engine.run(path, stego_output_dir)

            elif evidence.is_archive:
                success = self._handle_archive(evidence, wordlists)

            elif evidence.ext in {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}:
                success = self._handle_encrypted_file(evidence, wordlists)

            elif evidence.ext == ".hash":
                success = self._handle_hash_file(evidence, wordlists)

            elif evidence.is_text:
                self.logger.info(
                    "Plain text file detected (%s) - no cracking applied, skipping", evidence.name
                )
                # Future: could add keyword search, entropy analysis, etc.

            else:
                self.logger.warning("Unsupported file type for %s - skipping", evidence.name)

            if success:
                self.success_count += 1
            self.processed_count += 1

        self.logger.info(
            "Execution complete. Processed %d files, %d successes.",
            self.processed_count,
            self.success_count,
        )

    def extract_hash(self, evidence: EvidenceFile) -> str | None:
        ext = evidence.ext.lower()
        hash_extract_path = os.path.join(self.config.CRACKED_OUTPUT_DIR, f"{evidence.name}.hash")

        tool_map = {
           ".zip": "zip2john",
           ".7z": "7z2john",
            ".rar": "rar2john",
            ".pdf": "pdf2john",
       }
        if ext in {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}:
            tool = "office2john"
        elif ext in tool_map:
              tool = tool_map[ext]
        else:
            self.logger.warning(f"No hash extraction tool for {ext}")
            return None

        if shutil.which(tool) is None:
            self.logger.error(f"Tool '{tool}' not found. Install john package.")
            return None
    
        cmd = [tool, evidence.path]
        self.logger.info(f"Extracting hash : {' '.john(cmd)} > {hash_extract_path}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True)
            hash_output = result.stdout.decode('utf-8', errors='replace').strip()
            if not hash_output:
                self.logger.error(f"Hash extraction produced no output for {evidence.name} (file may not be encrypted)")
                return None
            
            with open(hash_extract_path, "w") as f:
                f.write(hash_output)

            if os.path.getsize(hash_extract_path) == 0:
                self.logger.error(f"Hash extraction produced empty file for {evidence.name}")
                return None
            
            self.logger.info(f"Hash Extracted successfully: {hash_extract_path}")
            return hash_extract_path
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.decode('utf-8', errors='replace').strip() or "Unknown error"
            self.logger.error(f"Hash extraction failed for {evidence.name}: {err_msg}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during hash extraction for {evidence.name}: {e}")
            return None

      

    def _handle_archive(self, evidence: EvidenceFile, wordlists: List[str]) -> bool:
        zip_info = None
        if evidence.ext == ".zip":
            zip_info = self.archive_engine.detect_zip_encryption(evidence.path)

        mode = self.hashcat_engine.resolve_hashcat_mode(evidence, self.file_id, zip_info)

        if mode is None:
            self.logger.warning("Could not determine cracking mode for %s", evidence.name)
            return False

        output_path = os.path.join(self.config.CRACKED_OUTPUT_DIR, f"{evidence.name}.pot")

        if isinstance(mode, str) and mode == "USE_PKCRACK":
            decrypted_zip = os.path.join(
                self.config.EXTRACTED_OUTPUT_DIR, f"decrypted_{evidence.name}.zip"
            )
            success = self.archive_engine.run_bkcrack(evidence.path, decrypted_zip)
            if success:
                extracted_dir = self.archive_engine.extract_to_archive_dir(decrypted_zip)
                if extracted_dir:
                    self.logger.info(f"Decrypted archive extracted to: {extracted_dir}")
            return success

        else:
            # Extract hash first
            hash_path = self.extract_hash(evidence)
            if not hash_path:
                return False
            crack_target = hash_path

            # Try Hashcat first
            success = self.hashcat_engine.crack_hashfile(
                crack_target, mode, wordlists, output_path
            )
            if not success:
                self.logger.info(
                    "Hashcat failed - falling back to John for %s", evidence.name
                )
                success = self.john_engine.crack(crack_target, wordlists, output_path)

            if success:
                # Optional future: if password recovered, attempt auto-extraction
                # self.archive_engine.extract_to_archive_dir(evidence.path)
                pass
            return success

    def _handle_encrypted_file(self, evidence: EvidenceFile, wordlists: List[str]) -> bool:
        mode = self.hashcat_engine.resolve_hashcat_mode(evidence, self.file_id)
        if mode is None or isinstance(mode, str):
            self.logger.warning("Invalid mode for encrypted file %s", evidence.name)
            return False

        # Extract hash first
        hash_path = self.extract_hash(evidence)
        if not hash_path:
            return False
        crack_target = hash_path

        output_path = os.path.join(self.config.CRACKED_OUTPUT_DIR, f"{evidence.name}.pot")
        success = self.hashcat_engine.crack_hashfile(
            crack_target, mode, wordlists, output_path
        )
        if not success:
            success = self.john_engine.crack(crack_target, wordlists, output_path)
        return success

    def _handle_hash_file(self, evidence: EvidenceFile, wordlists: List[str]) -> bool:
        mode = self.hashcat_engine.resolve_hashcat_mode(evidence, self.file_id)
        if mode is None or isinstance(mode, str):
            self.logger.warning("Invalid mode for hash file %s", evidence.name)
            return False

        output_path = os.path.join(self.config.CRACKED_OUTPUT_DIR, f"{evidence.name}.pot")
        success = self.hashcat_engine.crack_hashfile(
            evidence.path, mode, wordlists, output_path
        )
        if not success:
            success = self.john_engine.crack(evidence.path, wordlists, output_path)
        return success
from .config import Config
from .models import EvidenceFile
from .file_id import FileIdentifier
from .wordlists import WordlistManager
from .steg import StegEngine
from .steg_zsteg import ZstegEngine
from .cracking_hashcat import HashcatEngine
from .cracking_john import JohnEngine
from .archives import ArchiveEngine


class ForensiCrackApp:
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.file_id = FileIdentifier()
        self.wordlist_mgr = WordlistManager(self.config.WORDLIST_DIR)
        self.steg_engine = StegEngine(logger)
        self.zsteg_engine = ZstegEngine(logger)
        self.hashcat_engine = HashcatEngine(logger)
        self.john_engine = JohnEngine(logger)
        self.archive_engine = ArchiveEngine(
            self.config.ARCHIVE_DIR, self.config.PLAINTEXTS_DIR, logger
        )
        self.processed_count = 0
        self.success_count = 0

    def execute(self):
        self.logger.info("ForensiCrack execution started")
        wordlists = self.wordlist_mgr.escalating_lists()
        if not wordlists:
            self.logger.error("No wordlists found in %s. Aborting.", self.config.WORDLIST_DIR)
            return

        self.logger.info("Using wordlists: %s", wordlists)

        for filename in os.listdir(self.config.INPUT_DIR):
            path = os.path.join(self.config.INPUT_DIR, filename)
            if not os.path.isfile(path):
                continue

            evidence = EvidenceFile(path=path)
            (
                evidence.file_type,
                evidence.mime_type,
                evidence.is_graphic,
                evidence.is_archive,
                evidence.is_text,  # now available
            ) = self.file_id.identify(path)

            self.logger.info("Processing: %s (%s)", evidence.name, evidence.ext)

            success = False

            if evidence.is_graphic:
                stego_output_dir = self.config.STEGO_OUTPUT_DIR
                if evidence.ext in {".jpg", ".jpeg"}:
                    success = self.steg_engine.run(path, wordlists, stego_output_dir)
                    if not success:
                        self.logger.info(
                            "Stegseek failed - falling back to zsteg for %s", evidence.name
                        )
                        success = self.zsteg_engine.run(path, stego_output_dir)
                elif evidence.ext in {".png", ".bmp"}:
                    success = self.zsteg_engine.run(path, stego_output_dir)

            elif evidence.is_archive:
                success = self._handle_archive(evidence, wordlists)

            elif evidence.ext in {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}:
                success = self._handle_encrypted_file(evidence, wordlists)

            elif evidence.ext == ".hash":
                success = self._handle_hash_file(evidence, wordlists)

            elif evidence.is_text:
                self.logger.info(
                    "Plain text file detected (%s) - no cracking applied, skipping", evidence.name
                )
                # Future: could add keyword search, entropy analysis, etc.

            else:
                self.logger.warning("Unsupported file type for %s - skipping", evidence.name)

            if success:
                self.success_count += 1
            self.processed_count += 1

        self.logger.info(
            "Execution complete. Processed %d files, %d successes.",
            self.processed_count,
            self.success_count,
        )

    def extract_hash(self, evidence: EvidenceFile) -> str | None:
        ext = evidence.ext.lower()
        hash_extract_path = os.path.join(self.config.CRACKED_OUTPUT_DIR, f"{evidence.name}.hash")

        if ext in {".zip", ".7z", ".rar"}:
            tool = "zip2john" if ext == ".zip" else "7z2john" if ext == ".7z" else "rar2john"
        elif ext == ".pdf":
            tool = "pdf2john"
        elif ext in {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}:
            tool = "office2john"
        else:
            self.logger.warning(f"No hash extraction tool for {ext}")
            return None

        cmd = [tool, evidence.path]
        self.logger.info(f"Extracting hash with {' '.join(cmd)}")
        try:
            with open(hash_extract_path, "w") as f:
                subprocess.run(cmd, check=True, stdout=f)
            self.logger.info(f"Hash extracted to {hash_extract_path}")
            return hash_extract_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Hash extraction failed: {e.stderr}")
            return None

    def _handle_archive(self, evidence: EvidenceFile, wordlists: List[str]) -> bool:
        zip_info = None
        if evidence.ext == ".zip":
            zip_info = self.archive_engine.detect_zip_encryption(evidence.path)

        mode = self.hashcat_engine.resolve_hashcat_mode(evidence, self.file_id, zip_info)

        if mode is None:
            self.logger.warning("Could not determine cracking mode for %s", evidence.name)
            return False

        output_path = os.path.join(self.config.CRACKED_OUTPUT_DIR, f"{evidence.name}.pot")

        if isinstance(mode, str) and mode == "USE_PKCRACK":
            decrypted_zip = os.path.join(
                self.config.EXTRACTED_OUTPUT_DIR, f"decrypted_{evidence.name}.zip"
            )
            success = self.archive_engine.run_bkcrack(evidence.path, decrypted_zip)
            if success:
                extracted_dir = self.archive_engine.extract_to_archive_dir(decrypted_zip)
                if extracted_dir:
                    self.logger.info(f"Decrypted archive extracted to: {extracted_dir}")
            return success

        else:
            # Extract hash first
            hash_path = self.extract_hash(evidence)
            if not hash_path:
                return False
            crack_target = hash_path

            # Try Hashcat first
            success = self.hashcat_engine.crack_hashfile(
                crack_target, mode, wordlists, output_path
            )
            if not success:
                self.logger.info(
                    "Hashcat failed - falling back to John for %s", evidence.name
                )
                success = self.john_engine.crack(crack_target, wordlists, output_path)

            if success:
                # Optional future: if password recovered, attempt auto-extraction
                # self.archive_engine.extract_to_archive_dir(evidence.path)
                pass
            return success

    def _handle_encrypted_file(self, evidence: EvidenceFile, wordlists: List[str]) -> bool:
        mode = self.hashcat_engine.resolve_hashcat_mode(evidence, self.file_id)
        if mode is None or isinstance(mode, str):
            self.logger.warning("Invalid mode for encrypted file %s", evidence.name)
            return False

        # Extract hash first
        hash_path = self.extract_hash(evidence)
        if not hash_path:
            return False
        crack_target = hash_path

        output_path = os.path.join(self.config.CRACKED_OUTPUT_DIR, f"{evidence.name}.pot")
        success = self.hashcat_engine.crack_hashfile(
            crack_target, mode, wordlists, output_path
        )
        if not success:
            success = self.john_engine.crack(crack_target, wordlists, output_path)
        return success

    def _handle_hash_file(self, evidence: EvidenceFile, wordlists: List[str]) -> bool:
        mode = self.hashcat_engine.resolve_hashcat_mode(evidence, self.file_id)
        if mode is None or isinstance(mode, str):
            self.logger.warning("Invalid mode for hash file %s", evidence.name)
            return False

        output_path = os.path.join(self.config.CRACKED_OUTPUT_DIR, f"{evidence.name}.pot")
        success = self.hashcat_engine.crack_hashfile(
            evidence.path, mode, wordlists, output_path
        )
        if not success:
            success = self.john_engine.crack(evidence.path, wordlists, output_path)
        return success
