import os
from dataclasses import dataclass, field


@dataclass
class EvidenceFile:
    path: str
    file_type: str = ""
    mime_type: str = ""
    is_graphic: bool = False
    is_archive: bool = False

    known_hash_algo: str | None = None
    known_encryption_algo: str | None = None

    metadata: dict = field(default_factory=dict)

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def ext(self):
        return os.path.splitext(self.path)[1].lower()