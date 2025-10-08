import pytest
from datetime import datetime


@pytest.mark.integration
@pytest.mark.repo
class TestAccountRepoIntegration:
    async def test_create_and_retrieve_account(
        self,
        test_account_repo
    ):
        # Arrange
        login = "integration_test_user"
        password = "hashed_password_123"

        # Act - создаем аккаунт
        account_id = await test_account_repo.create_account(login, password)

        # Assert - проверяем, что ID был возвращен
        assert account_id > 0

        # Act - получаем аккаунт по ID
        accounts = await test_account_repo.account_by_id(account_id)

        # Assert - проверяем данные
        assert len(accounts) == 1
        account = accounts[0]
        assert account.id == account_id
        assert account.login == login
        assert account.password == password
        assert account.google_two_fa_key == ""
        assert isinstance(account.created_at, datetime)


    async def test_update_two_fa_key(
        self,
        test_account_repo
    ):
        """
        ПРИМЕР: Установка и удаление 2FA ключа
        """
        # Arrange - создаем аккаунт
        login = "user_with_2fa"
        password = "password"
        account_id = await test_account_repo.create_account(login, password)

        # Act - устанавливаем 2FA ключ
        two_fa_key = "SECRET_KEY_123456"
        await test_account_repo.set_two_fa_key(account_id, two_fa_key)

        # Assert - проверяем, что ключ установлен
        accounts = await test_account_repo.account_by_id(account_id)
        assert accounts[0].google_two_fa_key == two_fa_key

        # Act - удаляем 2FA ключ
        await test_account_repo.delete_two_fa_key(account_id)

        # Assert - проверяем, что ключ удален
        accounts = await test_account_repo.account_by_id(account_id)
        assert accounts[0].google_two_fa_key == ""


    async def test_account_by_login(
        self,
        test_account_repo
    ):
        """
        ПРИМЕР: Поиск аккаунта по логину
        """
        # TODO: Реализовать тест
        pass


    async def test_update_password(
        self,
        test_account_repo
    ):
        """
        ПРИМЕР: Обновление пароля
        """
        # TODO: Реализовать тест
        pass
