import os
import subprocess
import logging


class HashcatEngine:
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("ForensiCrack.Hashcat")

        # NOTE: Keep keys lowercase because resolve_hashcat_mode() lowercases inputs
        self.KNOWN_HASH_MAP = {
            "ntlm": 1000,
            "7-zip": 11600,
            "winzip": 13600,
            "pkzip (compressed)": 17200,
            "pkzip (uncompressed)": 17210,
            "pkzip (compressed multi-file)": 17220,
            "pkzip (mixed multi-file)": 17225,
            "pkzip (multi-file checksum-only)": 17230,
            "pkzip master key": 20500,
            "pkzip master key (6 bytes)": 20510,
            "sha256 (sha256($pass).$salt))": 207010,
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
            # common plain hashes if upstream passes these labels
            "md5": 0,
            "sha1": 100,
        }

        self.KNOWN_ENCRYPTION_MAP = {
            "zipcrypto": "USE_PKCRACK",
            "aes-zip": 13600,
            "aes": 13600,
            "aes-7zip": 11600,
            "7zip-aes": 11600,
            "pkzip (compressed)": 17200,
            "pkzip (uncompressed)": 17210,
            "pkzip (compressed multi-file)": 17220,
            "pkzip (mixed multi-file)": 17225,
            "pkzip (multi-file checksum-only)": 17230,
            "pkzip master key": 20500,
            "pkzip master key (6 bytes)": 20510,
            "sha256 (sha256($pass).$salt))": 207010,
            "office2007": 9400,
            "office2010": 9500,
            "office2013": 9600,
            "pdf14": 10500,
            "pdf17": 10700,
            "pdf20": 10710,
        }

    # ----------------------------
    # Hashcat cracking (FIXED)
    # ----------------------------
    def crack_hashfile(self, hashfile: str, hash_type_code: int, wordlists: list[str], output_path: str) -> bool:
        """
        FIXES:
        - Do NOT treat --outfile as a "pot" file.
        - Use a dedicated per-target hashcat potfile so --show is reliable.
        - Do NOT use check=True (hashcat exit codes are nuanced).
        - Log BOTH stdout and stderr on failures (hashcat often prints to stdout).
        - Determine success by running `hashcat --show` and finding real hash:plain lines.
        """
        out_dir = os.path.dirname(output_path) or "."
        os.makedirs(out_dir, exist_ok=True)

        # Dedicated potfile for hashcat ONLY (never share with John)
        pot_path = output_path + ".hashcat.pot"

        def _decode(b: bytes | None) -> str:
            return b.decode("utf-8", errors="replace") if b else ""

        def _filter_show_lines(show_text: str) -> list[str]:
            lines: list[str] = []
            for line in (show_text or "").splitlines():
                s = line.strip()
                if not s:
                    continue
                low = s.lower()
                # Drop hashcat informational headers that confused your GUI before
                if "the following" in low and "hash-modes" in low:
                    continue
                if "hash-modes match the structure" in low:
                    continue
                if low.startswith(("hashcat", "usage:", "session", "started", "warning:", "error:")):
                    continue
                # outfile-format 2 is typically "hash:plain" (hash might include colons for some modes)
                if ":" in s and not s.endswith(":"):
                    lines.append(s)
            return lines

        def _run_show() -> list[str]:
            show_cmd = [
                "hashcat",
                "--show",
                "-m", str(hash_type_code),
                "--outfile-format", "2",
                "--potfile-path", pot_path,
                hashfile,
            ]
            self.logger.info(f"Hashcat show: {' '.join(show_cmd)}")
            res = subprocess.run(show_cmd, capture_output=True)
            out = _decode(res.stdout)
            err = _decode(res.stderr)
            if err.strip():
                self.logger.debug(f"Hashcat --show stderr:\n{err.strip()}")
            return _filter_show_lines(out)

        for wordlist in wordlists:
            cmd = [
                "hashcat",
                "-m", str(hash_type_code),
                "-a", "0",
                hashfile,
                wordlist,
                "--potfile-path", pot_path,
                "--outfile", output_path,
                "--outfile-format", "2",
                "--quiet",
                "--force",
            ]
            self.logger.info(f"Running Hashcat: {' '.join(cmd)}")

            try:
                res = subprocess.run(cmd, capture_output=True)

                stdout_str = _decode(res.stdout).strip()
                stderr_str = _decode(res.stderr).strip()

                # Hashcat often prints useful info to stdout; log both at debug.
                if stdout_str:
                    self.logger.debug(f"Hashcat stdout:\n{stdout_str}")
                if stderr_str:
                    self.logger.debug(f"Hashcat stderr:\n{stderr_str}")

                # Always decide success by --show results (not by exit code)
                show_lines = _run_show()
                if show_lines:
                    # Write filtered results so the rest of your app can read one predictable file
                    with open(output_path, "w", encoding="utf-8", errors="replace") as f:
                        f.write("\n".join(show_lines) + "\n")

                    self.logger.info(f"Hashcat succeeded → wrote {len(show_lines)} result line(s): {output_path}")
                    self.logger.info(f"Hashcat completed on {hashfile} with {wordlist}")
                    return True

                # No cracks for this wordlist
                self.logger.info(f"No passwords cracked this run for {hashfile} with {wordlist} (exit {res.returncode})")

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
            elif zip_info == "zipcrypto":
                return "USE_PKCRACK"
            else:
                self.logger.warning(f"Unknown ZIP encryption type for {evidence.path} - assuming AES")
                return 13600

        # --- GUI-safe / non-interactive mode resolution ---
        import sys
        import re
        from pathlib import Path

        p = evidence.path
        p_str = p if isinstance(p, str) else str(p)
        fname = Path(p_str).name.lower()

        # Allow filename tags like: target__m0.hash, dump_m1000.hash, hashes-m22000.txt
        m = re.search(r'(?:^|[_\-.])m(\d+)(?:[_\-.]|$)', fname)
        if m:
            return int(m.group(1))

        # If running under GUI/non-interactive, do NOT prompt (prevents EOFError)
        if not sys.stdin or not sys.stdin.isatty():
            return None

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
