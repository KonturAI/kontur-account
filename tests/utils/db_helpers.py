from typing import Any, Dict, List

from internal import model


class DBRow:
    def __init__(self, **fields: Any) -> None:
        for key, value in fields.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        fields = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"DBRow({fields})"


def make_db_row(**fields: Any) -> DBRow:
    return DBRow(**fields)


def make_db_rows(data: List[Dict[str, Any]]) -> List[DBRow]:
    return [DBRow(**row_data) for row_data in data]


def account_to_db_row(account: model.Account) -> DBRow:
    return DBRow(
        id=account.id,
        login=account.login,
        password=account.password,
        google_two_fa_key=account.google_two_fa_key,
        created_at=account.created_at
    )
