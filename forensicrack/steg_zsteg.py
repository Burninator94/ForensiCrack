import os
import subprocess
import logging


class ZstegEngine:
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("ForensiCrack.Zsteg")

    def run(self, filepath: str, output_dir: str) -> bool:
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        output_file = os.path.join(output_dir, f"{base_name}_zsteg.txt")

        cmd = ["zsteg", "-a", filepath]
        self.logger.info(f"Running zsteg: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            output = result.stdout.strip()
            if "nothing to extract" in output.lower() or not output:
                self.logger.info(f"No hidden data found in {filepath}")
                return False

            with open(output_file, "w") as f:
                f.write(output)
            self.logger.info(f"zsteg extraction saved: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"zsteg failed: {e.stderr}")
            return False
