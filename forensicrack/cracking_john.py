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
            result = subprocess.run(cmd)
            if result.returncode == 0:
                self.logger.info(f"John succeeded on {hashfile} with {wordlist}")
                return True

        self.logger.warning(f"John failed for {hashfile}")
        return False