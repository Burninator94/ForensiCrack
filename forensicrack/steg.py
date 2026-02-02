import os
import subprocess
import logging


class StegEngine:
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("ForensiCrack.Steg")

    def run(self, filepath: str, wordlists: list[str], output_dir: str) -> bool:
        os.makedirs(output_dir, exist_ok=True)

        for wordlist in wordlists:
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            output_file = os.path.join(output_dir, f"{base_name}_extracted.out")

            cmd = ["stegseek", filepath, wordlist, output_file]
            self.logger.info(f"Running stegseek: {' '.join(cmd)}")
            result = subprocess.run(cmd)
            if result.returncode == 0:
                self.logger.info(f"Steg success on {filepath} with {wordlist} → {output_file}")
                return True

        self.logger.warning(f"Steg failed for {filepath}")
        return False
