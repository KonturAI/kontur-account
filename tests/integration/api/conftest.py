import pytest
from fastapi.testclient import TestClient

from internal.app.http.app import NewHTTP
from internal.controller.http.handler.account.handler import AccountController
from internal.controller.http.middlerware.middleware import HttpMiddleware
from internal.service.account.service import AccountService


@pytest.fixture
def test_password_secret() -> str:
    return "test_api_secret_key"


@pytest.fixture
def test_client(
    test_db,
    tel,
    test_account_repo,
    mock_loom_authorization_client,
    test_password_secret,
    log_context
):
    account_service = AccountService(
        tel=tel,
        account_repo=test_account_repo,
        loom_authorization_client=mock_loom_authorization_client,
        password_secret_key=test_password_secret
    )

    account_controller = AccountController(
        tel=tel,
        account_service=account_service
    )

    http_middleware = HttpMiddleware(
        tel=tel,
        loom_authorization_client=mock_loom_authorization_client,
        prefix="/api/account",
        log_context=log_context
    )

    app = NewHTTP(
        db=test_db,
        account_controller=account_controller,
        http_middleware=http_middleware,
        prefix="/api/account"
    )

    return TestClient(app)


@pytest.fixture
def api_headers():
    return {
        "Content-Type": "application/json"
    }
