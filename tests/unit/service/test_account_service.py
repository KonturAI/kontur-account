import pytest
from tests.utils.helpers import (
    setup_account_repo_find_by_login,
    setup_account_repo_create,
    setup_loom_auth_client_authorization,
    hash_password
)
from tests.utils.assertions import assert_authorization_dto

from internal import common


@pytest.mark.unit
class TestAccountServiceRegister:
    async def test_register_success(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        jwt_tokens,
        password_secret
    ):
        # Arrange
        login = "new_user"
        password = "secure_password"
        expected_account_id = 42

        setup_account_repo_find_by_login(mock_account_repo, not_found=True)
        setup_account_repo_create(mock_account_repo, account_id=expected_account_id)
        setup_loom_auth_client_authorization(mock_client=mock_loom_authorization_client, tokens=jwt_tokens)

        # Act
        result = await account_service.register(login, password)

        # Assert
        assert_authorization_dto(result, account_id=expected_account_id)
        assert result.access_token == jwt_tokens.access_token
        assert result.refresh_token == jwt_tokens.refresh_token

        mock_account_repo.account_by_login.assert_called_once_with(login=login)
        mock_account_repo.create_account.assert_called_once()

        call_args = mock_account_repo.create_account.call_args
        hashed_password = call_args.kwargs["password"]
        assert hashed_password != password, "Password should be hashed"

        mock_loom_authorization_client.authorization.assert_called_once_with(
            account_id=expected_account_id,
            two_fa_status=False,
            role="employee"
        )

    async def test_register_duplicate_login_raises_error(
        self,
        account_service,
        mock_account_repo,
        account
    ):
        # Arrange
        existing_login = account.login
        password = "password"

        setup_account_repo_find_by_login(mock_account_repo, account=account)

        # Act & Assert
        with pytest.raises(common.ErrAccountCreate):
            await account_service.register(existing_login, password)

        mock_account_repo.create_account.assert_not_called()

    async def test_register_password_is_hashed(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        password_secret
    ):
        # Arrange
        login = "user"
        plain_password = "my_password"

        setup_account_repo_find_by_login(mock_account_repo, not_found=True)
        setup_account_repo_create(mock_account_repo, account_id=1)
        setup_loom_auth_client_authorization(mock_loom_authorization_client)

        # Act
        await account_service.register(login, plain_password)

        # Assert
        call_args = mock_account_repo.create_account.call_args
        saved_password = call_args.kwargs["password"]

        assert saved_password != plain_password, "Password must be hashed"
        assert len(saved_password) > len(plain_password), "Hashed password should be longer"

    async def test_register_calls_authorization_with_correct_params(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        jwt_tokens
    ):
        # Arrange
        account_id = 123
        setup_account_repo_find_by_login(mock_account_repo, not_found=True)
        setup_account_repo_create(mock_account_repo, account_id=account_id)
        setup_loom_auth_client_authorization(mock_loom_authorization_client, tokens=jwt_tokens)

        # Act
        await account_service.register("user", "password")

        # Assert
        mock_loom_authorization_client.authorization.assert_called_once_with(
            account_id=account_id,
            two_fa_status=False,
            role="employee"
        )


@pytest.mark.unit
class TestAccountServiceLogin:
    async def test_login_success(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        account_factory,
        jwt_tokens,
        password_secret
    ):
        # Arrange
        plain_password = "correct_password"
        hashed = hash_password(plain_password, password_secret)

        test_account = account_factory(
            login="test_user",
            password=hashed,
            google_two_fa_key=""
        )

        setup_account_repo_find_by_login(mock_account_repo, account=test_account)
        setup_loom_auth_client_authorization(mock_loom_authorization_client, tokens=jwt_tokens)

        # Act
        result = await account_service.login(test_account.login, plain_password)

        # Assert
        assert result is not None
        assert_authorization_dto(result, account_id=test_account.id)
        assert result.access_token == jwt_tokens.access_token

    async def test_login_account_not_found_returns_none(
        self,
        account_service,
        mock_account_repo
    ):
        # Arrange
        setup_account_repo_find_by_login(mock_account_repo, not_found=True)

        # Act
        result = await account_service.login("nonexistent", "password")

        # Assert
        assert result is None

    async def test_login_invalid_password_returns_none(
        self,
        account_service,
        mock_account_repo,
        account_factory,
        password_secret
    ):
        # Arrange
        correct_password = "correct"
        wrong_password = "wrong"

        hashed = hash_password(correct_password, password_secret)
        test_account = account_factory(password=hashed)

        setup_account_repo_find_by_login(mock_account_repo, account=test_account)

        # Act
        result = await account_service.login(test_account.login, wrong_password)

        # Assert
        assert result is None
