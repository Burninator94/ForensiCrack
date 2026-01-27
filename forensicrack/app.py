import os
import logging
from typing import List

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
            # Try Hashcat first
            success = self.hashcat_engine.crack_hashfile(
                evidence.path, mode, wordlists, output_path
            )
            if not success:
                self.logger.info(
                    "Hashcat failed - falling back to John for %s", evidence.name
                )
                success = self.john_engine.crack(evidence.path, wordlists, output_path)

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

        output_path = os.path.join(self.config.CRACKED_OUTPUT_DIR, f"{evidence.name}.pot")
        success = self.hashcat_engine.crack_hashfile(
            evidence.path, mode, wordlists, output_path
        )
        if not success:
            success = self.john_engine.crack(evidence.path, wordlists, output_path)
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
