import pytest
from internal import model


@pytest.mark.integration
@pytest.mark.api
class TestAccountAPIRegister:
    async def test_register_returns_201(
        self,
        test_client,
        mock_loom_authorization_client,
        api_headers
    ):
        # Arrange
        payload = {
            "login": "new_user",
            "password": "secure_password"
        }

        mock_loom_authorization_client.set_authorization_response(
            account_id=1,
            two_fa_status=False,
            role="employee",
            response=model.JWTTokens(
                access_token="test_access_token",
                refresh_token="test_refresh_token"
            )
        )

        # Act
        response = test_client.post("/register", json=payload, headers=api_headers)

        # Assert
        assert response.status_code == 201
        assert "account_id" in response.json()

        # Проверяем cookies
        assert "Access-Token" in response.cookies
        assert "Refresh-Token" in response.cookies


    async def test_register_duplicate_login_returns_error(
        self,
        test_client,
        mock_account_repo,
        test_account,
        api_headers
    ):
        # Arrange
        mock_account_repo.add_account(test_account)

        payload = {
            "login": test_account.login,
            "password": "password"
        }

        # Act
        response = test_client.post("/register", json=payload, headers=api_headers)

        # Assert
        # TODO: Проверить правильный код ошибки и формат
        assert response.status_code >= 400


@pytest.mark.integration
@pytest.mark.api
class TestAccountAPILogin:
    async def test_login_success(self, test_client):
        # TODO: Реализовать тест
        pass


    async def test_login_invalid_credentials(self, test_client):
        # TODO: Реализовать тест
        pass
