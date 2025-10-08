import pytest
from tests.utils.helpers import create_mock_db_row
from datetime import datetime


@pytest.mark.unit
class TestAccountRepoCreateAccount:
    async def test_create_account_success(
        self,
        account_repo,
        mock_db
    ):
        # Arrange
        login = "test_user"
        password = "hashed_password"
        expected_id = 1

        # Настраиваем мок БД
        from internal.repo.account.sql_query import create_account
        mock_db.set_insert_response(create_account, expected_id)

        # Act
        result = await account_repo.create_account(login, password)

        # Assert
        assert result == expected_id

        # Проверяем вызовы БД
        calls = mock_db.get_call_history()
        assert len(calls) == 2  # select + insert
        assert calls[1]["method"] == "insert"


@pytest.mark.unit
class TestAccountRepoAccountById:
    async def test_account_by_id_found(
        self,
        account_repo,
        mock_db
    ):
        # Arrange
        account_id = 1
        mock_row = create_mock_db_row(
            id=account_id,
            login="test_user",
            password="hash",
            google_two_fa_key="",
            created_at=datetime.now()
        )

        from internal.repo.account.sql_query import get_account_by_id
        mock_db.set_select_response(get_account_by_id, [mock_row])

        # Act
        result = await account_repo.account_by_id(account_id)

        # Assert
        assert len(result) == 1
        assert result[0].id == account_id
        assert result[0].login == "test_user"


    async def test_account_by_id_not_found(self, account_repo, mock_db):
        # TODO: Реализовать тест
        pass
