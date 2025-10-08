import pytest
from internal import interface

from internal.controller.http.handler.account.handler import AccountController
from internal.service.account.service import AccountService
from internal.repo.account.repo import AccountRepo



# ============================================================================
# SERVICE LAYER
# ============================================================================

@pytest.fixture
def account_service(
    mock_telemetry,
    mock_account_repo,
    mock_loom_authorization_client,
    password_secret
):
    return AccountService(
        tel=mock_telemetry,
        account_repo=mock_account_repo,
        loom_authorization_client=mock_loom_authorization_client,
        password_secret_key=password_secret
    )


# ============================================================================
# REPOSITORY LAYER
# ============================================================================

@pytest.fixture
def account_repo(mock_telemetry, mock_db):
    return AccountRepo(
        tel=mock_telemetry,
        db=mock_db
    )


# ============================================================================
# CONTROLLER LAYER
# ============================================================================

@pytest.fixture
def mock_account_service(mocker):
    return mocker.AsyncMock(spec=interface.IAccountService)


@pytest.fixture
def account_controller(mock_telemetry, mock_account_service):
    return AccountController(
        tel=mock_telemetry,
        account_service=mock_account_service
    )
