import pytest
from fastapi.testclient import TestClient

from internal.app.http.app import NewHTTP
from internal.controller.http.handler.account.handler import AccountController
from internal.controller.http.middlerware.middleware import HttpMiddleware
from internal.service.account.service import AccountService


@pytest.fixture
def test_client(
    db,
    mock_tel,
    account_repo,
    mock_loom_authorization_client,
    password_secret,
    log_context
):
    account_service = AccountService(
        tel=mock_tel,
        account_repo=account_repo,
        loom_authorization_client=mock_loom_authorization_client,
        password_secret_key=password_secret
    )

    account_controller = AccountController(
        tel=mock_tel,
        account_service=account_service
    )

    http_middleware = HttpMiddleware(
        tel=mock_tel,
        loom_authorization_client=mock_loom_authorization_client,
        prefix="/api/account",
        log_context=log_context
    )

    app = NewHTTP(
        db=db,
        account_controller=account_controller,
        http_middleware=http_middleware,
        prefix="/api/account"
    )

    return TestClient(app)
