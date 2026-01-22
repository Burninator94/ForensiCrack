import os
import subprocess
import logging


class JohnEngine:
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("ForensiCrack.John")

    def crack(self, hashfile: str, wordlists: list[str], output_path: str) -> bool:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        for wordlist in wordlists:
            cmd = [
                "john",
                f"--wordlist={wordlist}",
                hashfile,
                f"--pot={output_path}",
            ]
            self.logger.info(f"Running John: {' '.join(cmd)}")
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                self.logger.info(f"John succeeded on {hashfile} with {wordlist}")
                self.logger.debug(result.stdout)
                return True
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"John attempt failed: {e.stderr}")

        self.logger.warning(f"John exhausted all wordlists for {hashfile}")
        return False