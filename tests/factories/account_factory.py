from datetime import datetime
from typing import Optional

from internal import model


class AccountFactory:
    _counter = 0

    @classmethod
    def _get_next_id(cls) -> int:
        cls._counter += 1
        return cls._counter

    @classmethod
    def reset_counter(cls) -> None:
        cls._counter = 0

    @classmethod
    def create(
        cls,
        id: Optional[int] = None,
        login: Optional[str] = None,
        password: str = "hashed_password_123",
        google_two_fa_key: str = "",
        created_at: Optional[datetime] = None,
    ) -> model.Account:
        if id is None:
            id = cls._get_next_id()

        if login is None:
            login = f"test_user_{id}"

        if created_at is None:
            created_at = datetime.now()

        return model.Account(
            id=id,
            login=login,
            password=password,
            google_two_fa_key=google_two_fa_key,
            created_at=created_at,
        )

    @classmethod
    def create_with_2fa(
        cls,
        google_two_fa_key: str = "JBSWY3DPEHPK3PXP",
        **kwargs
    ) -> model.Account:
        return cls.create(google_two_fa_key=google_two_fa_key, **kwargs)

    @classmethod
    def create_batch(cls, count: int, **kwargs) -> list[model.Account]:
        return [cls.create(**kwargs) for _ in range(count)]
