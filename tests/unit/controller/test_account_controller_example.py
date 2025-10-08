import pytest
from unittest.mock import AsyncMock
from internal import model
from internal.controller.http.handler.account.model import RegisterBody


@pytest.mark.unit
class TestAccountControllerRegister:
    async def test_register_success(
        self,
        account_controller,
        mock_account_service
    ):
        # Arrange
        body = RegisterBody(login="test_user", password="test_password")

        # Мокируем ответ сервиса
        mock_response = model.AuthorizationDataDTO(
            account_id=1,
            access_token="access_token_123",
            refresh_token="refresh_token_456"
        )
        mock_account_service.register = AsyncMock(return_value=mock_response)

        # Act
        response = await account_controller.register(body)

        # Assert
        assert response.status_code == 201
        assert response.body  # Проверяем наличие body

        # Проверяем, что сервис был вызван с правильными параметрами
        mock_account_service.register.assert_called_once_with(
            login=body.login,
            password=body.password
        )


    async def test_register_sets_cookies(self, account_controller, mock_account_service):
        # TODO: Реализовать тест
        pass
