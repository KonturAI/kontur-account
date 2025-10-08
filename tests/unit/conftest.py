import pytest
from internal import interface


@pytest.fixture
def mock_account_service(mocker) -> interface.IAccountService:
    return mocker.AsyncMock(spec=interface.IAccountService)


@pytest.fixture
def account_controller(
        mock_telemetry: interface.ITelemetry,
        mock_account_service: interface.IAccountService
) -> interface.IAccountController:
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
        mock_telemetry: interface.ITelemetry,
        mock_account_repo: interface.IAccountRepo,
        mock_loom_authorization_client: interface.ILoomAuthorizationClient,
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
        mock_telemetry: interface.ITelemetry,
        mock_db: interface.IDB
) -> interface.IAccountRepo:
    from internal.repo.account.repo import AccountRepo
    return AccountRepo(
        tel=mock_telemetry,
        db=mock_db
    )

# ============================================================================
# CONTROLLER LAYER - мокируем services
# ============================================================================
