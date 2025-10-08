import pytest
import respx


@pytest.mark.integration
@pytest.mark.client
class TestLoomAuthorizationClient:
    async def test_authorization_success(
        self,
        loom_authorization_client,
        mock_authorization_response
    ):
        # Arrange
        account_id = 1
        two_fa_status = False
        role = "employee"

        # Мокируем HTTP запрос
        respx.post("http://localhost:8080/api/authorization").mock(
            return_value=mock_authorization_response()
        )

        # Act
        result = await loom_authorization_client.authorization(
            account_id=account_id,
            two_fa_status=two_fa_status,
            role=role
        )

        # Assert
        assert result.access_token == "test_access"
        assert result.refresh_token == "test_refresh"


    async def test_authorization_tg_success(
        self,
        loom_authorization_client,
        mock_authorization_response
    ):
        # Arrange
        account_id = 1
        two_fa_status = False
        role = "employee"

        # Мокируем HTTP запрос
        respx.post("http://localhost:8080/api/authorization/tg").mock(
            return_value=mock_authorization_response(
                access_token="tg_access",
                refresh_token="tg_refresh"
            )
        )

        # Act
        result = await loom_authorization_client.authorization_tg(
            account_id=account_id,
            two_fa_status=two_fa_status,
            role=role
        )

        # Assert
        assert result.access_token == "tg_access"
        assert result.refresh_token == "tg_refresh"


    async def test_check_authorization_success(
        self,
        loom_authorization_client,
        mock_check_authorization_response
    ):
        # Arrange
        access_token = "valid_token"

        # Мокируем HTTP запрос
        respx.get("http://localhost:8080/api/authorization/check").mock(
            return_value=mock_check_authorization_response(account_id=123)
        )

        # Act
        result = await loom_authorization_client.check_authorization(access_token)

        # Assert
        assert result.account_id == 123
        assert result.two_fa_status is False
        assert result.role == "employee"
        assert result.status_code == 200


    async def test_authorization_with_2fa(self, loom_authorization_client):
        # TODO: Реализовать тест
        pass


    async def test_authorization_handles_errors(self, loom_authorization_client):
        # TODO: Реализовать тест
        pass
