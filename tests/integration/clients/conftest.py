import pytest
import respx
from httpx import Response

from pkg.client.internal.loom_authorization.client import LoomAuthorizationClient


@pytest.fixture
def respx_mock():
    with respx.mock:
        yield respx


@pytest.fixture
def loom_authorization_client(mock_telemetry, log_context):
    return LoomAuthorizationClient(
        tel=mock_telemetry,
        host="localhost",
        port=8080,
        log_context=log_context
    )


@pytest.fixture
def mock_authorization_response():
    def _create_response(access_token: str = "test_access", refresh_token: str = "test_refresh"):
        return Response(
            status_code=200,
            json={
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        )
    return _create_response


@pytest.fixture
def mock_check_authorization_response():
    def _create_response(
        account_id: int = 1,
        two_fa_status: bool = False,
        role: str = "employee"
    ):
        return Response(
            status_code=200,
            json={
                "account_id": account_id,
                "two_fa_status": two_fa_status,
                "role": role,
                "message": "OK",
                "status_code": 200
            }
        )
    return _create_response
