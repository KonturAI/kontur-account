from unittest.mock import AsyncMock, Mock
from internal import model


def assert_authorization_dto(
    dto: model.AuthorizationDataDTO,
    account_id: int = None
) -> None:
    assert dto is not None, "AuthorizationDataDTO must not be None"
    assert dto.access_token, "Access token must not be empty"
    assert dto.refresh_token, "Refresh token must not be empty"

    if account_id is not None:
        assert dto.account_id == account_id, (
            f"Account ID: {dto.account_id} != {account_id}"
        )


# ============================================================================
# MOCK ASSERTIONS
# ============================================================================

def assert_mock_call_count(mock: Mock | AsyncMock, expected_count: int) -> None:
    """
    Проверить количество вызовов мока.

    Пример:
        assert_mock_call_count(mock_repo.create_account, 2)
    """
    actual_count = mock.call_count
    assert actual_count == expected_count, (
        f"Expected {expected_count} calls, got {actual_count}"
    )