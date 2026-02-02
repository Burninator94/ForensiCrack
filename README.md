# ForensiCrack

DFIR File Recovery Tool

ForensiCrack is a modular, scalable, and professional‑grade Digital Forensics and Incident Response (DFIR) cracking orchestrator designed to automate the recovery of encrypted, password‑protected, or steganographically hidden artifacts discovered during forensic investigations.
The tool evolved from an earlier prototype (JailBreak_Tool), originally built for a NICE Challenge scenario. While the pilot tool automated a fixed workflow for a contrived environment, ForensiCrack expands the concept into a realistic, extensible, and investigator‑driven framework suitable for DFIR labs, academic exercises, and CTF environments.
ForensiCrack integrates with standard forensic workflows (e.g., Autopsy entropy scanning) and provides a unified interface for orchestrating multiple cracking engines, wordlist escalation, and evidence‑safe processing.

## Legal & Ethical Use Statement

# Must Read

ForensiCrack is developed exclusively for lawful Digital Forensics and Incident Response (DFIR) workflows, academic research, and Capture‑the‑Flag (CTF) environments. It is designed to support investigators, students, and security professionals in recovering encrypted or hidden data during authorized examinations. Any attempt to use this tool for unauthorized access, data theft, system intrusion, or circumventing security controls is strictly prohibited. Misuse of ForensiCrack may violate federal and state laws, institutional policies, and professional ethical standards. The developers do not condone, support, or accept responsibility for any unlawful or unethical use of this software. By downloading, installing, or operating ForensiCrack, the user acknowledges that they are solely responsible for ensuring their actions comply with all applicable laws, regulations, and organizational requirements, and that any consequences arising from misuse rest entirely with the user.

# Program Class Organization:

forensicrack/
/app.py                # Main application orchestrator
/config.py             # Centralized configuration and runtime paths
/file_id.py            # File identification and triage logic
/wordlists.py          # Wordlist manager and escalation logic
/cracking_hashcat.py   # Hashcat engine wrapper
/cracking_john.py      # John the Ripper engine wrapper
/steg.py               # Stegseek engine wrapper
/steg_zsteg.py         # zsteg engine wrapper
/archives.py           # Archive cracking and recursion engine
/install.py            # Debian/Kali-only installer
/init.py               # Package initializer

# Runtime Directories (Auto-Generated During Install)

runtime/
/input/        # Investigator-provided files to crack
/output/       # Successfully cracked results
  /stego       # stegseek &zsteg extractions
  /cracked     # .pot files from hashcat/john
  /extracted   # decrypted zips from bkcrack
/logs/         # Operational logs
/archives/     # Extracted or intermediate archive contents
/wordlists/    # Required wordlists (brockyou.txt and passphrases.txt)
/plaintexts/   # known plaintext files from ZipCrypto attack

# Installation

ForensiCrack v1 officially supports Debian/Kali Linux

1. Clone the main branch repository
2. install 'requests' module from Python
3. Run the installer: sudo python3 forensicrack.py --install
This should create all runtime directories, install required tools via apt, build and install bkcrack from source (if needed), download the passphrases.txt wordlist automatically, and self-validate completion

# Setup

Download brockyou.txt at ( https://mega.nz/file/cr5HGACC#ANXlTyu8sdlIUizcIX418sa1C2M4Ame_3bjxU9xXGfY ) and add to wordlist directory

# Dependency Tools

1. Hashcat - GPU/CPU password cracking engine ( https://hashcat.net/hashcat/ )
2. John the Ripper - CPU-based password crack with broad support ( https://www.openwall.com/john/ )
3. Stegseek - Fast steganography brute-forcer for JPEGs ( https://github.com/RickdeJager/stegseek )
4. zsteg - Steganography brute-forcer with wider media file support ( https://github.com/zed-0xff/zsteg )
5. bkcrack - Known plaintext attack tool for legacy Zip encryption ( https://github.com/kimci86/bkcrack )
6. passphrases.txt - expanded passphrase wordlist ( https://github.com/initstring/passphrase-wordlist/releases )

# Operation

1. Place files in the input directory (/runtime/input/)
   If using bkcrack to launch known-plaintext attack, ensure the plaintext file is located within /plaintexts subdirectory
2. Run ForensiCrack
  python3 forensicrack.py --execute
3. Review results in /output/, /logs/, and /archives/ directories
