from typing import Optional
from unittest.mock import AsyncMock

from internal import model


def setup_account_repo_find_by_login(
    mock_repo: AsyncMock,
    account: Optional[model.Account] = None,
    not_found: bool = False
) -> AsyncMock:
    if not_found:
        mock_repo.account_by_login.return_value = []
    elif account:
        mock_repo.account_by_login.return_value = [account]
    else:
        mock_repo.account_by_login.return_value = []
    return mock_repo


def setup_account_repo_find_by_id(
    mock_repo: AsyncMock,
    account: Optional[model.Account] = None,
    not_found: bool = False
) -> AsyncMock:
    if not_found:
        mock_repo.account_by_id.return_value = []
    elif account:
        mock_repo.account_by_id.return_value = [account]
    else:
        mock_repo.account_by_id.return_value = []
    return mock_repo


def setup_account_repo_create(
    mock_repo: AsyncMock,
    account_id: int = 10001
) -> AsyncMock:
    mock_repo.create_account.return_value = account_id
    return mock_repo


def setup_account_repo_update_password(
    mock_repo: AsyncMock
) -> AsyncMock:
    mock_repo.update_password.return_value = None
    return mock_repo


def setup_account_repo_set_two_fa_key(
    mock_repo: AsyncMock
) -> AsyncMock:
    mock_repo.set_two_fa_key.return_value = None
    return mock_repo


def setup_account_repo_delete_two_fa_key(
    mock_repo: AsyncMock
) -> AsyncMock:
    mock_repo.delete_two_fa_key.return_value = None
    return mock_repo


def setup_loom_auth_client_authorization(
    mock_client: AsyncMock,
    tokens: Optional[model.JWTTokens] = None,
    access_token: str = "test_access_token",
    refresh_token: str = "test_refresh_token"
) -> AsyncMock:
    if tokens:
        mock_client.authorization.return_value = tokens
    else:
        mock_client.authorization.return_value = model.JWTTokens(
            access_token=access_token,
            refresh_token=refresh_token
        )
    return mock_client


def setup_loom_auth_client_authorization_tg(
    mock_client: AsyncMock,
    tokens: Optional[model.JWTTokens] = None,
    access_token: str = "test_tg_access_token",
    refresh_token: str = "test_tg_refresh_token"
) -> AsyncMock:
    if tokens:
        mock_client.authorization_tg.return_value = tokens
    else:
        mock_client.authorization_tg.return_value = model.JWTTokens(
            access_token=access_token,
            refresh_token=refresh_token
        )
    return mock_client
