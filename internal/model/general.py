from dataclasses import dataclass
from typing import Optional


@dataclass
class AsyncWeedOperationResponse:
    status_code: int
    content: bytes
    content_type: str
    headers: dict
    fid: Optional[str] = None
    url: Optional[str] = None
    size: Optional[int] = None