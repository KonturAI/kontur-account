import pytest
import respx
from httpx import Response

from internal import model


@pytest.mark.integration
@pytest.mark.client
@pytest.mark.slow
class TestLoomAuthorizationClient:

    async def test_authorization_success(
        self,
        loom_authorization_client,
        mock_authorization_response
    ):
        account_id = 10001
        two_fa_status = False
        role = "employee"

        respx.post("http://localhost:8080/api/authorization").mock(
            return_value=mock_authorization_response()
        )

        result = await loom_authorization_client.authorization(
            account_id=account_id,
            two_fa_status=two_fa_status,
            role=role
        )

        assert result.access_token == "test_access_token"
        assert result.refresh_token == "test_refresh_token"

    async def test_authorization_tg_success(
        self,
        loom_authorization_client,
        mock_authorization_response
    ):
        account_id = 10001
        two_fa_status = False
        role = "employee"

        respx.post("http://localhost:8080/api/authorization/tg").mock(
            return_value=mock_authorization_response(
                access_token="tg_access_token",
                refresh_token="tg_refresh_token"
            )
        )

        result = await loom_authorization_client.authorization_tg(
            account_id=account_id,
            two_fa_status=two_fa_status,
            role=role
        )

        assert result.access_token == "tg_access_token"
        assert result.refresh_token == "tg_refresh_token"

    async def test_check_authorization_success(
        self,
        loom_authorization_client,
        mock_check_authorization_response
    ):
        access_token = "valid_token"

        respx.get("http://localhost:8080/api/authorization/check").mock(
            return_value=mock_check_authorization_response(account_id=10123)
        )

        result = await loom_authorization_client.check_authorization(access_token)

        assert result.account_id == 10123
        assert result.two_fa_status is False
        assert result.role == "employee"
        assert result.status_code == 200

    async def test_authorization_with_2fa_enabled(
        self,
        loom_authorization_client,
        mock_authorization_response
    ):
        account_id = 10001
        two_fa_status = True
        role = "employee"

        respx.post("http://localhost:8080/api/authorization").mock(
            return_value=mock_authorization_response()
        )

        result = await loom_authorization_client.authorization(
            account_id=account_id,
            two_fa_status=two_fa_status,
            role=role
        )

        assert result.access_token == "test_access_token"
        assert result.refresh_token == "test_refresh_token"

    async def test_authorization_handles_server_error(
        self,
        loom_authorization_client
    ):
        account_id = 10001

        respx.post("http://localhost:8080/api/authorization").mock(
            return_value=Response(status_code=500, json={"error": "Internal Server Error"})
        )

        with pytest.raises(Exception):
            await loom_authorization_client.authorization(
                account_id=account_id,
                two_fa_status=False,
                role="employee"
            )

    async def test_check_authorization_with_invalid_token(
        self,
        loom_authorization_client
    ):
        access_token = "invalid_token"

        respx.get("http://localhost:8080/api/authorization/check").mock(
            return_value=Response(
                status_code=401,
                json={
                    "account_id": 0,
                    "two_fa_status": False,
                    "role": "",
                    "message": "Unauthorized",
                    "status_code": 401
                }
            )
        )

        result = await loom_authorization_client.check_authorization(access_token)

        assert result.status_code == 401
        assert result.message == "Unauthorized"
