import pytest
import io
from unittest.mock import AsyncMock
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
    """Тесты для метода register сервиса AccountService"""

    async def test_register_success(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        jwt_tokens,
        password_secret
    ):
        """Успешная регистрация нового пользователя"""
        # Arrange
        login = "new_user"
        password = "secure_password"
        expected_account_id = 42

        setup_account_repo_create(mock_account_repo, account_id=expected_account_id)
        setup_loom_auth_client_authorization(mock_client=mock_loom_authorization_client, tokens=jwt_tokens)

        # Act
        result = await account_service.register(login, password)

        # Assert
        assert_authorization_dto(result, account_id=expected_account_id)
        assert result.access_token == jwt_tokens.access_token
        assert result.refresh_token == jwt_tokens.refresh_token

        mock_account_repo.create_account.assert_called_once()

        call_args = mock_account_repo.create_account.call_args
        hashed_password = call_args[0][1]
        assert hashed_password != password, "Password should be hashed"

        mock_loom_authorization_client.authorization.assert_called_once_with(
            expected_account_id,
            False,
            "employee"
        )

    async def test_register_password_is_hashed(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        password_secret
    ):
        """Пароль хешируется перед сохранением"""
        # Arrange
        login = "user"
        plain_password = "my_password"

        setup_account_repo_create(mock_account_repo, account_id=1)
        setup_loom_auth_client_authorization(mock_loom_authorization_client)

        # Act
        await account_service.register(login, plain_password)

        # Assert
        call_args = mock_account_repo.create_account.call_args
        saved_password = call_args[0][1]

        assert saved_password != plain_password, "Password must be hashed"
        assert len(saved_password) > len(plain_password), "Hashed password should be longer"

    async def test_register_calls_authorization_with_correct_params(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        jwt_tokens
    ):
        """Вызывает authorization клиента с правильными параметрами"""
        # Arrange
        account_id = 123
        setup_account_repo_create(mock_account_repo, account_id=account_id)
        setup_loom_auth_client_authorization(mock_loom_authorization_client, tokens=jwt_tokens)

        # Act
        await account_service.register("user", "password")

        # Assert
        mock_loom_authorization_client.authorization.assert_called_once_with(
            account_id,
            False,
            "employee"
        )

    async def test_register_returns_correct_authorization_dto(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client
    ):
        """Возвращает корректный AuthorizationDataDTO"""
        # Arrange
        expected_account_id = 999
        expected_access_token = "access_xyz"
        expected_refresh_token = "refresh_abc"

        setup_account_repo_create(mock_account_repo, account_id=expected_account_id)
        setup_loom_auth_client_authorization(
            mock_loom_authorization_client,
            access_token=expected_access_token,
            refresh_token=expected_refresh_token
        )

        # Act
        result = await account_service.register("user", "password")

        # Assert
        assert result.account_id == expected_account_id
        assert result.access_token == expected_access_token
        assert result.refresh_token == expected_refresh_token


@pytest.mark.unit
class TestAccountServiceRegisterFromTg:
    """Тесты для метода register_from_tg сервиса AccountService"""

    async def test_register_from_tg_success(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        jwt_tokens
    ):
        """Успешная регистрация через Telegram"""
        # Arrange
        login = "tg_user"
        password = "tg_password"
        expected_account_id = 10

        setup_account_repo_create(mock_account_repo, account_id=expected_account_id)
        mock_loom_authorization_client.authorization_tg = AsyncMock(return_value=jwt_tokens)

        # Act
        result = await account_service.register_from_tg(login, password)

        # Assert
        assert_authorization_dto(result, account_id=expected_account_id)
        assert result.access_token == jwt_tokens.access_token
        assert result.refresh_token == jwt_tokens.refresh_token

        mock_account_repo.create_account.assert_called_once()
        mock_loom_authorization_client.authorization_tg.assert_called_once_with(
            expected_account_id,
            False,
            "employee"
        )

    async def test_register_from_tg_hashes_password(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        jwt_tokens
    ):
        """Хеширует пароль при регистрации через TG"""
        # Arrange
        plain_password = "plain_tg_password"

        setup_account_repo_create(mock_account_repo, account_id=1)
        mock_loom_authorization_client.authorization_tg = AsyncMock(return_value=jwt_tokens)

        # Act
        await account_service.register_from_tg("user", plain_password)

        # Assert
        call_args = mock_account_repo.create_account.call_args
        saved_password = call_args[0][1]
        assert saved_password != plain_password, "Password must be hashed"

    async def test_register_from_tg_calls_authorization_tg_method(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        jwt_tokens
    ):
        """Вызывает authorization_tg вместо authorization"""
        # Arrange
        account_id = 55
        setup_account_repo_create(mock_account_repo, account_id=account_id)
        mock_loom_authorization_client.authorization_tg = AsyncMock(return_value=jwt_tokens)

        # Act
        await account_service.register_from_tg("user", "pass")

        # Assert
        mock_loom_authorization_client.authorization_tg.assert_called_once()
        mock_loom_authorization_client.authorization.assert_not_called()


@pytest.mark.unit
class TestAccountServiceLogin:
    """Тесты для метода login сервиса AccountService"""

    async def test_login_success(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        account_factory,
        jwt_tokens,
        password_secret
    ):
        """Успешный логин с правильным паролем"""
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

    async def test_login_account_not_found_raises_error(
        self,
        account_service,
        mock_account_repo
    ):
        """Логин с несуществующим аккаунтом выбрасывает ошибку"""
        # Arrange
        setup_account_repo_find_by_login(mock_account_repo, not_found=True)

        # Act & Assert
        with pytest.raises(common.ErrAccountNotFound):
            await account_service.login("nonexistent", "password")

    async def test_login_invalid_password_raises_error(
        self,
        account_service,
        mock_account_repo,
        account_factory,
        password_secret
    ):
        """Логин с неверным паролем выбрасывает ошибку"""
        # Arrange
        correct_password = "correct"
        wrong_password = "wrong"

        hashed = hash_password(correct_password, password_secret)
        test_account = account_factory(password=hashed)

        setup_account_repo_find_by_login(mock_account_repo, account=test_account)

        # Act & Assert
        with pytest.raises(common.ErrInvalidPassword):
            await account_service.login(test_account.login, wrong_password)

    async def test_login_with_2fa_sets_two_fa_status_true(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        account_factory,
        jwt_tokens,
        password_secret
    ):
        """Логин с включенной 2FA передает two_fa_status=True"""
        # Arrange
        plain_password = "password"
        hashed = hash_password(plain_password, password_secret)

        test_account = account_factory(
            password=hashed,
            google_two_fa_key="SOME2FAKEY"
        )

        setup_account_repo_find_by_login(mock_account_repo, account=test_account)
        setup_loom_auth_client_authorization(mock_loom_authorization_client, tokens=jwt_tokens)

        # Act
        await account_service.login(test_account.login, plain_password)

        # Assert
        mock_loom_authorization_client.authorization.assert_called_once_with(
            test_account.id,
            True,
            "employee"
        )

    async def test_login_without_2fa_sets_two_fa_status_false(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        account_factory,
        jwt_tokens,
        password_secret
    ):
        """Логин без 2FA передает two_fa_status=False"""
        # Arrange
        plain_password = "password"
        hashed = hash_password(plain_password, password_secret)

        test_account = account_factory(
            password=hashed,
            google_two_fa_key=""
        )

        setup_account_repo_find_by_login(mock_account_repo, account=test_account)
        setup_loom_auth_client_authorization(mock_loom_authorization_client, tokens=jwt_tokens)

        # Act
        await account_service.login(test_account.login, plain_password)

        # Assert
        mock_loom_authorization_client.authorization.assert_called_once_with(
            test_account.id,
            False,
            "employee"
        )


@pytest.mark.unit
class TestAccountServiceGenerateTwoFaKey:
    """Тесты для метода generate_two_fa_key сервиса AccountService"""

    async def test_generate_two_fa_key_returns_tuple(
        self,
        account_service
    ):
        """Генерирует 2FA ключ и QR-код"""
        # Arrange
        account_id = 1

        # Act
        result = await account_service.generate_two_fa_key(account_id)

        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 2

        two_fa_key, qr_image = result
        assert isinstance(two_fa_key, str)
        assert len(two_fa_key) > 0
        assert isinstance(qr_image, io.BytesIO)

    async def test_generate_two_fa_key_returns_valid_base32_key(
        self,
        account_service
    ):
        """Генерирует валидный Base32 ключ"""
        # Arrange
        account_id = 1

        # Act
        two_fa_key, _ = await account_service.generate_two_fa_key(account_id)

        # Assert
        import re
        # Base32 alphabet: A-Z and 2-7
        assert re.match(r'^[A-Z2-7]+$', two_fa_key)

    async def test_generate_two_fa_key_returns_qr_code_image(
        self,
        account_service
    ):
        """Генерирует QR-код в виде изображения"""
        # Arrange
        account_id = 1

        # Act
        _, qr_image = await account_service.generate_two_fa_key(account_id)

        # Assert
        qr_image.seek(0)
        image_data = qr_image.read()
        assert len(image_data) > 0
        # Проверяем, что это PNG (начинается с PNG magic bytes)
        assert image_data[:8] == b'\x89PNG\r\n\x1a\n'

    async def test_generate_two_fa_key_generates_unique_keys(
        self,
        account_service
    ):
        """Генерирует уникальные ключи при каждом вызове"""
        # Arrange
        account_id = 1

        # Act
        key1, _ = await account_service.generate_two_fa_key(account_id)
        key2, _ = await account_service.generate_two_fa_key(account_id)

        # Assert
        assert key1 != key2


@pytest.mark.unit
class TestAccountServiceSetTwoFaKey:
    """Тесты для метода set_two_fa_key сервиса AccountService"""

    async def test_set_two_fa_key_success(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        """Успешная установка 2FA ключа"""
        # Arrange
        account_id = 1
        two_fa_key = "JBSWY3DPEHPK3PXP"

        # Генерируем валидный код для данного ключа
        import pyotp
        totp = pyotp.TOTP(two_fa_key)
        valid_code = totp.now()

        test_account = account_factory(id=account_id, google_two_fa_key="")
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])
        mock_account_repo.set_two_fa_key = AsyncMock()

        # Act
        await account_service.set_two_fa_key(account_id, two_fa_key, valid_code)

        # Assert
        mock_account_repo.account_by_id.assert_called_once_with(account_id)
        mock_account_repo.set_two_fa_key.assert_called_once_with(account_id, two_fa_key)

    async def test_set_two_fa_key_already_enabled_raises_error(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        """Установка 2FA когда уже включена выбрасывает ошибку"""
        # Arrange
        account_id = 1
        test_account = account_factory(id=account_id, google_two_fa_key="EXISTING_KEY")
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        # Act & Assert
        with pytest.raises(common.ErrTwoFaAlreadyEnabled):
            await account_service.set_two_fa_key(account_id, "NEW_KEY", "123456")

        mock_account_repo.set_two_fa_key.assert_not_called()

    async def test_set_two_fa_key_invalid_code_raises_error(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        """Установка 2FA с неверным кодом выбрасывает ошибку"""
        # Arrange
        account_id = 1
        two_fa_key = "JBSWY3DPEHPK3PXP"
        invalid_code = "000000"

        test_account = account_factory(id=account_id, google_two_fa_key="")
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        # Act & Assert
        with pytest.raises(common.ErrTwoFaCodeInvalid):
            await account_service.set_two_fa_key(account_id, two_fa_key, invalid_code)

        mock_account_repo.set_two_fa_key.assert_not_called()

    async def test_set_two_fa_key_verifies_code_before_setting(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        """Проверяет код перед установкой ключа"""
        # Arrange
        account_id = 1
        two_fa_key = "JBSWY3DPEHPK3PXP"

        import pyotp
        totp = pyotp.TOTP(two_fa_key)
        valid_code = totp.now()

        test_account = account_factory(id=account_id, google_two_fa_key="")
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])
        mock_account_repo.set_two_fa_key = AsyncMock()

        # Act
        await account_service.set_two_fa_key(account_id, two_fa_key, valid_code)

        # Assert
        # Если код был невалидным, вызов set_two_fa_key не произошел бы
        mock_account_repo.set_two_fa_key.assert_called_once()


@pytest.mark.unit
class TestAccountServiceDeleteTwoFaKey:
    """Тесты для метода delete_two_fa_key сервиса AccountService"""

    async def test_delete_two_fa_key_success(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        """Успешное удаление 2FA ключа"""
        # Arrange
        account_id = 1
        two_fa_key = "JBSWY3DPEHPK3PXP"

        import pyotp
        totp = pyotp.TOTP(two_fa_key)
        valid_code = totp.now()

        test_account = account_factory(id=account_id, google_two_fa_key=two_fa_key)
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])
        mock_account_repo.delete_two_fa_key = AsyncMock()

        # Act
        await account_service.delete_two_fa_key(account_id, valid_code)

        # Assert
        mock_account_repo.account_by_id.assert_called_once_with(account_id)
        mock_account_repo.delete_two_fa_key.assert_called_once_with(account_id)

    async def test_delete_two_fa_key_not_enabled_raises_error(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        """Удаление 2FA когда она не включена выбрасывает ошибку"""
        # Arrange
        account_id = 1
        test_account = account_factory(id=account_id, google_two_fa_key="")
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        # Act & Assert
        with pytest.raises(common.ErrTwoFaNotEnabled):
            await account_service.delete_two_fa_key(account_id, "123456")

        mock_account_repo.delete_two_fa_key.assert_not_called()

    async def test_delete_two_fa_key_invalid_code_raises_error(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        """Удаление 2FA с неверным кодом выбрасывает ошибку"""
        # Arrange
        account_id = 1
        two_fa_key = "JBSWY3DPEHPK3PXP"
        invalid_code = "000000"

        test_account = account_factory(id=account_id, google_two_fa_key=two_fa_key)
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        # Act & Assert
        with pytest.raises(common.ErrTwoFaCodeInvalid):
            await account_service.delete_two_fa_key(account_id, invalid_code)

        mock_account_repo.delete_two_fa_key.assert_not_called()

    async def test_delete_two_fa_key_verifies_code_before_deleting(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        """Проверяет код перед удалением ключа"""
        # Arrange
        account_id = 1
        two_fa_key = "JBSWY3DPEHPK3PXP"

        import pyotp
        totp = pyotp.TOTP(two_fa_key)
        valid_code = totp.now()

        test_account = account_factory(id=account_id, google_two_fa_key=two_fa_key)
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])
        mock_account_repo.delete_two_fa_key = AsyncMock()

        # Act
        await account_service.delete_two_fa_key(account_id, valid_code)

        # Assert
        # Если код был невалидным, вызов delete_two_fa_key не произошел бы
        mock_account_repo.delete_two_fa_key.assert_called_once()


@pytest.mark.unit
class TestAccountServiceVerifyTwo:
    """Тесты для метода verify_two сервиса AccountService"""

    async def test_verify_two_success_valid_code(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        """Верификация с валидным кодом возвращает True"""
        # Arrange
        account_id = 1
        two_fa_key = "JBSWY3DPEHPK3PXP"

        import pyotp
        totp = pyotp.TOTP(two_fa_key)
        valid_code = totp.now()

        test_account = account_factory(id=account_id, google_two_fa_key=two_fa_key)
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        # Act
        result = await account_service.verify_two(account_id, valid_code)

        # Assert
        assert result is True
        mock_account_repo.account_by_id.assert_called_once_with(account_id)

    async def test_verify_two_success_invalid_code(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        """Верификация с невалидным кодом возвращает False"""
        # Arrange
        account_id = 1
        two_fa_key = "JBSWY3DPEHPK3PXP"
        invalid_code = "000000"

        test_account = account_factory(id=account_id, google_two_fa_key=two_fa_key)
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        # Act
        result = await account_service.verify_two(account_id, invalid_code)

        # Assert
        assert result is False

    async def test_verify_two_not_enabled_raises_error(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        """Верификация когда 2FA не включена выбрасывает ошибку"""
        # Arrange
        account_id = 1
        test_account = account_factory(id=account_id, google_two_fa_key="")
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        # Act & Assert
        with pytest.raises(common.ErrTwoFaNotEnabled):
            await account_service.verify_two(account_id, "123456")

    async def test_verify_two_gets_account_from_repo(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        """Получает аккаунт из репозитория при верификации"""
        # Arrange
        account_id = 42
        two_fa_key = "JBSWY3DPEHPK3PXP"

        import pyotp
        totp = pyotp.TOTP(two_fa_key)
        valid_code = totp.now()

        test_account = account_factory(id=account_id, google_two_fa_key=two_fa_key)
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        # Act
        await account_service.verify_two(account_id, valid_code)

        # Assert
        mock_account_repo.account_by_id.assert_called_once_with(account_id)


@pytest.mark.unit
class TestAccountServiceRecoveryPassword:
    """Тесты для метода recovery_password сервиса AccountService"""

    async def test_recovery_password_success(
        self,
        account_service,
        mock_account_repo
    ):
        """Успешное восстановление пароля"""
        # Arrange
        account_id = 1
        new_password = "new_secure_password"
        mock_account_repo.update_password = AsyncMock()

        # Act
        await account_service.recovery_password(account_id, new_password)

        # Assert
        mock_account_repo.update_password.assert_called_once()
        call_args = mock_account_repo.update_password.call_args

        assert call_args[0][0] == account_id
        saved_password = call_args[0][1]
        assert saved_password != new_password, "Password should be hashed"

    async def test_recovery_password_hashes_new_password(
        self,
        account_service,
        mock_account_repo
    ):
        """Новый пароль хешируется перед сохранением"""
        # Arrange
        account_id = 1
        plain_password = "my_new_password"
        mock_account_repo.update_password = AsyncMock()

        # Act
        await account_service.recovery_password(account_id, plain_password)

        # Assert
        call_args = mock_account_repo.update_password.call_args
        saved_password = call_args[0][1]

        assert saved_password != plain_password
        assert len(saved_password) > len(plain_password)

    async def test_recovery_password_calls_update_password(
        self,
        account_service,
        mock_account_repo
    ):
        """Вызывает update_password репозитория"""
        # Arrange
        account_id = 99
        new_password = "password"
        mock_account_repo.update_password = AsyncMock()

        # Act
        await account_service.recovery_password(account_id, new_password)

        # Assert
        mock_account_repo.update_password.assert_called_once()


@pytest.mark.unit
class TestAccountServiceChangePassword:
    """Тесты для метода change_password сервиса AccountService"""

    async def test_change_password_success(
        self,
        account_service,
        mock_account_repo,
        account_factory,
        password_secret
    ):
        """Успешная смена пароля"""
        # Arrange
        account_id = 1
        old_password = "old_password"
        new_password = "new_password"

        hashed_old = hash_password(old_password, password_secret)
        test_account = account_factory(id=account_id, password=hashed_old)

        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])
        mock_account_repo.update_password = AsyncMock()

        # Act
        await account_service.change_password(account_id, new_password, old_password)

        # Assert
        mock_account_repo.account_by_id.assert_called_once_with(account_id)
        mock_account_repo.update_password.assert_called_once()

    async def test_change_password_invalid_old_password_raises_error(
        self,
        account_service,
        mock_account_repo,
        account_factory,
        password_secret
    ):
        """Смена пароля с неверным старым паролем выбрасывает ошибку"""
        # Arrange
        account_id = 1
        correct_old_password = "correct_old"
        wrong_old_password = "wrong_old"
        new_password = "new_password"

        hashed_old = hash_password(correct_old_password, password_secret)
        test_account = account_factory(id=account_id, password=hashed_old)

        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        # Act & Assert
        with pytest.raises(common.ErrInvalidPassword):
            await account_service.change_password(account_id, new_password, wrong_old_password)

        mock_account_repo.update_password.assert_not_called()

    async def test_change_password_hashes_new_password(
        self,
        account_service,
        mock_account_repo,
        account_factory,
        password_secret
    ):
        """Новый пароль хешируется перед сохранением"""
        # Arrange
        account_id = 1
        old_password = "old_password"
        new_password = "new_password"

        hashed_old = hash_password(old_password, password_secret)
        test_account = account_factory(id=account_id, password=hashed_old)

        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])
        mock_account_repo.update_password = AsyncMock()

        # Act
        await account_service.change_password(account_id, new_password, old_password)

        # Assert
        call_args = mock_account_repo.update_password.call_args
        saved_password = call_args[0][1]

        assert saved_password != new_password
        assert saved_password != hashed_old

    async def test_change_password_verifies_old_password_first(
        self,
        account_service,
        mock_account_repo,
        account_factory,
        password_secret
    ):
        """Проверяет старый пароль перед изменением"""
        # Arrange
        account_id = 1
        old_password = "old_password"
        new_password = "new_password"

        hashed_old = hash_password(old_password, password_secret)
        test_account = account_factory(id=account_id, password=hashed_old)

        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])
        mock_account_repo.update_password = AsyncMock()

        # Act
        await account_service.change_password(account_id, new_password, old_password)

        # Assert
        # Если проверка не прошла бы, была бы выброшена ошибка
        mock_account_repo.update_password.assert_called_once()

    async def test_change_password_gets_account_from_repo(
        self,
        account_service,
        mock_account_repo,
        account_factory,
        password_secret
    ):
        """Получает аккаунт из репозитория для проверки старого пароля"""
        # Arrange
        account_id = 55
        old_password = "old_password"
        new_password = "new_password"

        hashed_old = hash_password(old_password, password_secret)
        test_account = account_factory(id=account_id, password=hashed_old)

        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])
        mock_account_repo.update_password = AsyncMock()

        # Act
        await account_service.change_password(account_id, new_password, old_password)

        # Assert
        mock_account_repo.account_by_id.assert_called_once_with(account_id)
