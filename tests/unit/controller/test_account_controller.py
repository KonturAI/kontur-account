import pytest
from unittest.mock import AsyncMock
from fastapi import Request
from io import BytesIO

from internal.controller.http.handler.account.model import (
    RegisterBody, LoginBody, SetTwoFaBody, DeleteTwoFaBody,
    VerifyTwoFaBody, RecoveryPasswordBody, ChangePasswordBody
)
from internal import  model


@pytest.mark.unit
class TestAccountControllerRegister:
    """Тесты для метода register контроллера AccountController"""

    async def test_register_success(
        self,
        account_controller,
        mock_account_service
    ):
        """Успешная регистрация пользователя"""
        # Arrange
        body = RegisterBody(login="test_user", password="test_password")

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
        assert response.body

        # Проверяем, что сервис был вызван с правильными параметрами
        mock_account_service.register.assert_called_once_with(
            login=body.login,
            password=body.password
        )

    async def test_register_returns_account_id_in_body(
        self,
        account_controller,
        mock_account_service
    ):
        """Регистрация возвращает account_id в теле ответа"""
        # Arrange
        expected_account_id = 42
        body = RegisterBody(login="user", password="pass")

        mock_response = model.AuthorizationDataDTO(
            account_id=expected_account_id,
            access_token="token",
            refresh_token="refresh"
        )
        mock_account_service.register = AsyncMock(return_value=mock_response)

        # Act
        response = await account_controller.register(body)

        # Assert
        import json
        response_data = json.loads(response.body)
        assert response_data["account_id"] == expected_account_id

    async def test_register_sets_access_token_cookie(
        self,
        account_controller,
        mock_account_service
    ):
        """Регистрация устанавливает cookie Access-Token"""
        # Arrange
        body = RegisterBody(login="user", password="pass")
        expected_token = "access_token_xyz"

        mock_response = model.AuthorizationDataDTO(
            account_id=1,
            access_token=expected_token,
            refresh_token="refresh"
        )
        mock_account_service.register = AsyncMock(return_value=mock_response)

        # Act
        response = await account_controller.register(body)

        # Assert
        cookies = response.headers.getlist("set-cookie")
        access_cookie = next((c for c in cookies if "Access-Token" in c), None)

        assert access_cookie is not None
        assert expected_token in access_cookie
        assert "httponly" in access_cookie.lower()
        assert "secure" in access_cookie.lower()
        assert "samesite=lax" in access_cookie.lower()

    async def test_register_sets_refresh_token_cookie(
        self,
        account_controller,
        mock_account_service
    ):
        """Регистрация устанавливает cookie Refresh-Token"""
        # Arrange
        body = RegisterBody(login="user", password="pass")
        expected_token = "refresh_token_xyz"

        mock_response = model.AuthorizationDataDTO(
            account_id=1,
            access_token="access",
            refresh_token=expected_token
        )
        mock_account_service.register = AsyncMock(return_value=mock_response)

        # Act
        response = await account_controller.register(body)

        # Assert
        cookies = response.headers.getlist("set-cookie")
        refresh_cookie = next((c for c in cookies if "Refresh-Token" in c), None)

        assert refresh_cookie is not None
        assert expected_token in refresh_cookie
        assert "httponly" in refresh_cookie.lower()
        assert "secure" in refresh_cookie.lower()
        assert "samesite=lax" in refresh_cookie.lower()

    async def test_register_with_special_characters_in_login(
        self,
        account_controller,
        mock_account_service
    ):
        """Регистрация с специальными символами в логине"""
        # Arrange
        body = RegisterBody(login="user@test.com", password="password123")

        mock_response = model.AuthorizationDataDTO(
            account_id=1,
            access_token="token",
            refresh_token="refresh"
        )
        mock_account_service.register = AsyncMock(return_value=mock_response)

        # Act
        response = await account_controller.register(body)

        # Assert
        assert response.status_code == 201
        mock_account_service.register.assert_called_once_with(
            login="user@test.com",
            password="password123"
        )


@pytest.mark.unit
class TestAccountControllerRegisterFromTg:
    """Тесты для метода register_from_tg контроллера AccountController"""

    async def test_register_from_tg_success(
        self,
        account_controller,
        mock_account_service
    ):
        """Успешная регистрация через Telegram"""
        # Arrange
        body = RegisterBody(login="tg_user", password="tg_password")

        mock_response = model.AuthorizationDataDTO(
            account_id=10,
            access_token="tg_access_token",
            refresh_token="tg_refresh_token"
        )
        mock_account_service.register_from_tg = AsyncMock(return_value=mock_response)

        # Act
        response = await account_controller.register_from_tg(body)

        # Assert
        assert response.status_code == 201
        mock_account_service.register_from_tg.assert_called_once_with(
            login=body.login,
            password=body.password
        )

    async def test_register_from_tg_returns_account_id(
        self,
        account_controller,
        mock_account_service
    ):
        """Регистрация через TG возвращает account_id"""
        # Arrange
        expected_account_id = 99
        body = RegisterBody(login="tg_user", password="pass")

        mock_response = model.AuthorizationDataDTO(
            account_id=expected_account_id,
            access_token="token",
            refresh_token="refresh"
        )
        mock_account_service.register_from_tg = AsyncMock(return_value=mock_response)

        # Act
        response = await account_controller.register_from_tg(body)

        # Assert
        import json
        response_data = json.loads(response.body)
        assert response_data["account_id"] == expected_account_id

    async def test_register_from_tg_sets_cookies(
        self,
        account_controller,
        mock_account_service
    ):
        """Регистрация через TG устанавливает оба cookie"""
        # Arrange
        body = RegisterBody(login="user", password="pass")

        mock_response = model.AuthorizationDataDTO(
            account_id=1,
            access_token="access_123",
            refresh_token="refresh_456"
        )
        mock_account_service.register_from_tg = AsyncMock(return_value=mock_response)

        # Act
        response = await account_controller.register_from_tg(body)

        # Assert
        cookies = response.headers.getlist("set-cookie")
        assert len(cookies) == 2
        assert any("Access-Token" in c for c in cookies)
        assert any("Refresh-Token" in c for c in cookies)


@pytest.mark.unit
class TestAccountControllerLogin:
    """Тесты для метода login контроллера AccountController"""

    async def test_login_success(
        self,
        account_controller,
        mock_account_service
    ):
        """Успешный логин пользователя"""
        # Arrange
        body = LoginBody(login="existing_user", password="correct_password")

        mock_response = model.AuthorizationDataDTO(
            account_id=5,
            access_token="login_access_token",
            refresh_token="login_refresh_token"
        )
        mock_account_service.login = AsyncMock(return_value=mock_response)

        # Act
        response = await account_controller.login(body)

        # Assert
        assert response.status_code == 200
        mock_account_service.login.assert_called_once_with(
            login=body.login,
            password=body.password
        )

    async def test_login_returns_account_id(
        self,
        account_controller,
        mock_account_service
    ):
        """Логин возвращает account_id в теле ответа"""
        # Arrange
        expected_account_id = 77
        body = LoginBody(login="user", password="pass")

        mock_response = model.AuthorizationDataDTO(
            account_id=expected_account_id,
            access_token="token",
            refresh_token="refresh"
        )
        mock_account_service.login = AsyncMock(return_value=mock_response)

        # Act
        response = await account_controller.login(body)

        # Assert
        import json
        response_data = json.loads(response.body)
        assert response_data["account_id"] == expected_account_id

    async def test_login_sets_access_token_cookie(
        self,
        account_controller,
        mock_account_service
    ):
        """Логин устанавливает cookie Access-Token"""
        # Arrange
        body = LoginBody(login="user", password="pass")
        expected_token = "new_access_token"

        mock_response = model.AuthorizationDataDTO(
            account_id=1,
            access_token=expected_token,
            refresh_token="refresh"
        )
        mock_account_service.login = AsyncMock(return_value=mock_response)

        # Act
        response = await account_controller.login(body)

        # Assert
        cookies = response.headers.getlist("set-cookie")
        access_cookie = next((c for c in cookies if "Access-Token" in c), None)

        assert access_cookie is not None
        assert expected_token in access_cookie

    async def test_login_sets_refresh_token_cookie(
        self,
        account_controller,
        mock_account_service
    ):
        """Логин устанавливает cookie Refresh-Token"""
        # Arrange
        body = LoginBody(login="user", password="pass")
        expected_token = "new_refresh_token"

        mock_response = model.AuthorizationDataDTO(
            account_id=1,
            access_token="access",
            refresh_token=expected_token
        )
        mock_account_service.login = AsyncMock(return_value=mock_response)

        # Act
        response = await account_controller.login(body)

        # Assert
        cookies = response.headers.getlist("set-cookie")
        refresh_cookie = next((c for c in cookies if "Refresh-Token" in c), None)

        assert refresh_cookie is not None
        assert expected_token in refresh_cookie

    async def test_login_sets_cookies_with_security_flags(
        self,
        account_controller,
        mock_account_service
    ):
        """Логин устанавливает cookies с security флагами"""
        # Arrange
        body = LoginBody(login="user", password="pass")

        mock_response = model.AuthorizationDataDTO(
            account_id=1,
            access_token="access",
            refresh_token="refresh"
        )
        mock_account_service.login = AsyncMock(return_value=mock_response)

        # Act
        response = await account_controller.login(body)

        # Assert
        cookies = response.headers.getlist("set-cookie")

        for cookie in cookies:
            assert "httponly" in cookie.lower()
            assert "secure" in cookie.lower()
            assert "samesite=lax" in cookie.lower()


@pytest.mark.unit
class TestAccountControllerGenerateTwoFa:
    """Тесты для метода generate_two_fa контроллера AccountController"""

    async def test_generate_two_fa_success(
        self,
        account_controller,
        mock_account_service,
        mocker
    ):
        """Успешная генерация 2FA"""
        # Arrange
        account_id = 1
        two_fa_key = "JBSWY3DPEHPK3PXP"
        qr_image = BytesIO(b"fake_qr_image_data")

        mock_request = mocker.MagicMock(spec=Request)
        mock_auth_data = mocker.MagicMock()
        mock_auth_data.account_id = account_id
        mock_request.state.authorization_data = mock_auth_data

        mock_account_service.generate_two_fa_key = AsyncMock(
            return_value=(two_fa_key, qr_image)
        )

        # Act
        response = await account_controller.generate_two_fa(mock_request)

        # Assert
        assert response.media_type == "image/png"
        assert response.headers["X-TwoFA-Key"] == two_fa_key
        assert "qr_code.png" in response.headers["Content-Disposition"]
        mock_account_service.generate_two_fa_key.assert_called_once_with(account_id)

    async def test_generate_two_fa_forbidden_for_unauthorized(
        self,
        account_controller,
        mock_account_service,
        mocker
    ):
        """Генерация 2FA возвращает 403 для неавторизованного пользователя"""
        # Arrange
        mock_request = mocker.MagicMock(spec=Request)
        mock_auth_data = mocker.MagicMock()
        mock_auth_data.account_id = 0
        mock_request.state.authorization_data = mock_auth_data

        # Act
        response = await account_controller.generate_two_fa(mock_request)

        # Assert
        assert response.status_code == 403
        mock_account_service.generate_two_fa_key.assert_not_called()


@pytest.mark.unit
class TestAccountControllerSetTwoFa:
    """Тесты для метода set_two_fa контроллера AccountController"""

    async def test_set_two_fa_success(
        self,
        account_controller,
        mock_account_service,
        mocker
    ):
        """Успешная установка 2FA"""
        # Arrange
        account_id = 1
        body = SetTwoFaBody(
            google_two_fa_key="JBSWY3DPEHPK3PXP",
            google_two_fa_code="123456"
        )

        mock_request = mocker.MagicMock(spec=Request)
        mock_auth_data = mocker.MagicMock()
        mock_auth_data.account_id = account_id
        mock_request.state.authorization_data = mock_auth_data

        mock_account_service.set_two_fa_key = AsyncMock()

        # Act
        response = await account_controller.set_two_fa(mock_request, body)

        # Assert
        assert response.status_code == 200
        mock_account_service.set_two_fa_key.assert_called_once_with(
            account_id=account_id,
            google_two_fa_key=body.google_two_fa_key,
            google_two_fa_code=body.google_two_fa_code
        )

    async def test_set_two_fa_forbidden_for_unauthorized(
        self,
        account_controller,
        mock_account_service,
        mocker
    ):
        """Установка 2FA возвращает 403 для неавторизованного"""
        # Arrange
        body = SetTwoFaBody(
            google_two_fa_key="KEY",
            google_two_fa_code="123456"
        )

        mock_request = mocker.MagicMock(spec=Request)
        mock_auth_data = mocker.MagicMock()
        mock_auth_data.account_id = 0
        mock_request.state.authorization_data = mock_auth_data

        # Act
        response = await account_controller.set_two_fa(mock_request, body)

        # Assert
        assert response.status_code == 403
        mock_account_service.set_two_fa_key.assert_not_called()


@pytest.mark.unit
class TestAccountControllerDeleteTwoFa:
    """Тесты для метода delete_two_fa контроллера AccountController"""

    async def test_delete_two_fa_success(
        self,
        account_controller,
        mock_account_service,
        mocker
    ):
        """Успешное удаление 2FA"""
        # Arrange
        account_id = 1
        body = DeleteTwoFaBody(google_two_fa_code="123456")

        mock_request = mocker.MagicMock(spec=Request)
        mock_auth_data = mocker.MagicMock()
        mock_auth_data.account_id = account_id
        mock_request.state.authorization_data = mock_auth_data

        mock_account_service.delete_two_fa_key = AsyncMock()

        # Act
        response = await account_controller.delete_two_fa(mock_request, body)

        # Assert
        assert response.status_code == 200
        mock_account_service.delete_two_fa_key.assert_called_once_with(
            account_id=account_id,
            google_two_fa_code=body.google_two_fa_code
        )

    async def test_delete_two_fa_forbidden_for_unauthorized(
        self,
        account_controller,
        mock_account_service,
        mocker
    ):
        """Удаление 2FA возвращает 403 для неавторизованного"""
        # Arrange
        body = DeleteTwoFaBody(google_two_fa_code="123456")

        mock_request = mocker.MagicMock(spec=Request)
        mock_auth_data = mocker.MagicMock()
        mock_auth_data.account_id = 0
        mock_request.state.authorization_data = mock_auth_data

        # Act
        response = await account_controller.delete_two_fa(mock_request, body)

        # Assert
        assert response.status_code == 403
        mock_account_service.delete_two_fa_key.assert_not_called()


@pytest.mark.unit
class TestAccountControllerVerifyTwoFa:
    """Тесты для метода verify_two_fa контроллера AccountController"""

    async def test_verify_two_fa_success_valid_code(
        self,
        account_controller,
        mock_account_service,
        mocker
    ):
        """Успешная верификация 2FA с валидным кодом"""
        # Arrange
        account_id = 1
        body = VerifyTwoFaBody(google_two_fa_code="123456")

        mock_request = mocker.MagicMock(spec=Request)
        mock_auth_data = mocker.MagicMock()
        mock_auth_data.account_id = account_id
        mock_request.state.authorization_data = mock_auth_data

        mock_account_service.verify_two = AsyncMock(return_value=True)

        # Act
        response = await account_controller.verify_two_fa(mock_request, body)

        # Assert
        assert response.status_code == 200
        import json
        response_data = json.loads(response.body)
        assert response_data["is_valid"] is True
        mock_account_service.verify_two.assert_called_once_with(
            account_id=account_id,
            google_two_fa_code=body.google_two_fa_code
        )

    async def test_verify_two_fa_success_invalid_code(
        self,
        account_controller,
        mock_account_service,
        mocker
    ):
        """Верификация 2FA с невалидным кодом"""
        # Arrange
        account_id = 1
        body = VerifyTwoFaBody(google_two_fa_code="000000")

        mock_request = mocker.MagicMock(spec=Request)
        mock_auth_data = mocker.MagicMock()
        mock_auth_data.account_id = account_id
        mock_request.state.authorization_data = mock_auth_data

        mock_account_service.verify_two = AsyncMock(return_value=False)

        # Act
        response = await account_controller.verify_two_fa(mock_request, body)

        # Assert
        assert response.status_code == 200
        import json
        response_data = json.loads(response.body)
        assert response_data["is_valid"] is False

    async def test_verify_two_fa_forbidden_for_unauthorized(
        self,
        account_controller,
        mock_account_service,
        mocker
    ):
        """Верификация 2FA возвращает 403 для неавторизованного"""
        # Arrange
        body = VerifyTwoFaBody(google_two_fa_code="123456")

        mock_request = mocker.MagicMock(spec=Request)
        mock_auth_data = mocker.MagicMock()
        mock_auth_data.account_id = 0
        mock_request.state.authorization_data = mock_auth_data

        # Act
        response = await account_controller.verify_two_fa(mock_request, body)

        # Assert
        assert response.status_code == 403
        mock_account_service.verify_two.assert_not_called()


@pytest.mark.unit
class TestAccountControllerRecoveryPassword:
    """Тесты для метода recovery_password контроллера AccountController"""

    async def test_recovery_password_success(
        self,
        account_controller,
        mock_account_service,
        mocker
    ):
        """Успешное восстановление пароля"""
        # Arrange
        account_id = 1
        body = RecoveryPasswordBody(new_password="new_secure_password")

        mock_request = mocker.MagicMock(spec=Request)
        mock_auth_data = mocker.MagicMock()
        mock_auth_data.account_id = account_id
        mock_request.state.authorization_data = mock_auth_data

        mock_account_service.recovery_password = AsyncMock()

        # Act
        response = await account_controller.recovery_password(mock_request, body)

        # Assert
        assert response.status_code == 200
        mock_account_service.recovery_password.assert_called_once_with(
            account_id=account_id,
            new_password=body.new_password
        )

    async def test_recovery_password_forbidden_for_unauthorized(
        self,
        account_controller,
        mock_account_service,
        mocker
    ):
        """Восстановление пароля возвращает 403 для неавторизованного"""
        # Arrange
        body = RecoveryPasswordBody(new_password="new_password")

        mock_request = mocker.MagicMock(spec=Request)
        mock_auth_data = mocker.MagicMock()
        mock_auth_data.account_id = 0
        mock_request.state.authorization_data = mock_auth_data

        # Act
        response = await account_controller.recovery_password(mock_request, body)

        # Assert
        assert response.status_code == 403
        mock_account_service.recovery_password.assert_not_called()


@pytest.mark.unit
class TestAccountControllerChangePassword:
    """Тесты для метода change_password контроллера AccountController"""

    async def test_change_password_success(
        self,
        account_controller,
        mock_account_service,
        mocker
    ):
        """Успешная смена пароля"""
        # Arrange
        account_id = 1
        body = ChangePasswordBody(
            old_password="old_password",
            new_password="new_password"
        )

        mock_request = mocker.MagicMock(spec=Request)
        mock_auth_data = mocker.MagicMock()
        mock_auth_data.account_id = account_id
        mock_request.state.authorization_data = mock_auth_data

        mock_account_service.change_password = AsyncMock()

        # Act
        response = await account_controller.change_password(mock_request, body)

        # Assert
        assert response.status_code == 200
        mock_account_service.change_password.assert_called_once_with(
            account_id=account_id,
            new_password=body.new_password,
            old_password=body.old_password
        )

    async def test_change_password_forbidden_for_unauthorized(
        self,
        account_controller,
        mock_account_service,
        mocker
    ):
        """Смена пароля возвращает 403 для неавторизованного"""
        # Arrange
        body = ChangePasswordBody(
            old_password="old",
            new_password="new"
        )

        mock_request = mocker.MagicMock(spec=Request)
        mock_auth_data = mocker.MagicMock()
        mock_auth_data.account_id = 0
        mock_request.state.authorization_data = mock_auth_data

        # Act
        response = await account_controller.change_password(mock_request, body)

        # Assert
        assert response.status_code == 403
        mock_account_service.change_password.assert_not_called()
