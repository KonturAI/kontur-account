import bcrypt
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock
from internal import model


# ============================================================================
# PASSWORD HELPERS
# ============================================================================

def hash_password(password: str, secret_key: str = "test_secret") -> str:
    peppered_password = secret_key + password
    hashed_password = bcrypt.hashpw(peppered_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def make_hashed_account(
    login: str,
    password: str,
    secret_key: str = "test_secret",
    **kwargs
) -> model.Account:

    from tests.factories.account_factory import AccountFactory
    hashed = hash_password(password, secret_key)
    return AccountFactory(login=login, password=hashed, **kwargs)


# ============================================================================
# DB HELPERS
# ============================================================================

class DBRow:
    def __init__(self, **fields):
        for key, value in fields.items():
            setattr(self, key, value)

    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"DBRow({fields})"


def make_db_row(**fields) -> DBRow:
    return DBRow(**fields)


def create_mock_db_row(**kwargs) -> Any:
    return make_db_row(**kwargs)


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


# ============================================================================
# MOCK SETUP HELPERS
# ============================================================================

def setup_account_repo_find_by_login(
    mock_repo: AsyncMock,
    account: Optional[model.Account] = None,
    not_found: bool = False
) -> None:
    if not_found:
        mock_repo.account_by_login.return_value = []
    elif account:
        mock_repo.account_by_login.return_value = [account]
    else:
        mock_repo.account_by_login.return_value = []


def setup_account_repo_create(
    mock_repo: AsyncMock,
    account_id: int = 1
) -> None:
    mock_repo.create_account.return_value = account_id


def setup_loom_auth_client_authorization(
    mock_client: AsyncMock,
    tokens: Optional[model.JWTTokens] = None,
    access_token: str = "test_access",
    refresh_token: str = "test_refresh"
) -> None:
    if tokens:
        mock_client.authorization.return_value = tokens
    else:
        mock_client.authorization.return_value = model.JWTTokens(
            access_token=access_token,
            refresh_token=refresh_token
        )


