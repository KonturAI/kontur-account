import pytest

from internal.service.account.service import AccountService
from internal.repo.account.repo import AccountRepo
from internal.controller.http.handler.account.handler import AccountController

@pytest.fixture
def account_service(
    mock_telemetry,
    mock_account_repo,
    mock_loom_authorization_client,
    test_password_secret
):
    return AccountService(
        tel=mock_telemetry,
        account_repo=mock_account_repo,
        loom_authorization_client=mock_loom_authorization_client,
        password_secret_key=test_password_secret
    )


@pytest.fixture
def account_repo(mock_telemetry, mock_db):
    return AccountRepo(
        tel=mock_telemetry,
        db=mock_db
    )

@pytest.fixture
def mock_account_service(mocker):
    from internal.interface import IAccountService
    return mocker.MagicMock(spec=IAccountService)


@pytest.fixture
def account_controller(mock_telemetry, mock_account_service):
    return AccountController(
        tel=mock_telemetry,
        account_service=mock_account_service
    )
