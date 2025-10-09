import pytest

from internal import common
from internal.repo.account.sql_query import (
    create_account,
    get_account_by_id,
    get_account_by_login,
    set_two_fa_key,
    delete_two_fa_key,
    update_password,
)
from tests.factories import AccountFactory


class TestAccountRepoCreateAccount:
    async def test_create_account_success(self, account_repo, mock_db):
        # Arrange
        login = "test_user"
        password = "hashed_password"
        expected_account_id = 42

        # Mock that account doesn't exist
        mock_db.select.return_value = []
        mock_db.insert.return_value = expected_account_id

        # Act
        result = await account_repo.create_account(login, password)

        # Assert
        assert result == expected_account_id

        # Verify SQL query and arguments are correct
        mock_db.select.assert_called_once_with(
            get_account_by_login,
            {'login': login}
        )
        mock_db.insert.assert_called_once_with(
            create_account,
            {'login': login, 'password': password}
        )

    async def test_create_account_duplicate_login(self, account_repo, mock_db):
        # Arrange
        login = "existing_user"
        password = "hashed_password"

        existing_account = AccountFactory.create(login=login)

        # Mock that account already exists
        mock_db.select.return_value = [existing_account]

        # Act & Assert
        with pytest.raises(common.ErrAccountCreate):
            await account_repo.create_account(login, password)

        # Verify select was called but insert was not
        mock_db.select.assert_called_once_with(
            get_account_by_login,
            {'login': login}
        )
        mock_db.insert.assert_not_called()

    @pytest.mark.parametrize("login,password", [
        pytest.param("", "hashed_password", id="empty_login"),
        pytest.param("user", "", id="empty_password"),
        pytest.param("", "", id="both_empty"),
    ])
    async def test_create_account_empty_credentials(
        self, account_repo, mock_db, login, password
    ):
        # Arrange
        expected_account_id = 10

        mock_db.select.return_value = []
        mock_db.insert.return_value = expected_account_id

        # Act
        result = await account_repo.create_account(login, password)

        # Assert
        assert result == expected_account_id
        mock_db.insert.assert_called_once_with(
            create_account,
            {'login': login, 'password': password}
        )

    async def test_create_account_select_returns_none(self, account_repo, mock_db):
        # Arrange
        login = "test_user"
        password = "hashed_password"
        expected_account_id = 42

        mock_db.select.return_value = []
        mock_db.insert.return_value = expected_account_id

        # Act
        result = await account_repo.create_account(login, password)

        # Assert
        assert result == expected_account_id


class TestAccountRepoCreateAccountErrorHandling:
    async def test_create_account_select_db_error(self, account_repo, mock_db):
        # Arrange
        mock_db.select.side_effect = Exception("Database connection lost")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await account_repo.create_account("user", "pass")

        assert "Database connection lost" in str(exc_info.value)
        mock_db.insert.assert_not_called()

    async def test_create_account_insert_db_error(self, account_repo, mock_db):
        # Arrange
        mock_db.select.return_value = []
        mock_db.insert.side_effect = Exception("Constraint violation")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await account_repo.create_account("user", "pass")

        assert "Constraint violation" in str(exc_info.value)


class TestAccountRepoAccountById:
    async def test_account_by_id_found(self, account_repo, mock_db):
        # Arrange
        account_id = 123
        expected_account = AccountFactory.create(
            id=account_id,
            login="test_user",
            google_two_fa_key="secret_key"
        )

        mock_db.select.return_value = [expected_account]

        # Act
        result = await account_repo.account_by_id(account_id)

        # Assert
        assert len(result) == 1
        assert result[0].id == account_id
        assert result[0].login == "test_user"
        assert result[0].google_two_fa_key == "secret_key"

        mock_db.select.assert_called_once_with(
            get_account_by_id,
            {'account_id': account_id}
        )

    async def test_account_by_id_not_found(self, account_repo, mock_db):
        # Arrange
        account_id = 999
        mock_db.select.return_value = []

        # Act
        result = await account_repo.account_by_id(account_id)

        # Assert
        assert result == []
        mock_db.select.assert_called_once_with(
            get_account_by_id,
            {'account_id': account_id}
        )

    async def test_account_by_id_none_result(self, account_repo, mock_db):
        # Arrange
        account_id = 456
        mock_db.select.return_value = []

        # Act
        result = await account_repo.account_by_id(account_id)

        # Assert
        assert result == []
        mock_db.select.assert_called_once_with(
            get_account_by_id,
            {'account_id': account_id}
        )

    async def test_account_by_id_multiple_results(self, account_repo, mock_db):
        # Arrange
        account_id = 100
        accounts = AccountFactory.create_batch(2, id=account_id)

        mock_db.select.return_value = accounts

        # Act
        result = await account_repo.account_by_id(account_id)

        # Assert
        assert len(result) == 2

    async def test_account_by_id_db_error(self, account_repo, mock_db):
        # Arrange
        mock_db.select.side_effect = Exception("Database timeout")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await account_repo.account_by_id(123)

        assert "Database timeout" in str(exc_info.value)


class TestAccountRepoAccountByLogin:
    async def test_account_by_login_found(self, account_repo, mock_db):
        # Arrange
        login = "test_user"
        expected_account = AccountFactory.create(login=login)

        mock_db.select.return_value = [expected_account]

        # Act
        result = await account_repo.account_by_login(login)

        # Assert
        assert len(result) == 1
        assert result[0].login == login

        mock_db.select.assert_called_once_with(
            get_account_by_login,
            {'login': login}
        )

    async def test_account_by_login_not_found(self, account_repo, mock_db):
        # Arrange
        login = "nonexistent_user"
        mock_db.select.return_value = []

        # Act
        result = await account_repo.account_by_login(login)

        # Assert
        assert result == []
        mock_db.select.assert_called_once_with(
            get_account_by_login,
            {'login': login}
        )

    async def test_account_by_login_none_result(self, account_repo, mock_db):
        # Arrange
        login = "test_user"
        mock_db.select.return_value = []

        # Act
        result = await account_repo.account_by_login(login)

        # Assert
        assert result == []

    @pytest.mark.parametrize("login", [
        pytest.param("", id="empty"),
        pytest.param("  ", id="whitespace"),
        pytest.param("test_user", id="lowercase"),
        pytest.param("Test_User", id="mixed_case"),
        pytest.param("TEST_USER", id="uppercase"),
    ])
    async def test_account_by_login_various_formats(self, account_repo, mock_db, login):
        # Arrange
        expected_account = AccountFactory.create(login=login)
        mock_db.select.return_value = [expected_account]

        # Act
        result = await account_repo.account_by_login(login)

        # Assert
        assert len(result) == 1
        assert result[0].login == login
        mock_db.select.assert_called_once_with(
            get_account_by_login,
            {'login': login}
        )

    async def test_account_by_login_db_error(self, account_repo, mock_db):
        # Arrange
        mock_db.select.side_effect = Exception("Connection refused")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await account_repo.account_by_login("test_user")

        assert "Connection refused" in str(exc_info.value)


class TestAccountRepoSetTwoFaKey:
    async def test_set_two_fa_key_success(self, account_repo, mock_db):
        # Arrange
        account_id = 100
        google_two_fa_key = "JBSWY3DPEHPK3PXP"

        mock_db.update.return_value = None

        # Act
        await account_repo.set_two_fa_key(account_id, google_two_fa_key)

        # Assert
        mock_db.update.assert_called_once_with(
            set_two_fa_key,
            {
                'account_id': account_id,
                'google_two_fa_key': google_two_fa_key
            }
        )

    async def test_set_two_fa_key_empty_key(self, account_repo, mock_db):
        # Arrange
        account_id = 100
        google_two_fa_key = ""

        mock_db.update.return_value = None

        # Act
        await account_repo.set_two_fa_key(account_id, google_two_fa_key)

        # Assert
        mock_db.update.assert_called_once_with(
            set_two_fa_key,
            {
                'account_id': account_id,
                'google_two_fa_key': google_two_fa_key
            }
        )

    async def test_set_two_fa_key_overwrite_existing(self, account_repo, mock_db):
        # Arrange
        account_id = 100
        new_key = "NEWKEY123456"

        mock_db.update.return_value = None

        # Act
        await account_repo.set_two_fa_key(account_id, new_key)

        # Assert
        mock_db.update.assert_called_once()

    async def test_set_two_fa_key_db_error(self, account_repo, mock_db):
        # Arrange
        mock_db.update.side_effect = Exception("Update failed")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await account_repo.set_two_fa_key(100, "KEY123")

        assert "Update failed" in str(exc_info.value)


class TestAccountRepoDeleteTwoFaKey:
    async def test_delete_two_fa_key_success(self, account_repo, mock_db):
        # Arrange
        account_id = 100

        mock_db.update.return_value = None

        # Act
        await account_repo.delete_two_fa_key(account_id)

        # Assert
        mock_db.update.assert_called_once_with(
            delete_two_fa_key,
            {'account_id': account_id}
        )

    async def test_delete_two_fa_key_idempotent(self, account_repo, mock_db):
        # Arrange
        account_id = 100
        mock_db.update.return_value = None

        # Act
        await account_repo.delete_two_fa_key(account_id)
        await account_repo.delete_two_fa_key(account_id)

        # Assert
        assert mock_db.update.call_count == 2

    async def test_delete_two_fa_key_db_error(self, account_repo, mock_db):
        # Arrange
        mock_db.update.side_effect = Exception("Deadlock detected")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await account_repo.delete_two_fa_key(100)

        assert "Deadlock detected" in str(exc_info.value)


class TestAccountRepoUpdatePassword:
    async def test_update_password_success(self, account_repo, mock_db):
        # Arrange
        account_id = 100
        new_password = "new_hashed_password"

        mock_db.update.return_value = None

        # Act
        await account_repo.update_password(account_id, new_password)

        # Assert
        mock_db.update.assert_called_once_with(
            update_password,
            {
                'account_id': account_id,
                'new_password': new_password
            }
        )

    async def test_update_password_same_password(self, account_repo, mock_db):
        # Arrange
        account_id = 100
        new_password = "same_hashed_password"

        mock_db.update.return_value = None

        # Act
        await account_repo.update_password(account_id, new_password)

        # Assert
        mock_db.update.assert_called_once()

    @pytest.mark.parametrize("password", [
        pytest.param("", id="empty"),
        pytest.param("a" * 1000, id="very_long"),
        pytest.param("pass with spaces", id="with_spaces"),
        pytest.param("пароль", id="unicode"),
    ])
    async def test_update_password_edge_cases(
        self, account_repo, mock_db, password
    ):
        # Arrange
        account_id = 100
        mock_db.update.return_value = None

        # Act
        await account_repo.update_password(account_id, password)

        # Assert
        mock_db.update.assert_called_once_with(
            update_password,
            {
                'account_id': account_id,
                'new_password': password
            }
        )

    async def test_update_password_db_error(self, account_repo, mock_db):
        # Arrange
        mock_db.update.side_effect = Exception("Connection lost")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await account_repo.update_password(100, "new_pass")

        assert "Connection lost" in str(exc_info.value)


class TestAccountRepoLifecycle:
    async def test_full_account_lifecycle(self, account_repo, mock_db):
        # Create account
        login = "lifecycle_user"
        password = "initial_pass"
        account_id = 42

        mock_db.select.return_value = []
        mock_db.insert.return_value = account_id

        created_id = await account_repo.create_account(login, password)
        assert created_id == account_id

        # Read account
        account = AccountFactory.create(id=account_id, login=login)
        mock_db.select.return_value = [account]

        found_accounts = await account_repo.account_by_login(login)
        assert len(found_accounts) == 1
        assert found_accounts[0].id == account_id

        # Update password
        mock_db.update.return_value = None
        await account_repo.update_password(account_id, "new_pass")

        # Set 2FA
        await account_repo.set_two_fa_key(account_id, "2FA_KEY")

        # Delete 2FA
        await account_repo.delete_two_fa_key(account_id)

        # Verify call counts
        assert mock_db.select.call_count == 2
        assert mock_db.insert.call_count == 1
        assert mock_db.update.call_count == 3
