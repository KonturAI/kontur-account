import pytest
from internal import interface


@pytest.fixture
def mock_account_service(mocker):
    return mocker.AsyncMock(spec=interface.IAccountService)


@pytest.fixture
def account_controller(
        mock_telemetry,
        mock_account_service
):
    from internal.controller.http.handler.account.handler import AccountController
    return AccountController(
        tel=mock_telemetry,
        account_service=mock_account_service
    )


# ============================================================================
# SERVICE LAYER - мокируем repo + clients
# ============================================================================

@pytest.fixture
def account_service(
        mock_telemetry,
        mock_account_repo,
        mock_loom_authorization_client,
        password_secret: str
):
    from internal.service.account.service import AccountService
    return AccountService(
        tel=mock_telemetry,
        account_repo=mock_account_repo,
        loom_authorization_client=mock_loom_authorization_client,
        password_secret_key=password_secret
    )


# ============================================================================
# REPOSITORY LAYER - мокируем DB
# ============================================================================

@pytest.fixture
def account_repo(
        mock_telemetry,
        mock_db
):
    from internal.repo.account.repo import AccountRepo
    return AccountRepo(
        tel=mock_telemetry,
        db=mock_db
    )

# ============================================================================
# CONTROLLER LAYER - мокируем services
# ============================================================================
