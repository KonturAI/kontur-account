import pytest
from internal import model, common


@pytest.mark.unit
class TestAccountServiceRegister:
    async def test_register_success(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        test_jwt_tokens
    ):
        # Arrange
        login = "test_user"
        password = "test_password"
        expected_account_id = 1

        mock_loom_authorization_client.set_authorization_response(
            account_id=expected_account_id,
            two_fa_status=False,
            role="employee",
            response=test_jwt_tokens
        )

        # Act
        result = await account_service.register(login, password)

        # Assert
        assert isinstance(result, model.AuthorizationDataDTO)
        assert result.account_id == expected_account_id
        assert result.access_token == test_jwt_tokens.access_token
        assert result.refresh_token == test_jwt_tokens.refresh_token

        # Проверяем, что репо был вызван
        calls = mock_account_repo.get_call_history()
        assert len(calls) == 2  # account_by_login + create_account
        assert calls[1]["method"] == "create_account"
        assert calls[1]["login"] == login


    async def test_register_duplicate_login(
        self,
        account_service,
        mock_account_repo,
        test_account
    ):
        # Arrange
        mock_account_repo.add_account(test_account)

        # Act & Assert
        with pytest.raises(common.ErrAccountCreate):
            await account_service.register(test_account.login, "password")


@pytest.mark.unit
class TestAccountServiceLogin:
    async def test_login_success(
        self,
        account_service,
        mock_account_repo,
        test_account,
        test_password_secret
    ):
        # TODO: Реализовать тест
        pass


    async def test_login_account_not_found(self, account_service):
        # TODO: Реализовать тест
        pass


    async def test_login_invalid_password(self, account_service):
        # TODO: Реализовать тест
        pass
