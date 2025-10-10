import pytest

from internal import interface
from internal.controller.http.handler.account.handler import AccountController
from internal.service.account.service import AccountService
from internal.repo.account.repo import AccountRepo


@pytest.fixture
def mock_db(mocker):
    return mocker.AsyncMock(spec=interface.IDB)


@pytest.fixture
def mock_account_repo(mocker):
    return mocker.AsyncMock(spec=interface.IAccountRepo)


@pytest.fixture
def mock_account_service(mocker):
    return mocker.AsyncMock(spec=interface.IAccountService)


@pytest.fixture
def account_service(
        mock_tel,
        mock_account_repo,
        mock_loom_authorization_client,
        password_secret
):
    return AccountService(
        tel=mock_tel,
        account_repo=mock_account_repo,
        loom_authorization_client=mock_loom_authorization_client,
        password_secret_key=password_secret
    )


@pytest.fixture
def account_repo(mock_tel, mock_db):
    return AccountRepo(
        tel=mock_tel,
        db=mock_db
    )


@pytest.fixture
def account_controller(mock_tel, mock_account_service):
    return AccountController(
        tel=mock_tel,
        account_service=mock_account_service
    )
