import pytest

from internal import model
from tests import utils
from tests.factories.auth_factory import JWTTokensFactory


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.slow
@pytest.mark.auth
class TestAccountAPIRegister:

    async def test_register_returns_201_with_valid_data(
        self,
        test_client,
        mock_loom_authorization_client,
        api_headers
    ):
        payload = {
            "login": "new_user_123",
            "password": "secure_password_123"
        }

        tokens = JWTTokensFactory()
        utils.setup_loom_auth_client_authorization(mock_loom_authorization_client, tokens=tokens)

        response = test_client.post("/register", json=payload, headers=api_headers)

        assert response.status_code == 201
        data = response.json()
        assert "account_id" in data
        assert data["account_id"] > 0

        assert "Access-Token" in response.cookies
        assert "Refresh-Token" in response.cookies

    async def test_register_with_duplicate_login_returns_error(
        self,
        test_client,
        account_repo,
        api_headers
    ):
        login = "existing_user_456"
        password = "password123"

        existing_account = utils.make_hashed_account(login=login, password=password)
        await account_repo.create_account(existing_account.login, existing_account.password)

        payload = {
            "login": login,
            "password": "another_password"
        }

        response = test_client.post("/register", json=payload, headers=api_headers)

        assert response.status_code >= 400

    async def test_register_with_invalid_payload_returns_422(
        self,
        test_client,
        api_headers
    ):
        invalid_payloads = [
            {},
            {"login": "only_login"},
            {"password": "only_password"},
            {"login": "", "password": "password"},
            {"login": "user", "password": ""},
        ]

        for payload in invalid_payloads:
            response = test_client.post("/register", json=payload, headers=api_headers)
            assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.slow
@pytest.mark.auth
@pytest.mark.password
class TestAccountAPILogin:

    async def test_login_with_valid_credentials_returns_200(
        self,
        test_client,
        account_repo,
        mock_loom_authorization_client,
        api_headers,
        password_secret
    ):
        login = "test_user_login"
        password = "test_password"

        hashed_account = utils.make_hashed_account(login=login, password=password, secret_key=password_secret)
        await account_repo.create_account(hashed_account.login, hashed_account.password)

        tokens = JWTTokensFactory()
        utils.setup_loom_auth_client_authorization(mock_loom_authorization_client, tokens=tokens)

        payload = {
            "login": login,
            "password": password
        }

        response = test_client.post("/login", json=payload, headers=api_headers)

        assert response.status_code == 200
        assert "Access-Token" in response.cookies
        assert "Refresh-Token" in response.cookies

    async def test_login_with_invalid_credentials_returns_401(
        self,
        test_client,
        account_repo,
        api_headers,
        password_secret
    ):
        login = "existing_user_789"
        correct_password = "correct_password"
        wrong_password = "wrong_password"

        hashed_account = utils.make_hashed_account(login=login, password=correct_password, secret_key=password_secret)
        await account_repo.create_account(hashed_account.login, hashed_account.password)

        payload = {
            "login": login,
            "password": wrong_password
        }

        response = test_client.post("/login", json=payload, headers=api_headers)

        assert response.status_code == 401

    async def test_login_with_nonexistent_account_returns_404(
        self,
        test_client,
        api_headers
    ):
        payload = {
            "login": "nonexistent_user_999",
            "password": "some_password"
        }

        response = test_client.post("/login", json=payload, headers=api_headers)

        assert response.status_code == 404

    async def test_login_with_missing_fields_returns_422(
        self,
        test_client,
        api_headers
    ):
        invalid_payloads = [
            {},
            {"login": "only_login"},
            {"password": "only_password"},
        ]

        for payload in invalid_payloads:
            response = test_client.post("/login", json=payload, headers=api_headers)
            assert response.status_code == 422
