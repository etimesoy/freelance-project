from dataclasses import dataclass
from io import BytesIO


@dataclass
class FileInfo:
    content: BytesIO
    name: str
    content_type: str
