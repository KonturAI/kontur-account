from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel


@dataclass
class AsyncWeedOperationResponse:
    status_code: int
    content: bytes
    content_type: str
    headers: dict
    fid: Optional[str] = None
    url: Optional[str] = None
    size: Optional[int] = None

@dataclass
class AuthorizationData:
    account_id: int
    access_token: str
    refresh_token: str

class JWTTokens(BaseModel):
    access_token: str
    refresh_token: str