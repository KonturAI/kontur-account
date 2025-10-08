from typing import Optional
from unittest.mock import AsyncMock

from internal import model


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
