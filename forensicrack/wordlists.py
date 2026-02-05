import os
import gzip
import shutil
import logging
import subprocess
import sys
import glob


class WordlistManager:
    def __init__(self, wordlist_dir: str):
        self.wordlist_dir = wordlist_dir
        self.logger = logging.getLogger("ForensiCrack.Wordlists")

        # Standard wordlists
        self.brockyou = os.path.join(wordlist_dir, "brockyou.txt")
        self.passphrases = os.path.join(wordlist_dir, "passphrases.txt")

        # RockYou2021 paths
        self.rockyou2021_txt = os.path.join(wordlist_dir, "rockyou2021.txt")
        self.rockyou_parts_pattern = os.path.join(wordlist_dir, "RockYou2021.7z.*")  # matches .001, .002, etc.

    def _check_disk_space(self, required_gb=150):
        """Check available disk space before extraction."""
        try:
            stat = shutil.disk_usage(self.wordlist_dir)
            free_gb = stat.free // (1024 ** 3)
            if free_gb < required_gb:
                print(f"\nWARNING: Only ~{free_gb} GB free on disk. Extraction needs ~{required_gb} GB.")
                print("Risk of disk full! Continue anyway? (Y/N): ", end="")
                if input().strip().lower() not in ('y', 'yes'):
                    self.logger.info("User cancelled due to low disk space.")
                    return False
            return True
        except Exception as e:
            self.logger.warning(f"Could not check disk space: {e}")
            return True  # continue anyway if check fails

    def _extract_rockyou2021_parts(self):
        """Extract multi-part 7z archive if parts exist and output doesn't."""
        if os.path.exists(self.rockyou2021_txt):
            self.logger.info("RockYou2021.txt already extracted.")
            return self.rockyou2021_txt

        # Find all parts (*.001, .002, etc.)
        parts = sorted(glob.glob(self.rockyou_parts_pattern))
        if not parts:
            self.logger.warning("No RockYou2021.7z.* parts found.")
            print("RockYou2021 multi-part archive not found.")
            print("Download from: https://mega.nz/folder/aDpmxCiD#f_pSJ0vV698-Ev1mbyYNAQ")
            print("Place all parts in runtime/wordlists/ and re-run.")
            return None

        first_part = parts[0]
        part_count = len(parts)
        print(f"\nFound {part_count} RockYou2021 parts. First: {os.path.basename(first_part)}")

        # Interactive warning
        warning_msg = f"""
┌────────────────────────────────────────────────────────────────────────────┐
│                  RockYou2021 Wordlist Warning                              │
├────────────────────────────────────────────────────────────────────────────┤
│ This wordlist contains ~8.4 BILLION unique passwords (~100–140 GB         │
│ uncompressed). Extracting requires at least 150 GB free disk space.       │
│                                                                            │
│ Performance note:                                                          │
│ - Fast hashes (MD5, NTLM): minutes to hours on a good GPU                 │
│ - Slow hashes (bcrypt, WPA2-PBKDF2, RAR5): months to years                │
│ - Use rules (-r), masks, or hybrid attacks for realistic results          │
│ - Strong GPU + good cooling recommended (high TDP, sustained load)        │
└────────────────────────────────────────────────────────────────────────────┘

Found {part_count} parts. Do you want to extract RockYou2021 now? (Y/N): """

        print(warning_msg, end="")
        sys.stdout.flush()
        response = input().strip().lower()

        if response not in ('y', 'yes'):
            self.logger.info("User declined RockYou2021 extraction.")
            print("Extraction cancelled. RockYou2021 will not be used.")
            return None

        # Disk space check
        if not self._check_disk_space():
            print("Extraction cancelled due to insufficient disk space.")
            return None

        print("Extracting multi-part 7z archive... (this may take 10–60 minutes)")
        self.logger.info(f"Extracting from {first_part} to {self.wordlist_dir}")

        try:
            cmd = ["7za", "e", first_part, f"-o{self.wordlist_dir}", "-y"]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.debug(f"7za output:\n{result.stdout}")
            print("Extraction complete.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Extraction failed: {e.stderr}")
            print(f"Extraction error:\n{e.stderr}")
            return None
        except FileNotFoundError:
            self.logger.error("7za command not found. Install: sudo apt install p7zip-full")
            print("Error: 7za not found. Run: sudo apt install p7zip-full")
            return None

        # Find the extracted .txt file (handle possible name variations)
        possible_names = ["rockyou2021.txt", "RockYou2021.txt", "rockyou.txt"]
        extracted_txt = None
        for name in possible_names:
            candidate = os.path.join(self.wordlist_dir, name)
            if os.path.exists(candidate):
                extracted_txt = candidate
                break

        if extracted_txt:
            # Rename to standard name if needed
            if extracted_txt != self.rockyou2021_txt:
                shutil.move(extracted_txt, self.rockyou2021_txt)
                extracted_txt = self.rockyou2021_txt
            self.logger.info(f"RockYou2021 extracted successfully: {extracted_txt}")
            return extracted_txt
        else:
            self.logger.warning("Could not find extracted rockyou2021.txt.")
            print("Warning: rockyou2021.txt not found after extraction.")
            print("Check files in wordlists/ manually.")
            return None

    def escalating_lists(self):
        lists = []

        if os.path.exists(self.brockyou):
            lists.append(self.brockyou)
        if os.path.exists(self.passphrases):
            lists.append(self.passphrases)

        # Trigger RockYou2021 extraction only when needed
        rockyou_path = self._extract_rockyou2021_parts()
        if rockyou_path:
            lists.append(rockyou_path)

        return lists
