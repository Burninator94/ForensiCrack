import mimetypes
import os


class FileIdentifier:
    GRAPHIC_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
    ARCHIVE_EXT = {".zip", ".7z"}
    PDF_EXT = {".pdf"}
    OFFICE_EXT = {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}
    TEXT_EXT = {".txt"}

    def identify(self, path: str):
        ext = os.path.splitext(path)[1].lower()
        mime, _ = mimetypes.guess_type(path)
        is_graphic = ext in self.GRAPHIC_EXT
        is_archive = ext in self.ARCHIVE_EXT
        is_text = ext in self.TEXT_EXT
        return ext, mime or "", is_graphic, is_archive, is_text

    def classify_office(self, ext: str) -> str | None:
        if ext in self.OFFICE_EXT:
            if ext in {".docx", ".xlsx", ".pptx"}:
                return "office2013"
            else:
                return "office2007"
        return None

    def is_pdf(self, ext: str) -> bool:
        return ext in self.PDF_EXT
