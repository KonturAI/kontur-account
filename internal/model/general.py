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
class AuthorizationDataDTO:
    account_id: int
    access_token: str
    refresh_token: str


class AuthorizationData(BaseModel):
    account_id: int
    message: str
    code: int


class JWTTokens(BaseModel):
    access_token: str
    refresh_token: str
