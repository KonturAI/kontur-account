from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


@dataclass
class Account:
    id: int

    login: int
    password: int

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> List['Account']:
        return [
            cls(
                id=row.id,
                login=row.login,
                password=row.password,
                created_at=row.created_at
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "login": self.login,
            "password": self.password,
            "created_at": self.created_at.isoformat()
        }