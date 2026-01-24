import os
import subprocess
import logging


class StegEngine:
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("ForensiCrack.Steg")

    def run(self, filepath: str, wordlists: list[str], output_dir: str) -> bool:
        os.makedirs(output_dir, exist_ok=True)

        for wordlist in wordlists:
            cmd = ["stegseek", filepath, wordlist, "crack", output_dir]
            self.logger.info(f"Running stegseek: {' '.join(cmd)}")
            result = subprocess.run(cmd)
            if result.returncode == 0:
                self.logger.info(f"Steg success on {filepath} with {wordlist}")
                return True

        self.logger.warning(f"Steg failed for {filepath}")
        return False
