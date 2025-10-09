import pytest
import io
from unittest.mock import AsyncMock, patch, MagicMock

from tests import utils
from internal import common


@pytest.mark.unit
@pytest.mark.auth
@pytest.mark.password
class TestAccountServiceRegister:

    async def test_register_success(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        jwt_tokens
    ):
        account_id = 10042
        login = "new_user"
        password = "secure_password"

        utils.setup_account_repo_create(mock_account_repo, account_id=account_id)
        utils.setup_loom_auth_client_authorization(mock_loom_authorization_client, tokens=jwt_tokens)

        with patch('bcrypt.hashpw', return_value=b"hashed_password"):
            with patch('bcrypt.gensalt', return_value=b"salt"):
                result = await account_service.register(login, password)

        utils.assert_authorization_dto(
            result,
            account_id=account_id,
            access_token=jwt_tokens.access_token,
            refresh_token=jwt_tokens.refresh_token
        )
        mock_account_repo.create_account.assert_called_once()
        mock_loom_authorization_client.authorization.assert_called_once_with(account_id, False, "employee")

    async def test_register_hashes_password_before_saving(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client
    ):
        login = "user"
        plain_password = "my_password"

        utils.setup_account_repo_create(mock_account_repo, account_id=10001)
        utils.setup_loom_auth_client_authorization(mock_loom_authorization_client)

        with patch('bcrypt.hashpw', return_value=b"mock_hashed") as mock_hash:
            with patch('bcrypt.gensalt'):
                await account_service.register(login, plain_password)

                mock_hash.assert_called_once()

    @pytest.mark.parametrize("account_id,role", [
        (10001, "employee"),
        (10002, "employee"),
        (10123, "employee"),
    ])
    async def test_register_calls_authorization_with_correct_params(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        jwt_tokens,
        account_id,
        role
    ):
        utils.setup_account_repo_create(mock_account_repo, account_id=account_id)
        utils.setup_loom_auth_client_authorization(mock_loom_authorization_client, tokens=jwt_tokens)

        with patch('bcrypt.hashpw', return_value=b"hashed"):
            with patch('bcrypt.gensalt'):
                await account_service.register("user", "password")

        mock_loom_authorization_client.authorization.assert_called_once_with(account_id, False, role)


@pytest.mark.unit
@pytest.mark.auth
class TestAccountServiceRegisterFromTg:

    async def test_register_from_tg_success(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        jwt_tokens
    ):
        login = "tg_user"
        password = "tg_password"
        account_id = 10010

        utils.setup_account_repo_create(mock_account_repo, account_id=account_id)
        mock_loom_authorization_client.authorization_tg = AsyncMock(return_value=jwt_tokens)

        with patch('bcrypt.hashpw', return_value=b"hashed"):
            with patch('bcrypt.gensalt'):
                result = await account_service.register_from_tg(login, password)

        utils.assert_authorization_dto(result, account_id=account_id)
        mock_account_repo.create_account.assert_called_once()
        mock_loom_authorization_client.authorization_tg.assert_called_once_with(account_id, False, "employee")

    async def test_register_from_tg_uses_authorization_tg_not_authorization(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        jwt_tokens
    ):
        utils.setup_account_repo_create(mock_account_repo, account_id=10055)
        mock_loom_authorization_client.authorization_tg = AsyncMock(return_value=jwt_tokens)

        with patch('bcrypt.hashpw', return_value=b"hashed"):
            with patch('bcrypt.gensalt'):
                await account_service.register_from_tg("user", "pass")

        mock_loom_authorization_client.authorization_tg.assert_called_once()
        mock_loom_authorization_client.authorization.assert_not_called()


@pytest.mark.unit
@pytest.mark.auth
@pytest.mark.password
class TestAccountServiceLogin:

    async def test_login_success(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        account_factory,
        jwt_tokens
    ):
        test_account = account_factory(login="test_user", password="hashed_password", google_two_fa_key="")

        utils.setup_account_repo_find_by_login(mock_account_repo, account=test_account)
        utils.setup_loom_auth_client_authorization(mock_loom_authorization_client, tokens=jwt_tokens)

        with patch('bcrypt.checkpw', return_value=True):
            result = await account_service.login(test_account.login, "correct_password")

        utils.assert_authorization_dto(result, account_id=test_account.id)

    async def test_login_account_not_found_raises_error(
        self,
        account_service,
        mock_account_repo
    ):
        utils.setup_account_repo_find_by_login(mock_account_repo, not_found=True)

        with pytest.raises(common.ErrAccountNotFound):
            await account_service.login("nonexistent", "password")

    async def test_login_invalid_password_raises_error(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        test_account = account_factory(password="hashed_password")
        utils.setup_account_repo_find_by_login(mock_account_repo, account=test_account)

        with patch('bcrypt.checkpw', return_value=False):
            with pytest.raises(common.ErrInvalidPassword):
                await account_service.login(test_account.login, "wrong_password")

    @pytest.mark.parametrize("two_fa_key,expected_status", [
        ("SOME2FAKEY", True),
        ("", False),
        ("ANOTHER_KEY_123", True),
    ])
    async def test_login_sets_correct_two_fa_status(
        self,
        account_service,
        mock_account_repo,
        mock_loom_authorization_client,
        account_factory,
        jwt_tokens,
        two_fa_key,
        expected_status
    ):
        test_account = account_factory(password="hashed", google_two_fa_key=two_fa_key)

        utils.setup_account_repo_find_by_login(mock_account_repo, account=test_account)
        utils.setup_loom_auth_client_authorization(mock_loom_authorization_client, tokens=jwt_tokens)

        with patch('bcrypt.checkpw', return_value=True):
            await account_service.login(test_account.login, "password")

        mock_loom_authorization_client.authorization.assert_called_once_with(
            test_account.id,
            expected_status,
            "employee"
        )


@pytest.mark.unit
class TestAccountServiceGenerateTwoFaKey:

    async def test_generate_two_fa_key_returns_key_and_qr_image(self, account_service):
        result = await account_service.generate_two_fa_key(10001)

        assert isinstance(result, tuple)
        assert len(result) == 2

        two_fa_key, qr_image = result
        assert isinstance(two_fa_key, str)
        assert len(two_fa_key) > 0
        assert isinstance(qr_image, io.BytesIO)

    async def test_generate_two_fa_key_returns_valid_base32_key(self, account_service):
        two_fa_key, _ = await account_service.generate_two_fa_key(10001)

        import re
        assert re.match(r'^[A-Z2-7]+$', two_fa_key)

    async def test_generate_two_fa_key_generates_unique_keys(self, account_service):
        key1, _ = await account_service.generate_two_fa_key(10001)
        key2, _ = await account_service.generate_two_fa_key(10001)

        assert key1 != key2

    async def test_generate_two_fa_key_qr_code_contains_data(self, account_service):
        _, qr_image = await account_service.generate_two_fa_key(10001)

        qr_image.seek(0)
        image_data = qr_image.read()
        assert len(image_data) > 100


@pytest.mark.unit
class TestAccountServiceSetTwoFaKey:

    async def test_set_two_fa_key_success(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        account_id = 10001
        two_fa_key = "JBSWY3DPEHPK3PXP"

        import pyotp
        totp = pyotp.TOTP(two_fa_key)
        valid_code = totp.now()

        test_account = account_factory(id=account_id, google_two_fa_key="")
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])
        utils.setup_account_repo_set_two_fa_key(mock_account_repo)

        await account_service.set_two_fa_key(account_id, two_fa_key, valid_code)

        mock_account_repo.account_by_id.assert_called_once_with(account_id)
        mock_account_repo.set_two_fa_key.assert_called_once_with(account_id, two_fa_key)

    async def test_set_two_fa_key_already_enabled_raises_error(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        account_id = 10001
        test_account = account_factory(id=account_id, google_two_fa_key="EXISTING_KEY")
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        with pytest.raises(common.ErrTwoFaAlreadyEnabled):
            await account_service.set_two_fa_key(account_id, "NEW_KEY", "123456")

        mock_account_repo.set_two_fa_key.assert_not_called()

    async def test_set_two_fa_key_invalid_code_raises_error(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        account_id = 10001
        two_fa_key = "JBSWY3DPEHPK3PXP"
        invalid_code = "000000"

        test_account = account_factory(id=account_id, google_two_fa_key="")
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        with pytest.raises(common.ErrTwoFaCodeInvalid):
            await account_service.set_two_fa_key(account_id, two_fa_key, invalid_code)

        mock_account_repo.set_two_fa_key.assert_not_called()


@pytest.mark.unit
class TestAccountServiceDeleteTwoFaKey:

    async def test_delete_two_fa_key_success(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        account_id = 10001
        two_fa_key = "JBSWY3DPEHPK3PXP"

        import pyotp
        totp = pyotp.TOTP(two_fa_key)
        valid_code = totp.now()

        test_account = account_factory(id=account_id, google_two_fa_key=two_fa_key)
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])
        utils.setup_account_repo_delete_two_fa_key(mock_account_repo)

        await account_service.delete_two_fa_key(account_id, valid_code)

        mock_account_repo.account_by_id.assert_called_once_with(account_id)
        mock_account_repo.delete_two_fa_key.assert_called_once_with(account_id)

    async def test_delete_two_fa_key_not_enabled_raises_error(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        account_id = 10001
        test_account = account_factory(id=account_id, google_two_fa_key="")
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        with pytest.raises(common.ErrTwoFaNotEnabled):
            await account_service.delete_two_fa_key(account_id, "123456")

        mock_account_repo.delete_two_fa_key.assert_not_called()

    async def test_delete_two_fa_key_invalid_code_raises_error(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        account_id = 10001
        two_fa_key = "JBSWY3DPEHPK3PXP"
        invalid_code = "000000"

        test_account = account_factory(id=account_id, google_two_fa_key=two_fa_key)
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        with pytest.raises(common.ErrTwoFaCodeInvalid):
            await account_service.delete_two_fa_key(account_id, invalid_code)

        mock_account_repo.delete_two_fa_key.assert_not_called()


@pytest.mark.unit
class TestAccountServiceVerifyTwo:

    async def test_verify_two_valid_code_returns_true(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        account_id = 10001
        two_fa_key = "JBSWY3DPEHPK3PXP"

        import pyotp
        totp = pyotp.TOTP(two_fa_key)
        valid_code = totp.now()

        test_account = account_factory(id=account_id, google_two_fa_key=two_fa_key)
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        result = await account_service.verify_two(account_id, valid_code)

        assert result is True

    async def test_verify_two_invalid_code_returns_false(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        account_id = 10001
        two_fa_key = "JBSWY3DPEHPK3PXP"
        invalid_code = "000000"

        test_account = account_factory(id=account_id, google_two_fa_key=two_fa_key)
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        result = await account_service.verify_two(account_id, invalid_code)

        assert result is False

    async def test_verify_two_not_enabled_raises_error(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        account_id = 10001
        test_account = account_factory(id=account_id, google_two_fa_key="")
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        with pytest.raises(common.ErrTwoFaNotEnabled):
            await account_service.verify_two(account_id, "123456")


@pytest.mark.unit
@pytest.mark.password
class TestAccountServiceRecoveryPassword:

    async def test_recovery_password_success(
        self,
        account_service,
        mock_account_repo
    ):
        account_id = 10001
        new_password = "new_secure_password"
        utils.setup_account_repo_update_password(mock_account_repo)

        with patch('bcrypt.hashpw', return_value=b"hashed_new") as mock_hash:
            with patch('bcrypt.gensalt'):
                await account_service.recovery_password(account_id, new_password)

                mock_hash.assert_called_once()
                mock_account_repo.update_password.assert_called_once()

    async def test_recovery_password_hashes_new_password(
        self,
        account_service,
        mock_account_repo
    ):
        account_id = 10001
        plain_password = "my_new_password"
        utils.setup_account_repo_update_password(mock_account_repo)

        with patch('bcrypt.hashpw', return_value=b"mock_hashed") as mock_hash:
            with patch('bcrypt.gensalt'):
                await account_service.recovery_password(account_id, plain_password)

                mock_hash.assert_called_once()


@pytest.mark.unit
@pytest.mark.password
class TestAccountServiceChangePassword:

    async def test_change_password_success(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        account_id = 10001
        old_password = "old_password"
        new_password = "new_password"

        test_account = account_factory(id=account_id, password="hashed_old")
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])
        utils.setup_account_repo_update_password(mock_account_repo)

        with patch('bcrypt.checkpw', return_value=True):
            with patch('bcrypt.hashpw', return_value=b"hashed_new"):
                with patch('bcrypt.gensalt'):
                    await account_service.change_password(account_id, new_password, old_password)

        mock_account_repo.account_by_id.assert_called_once_with(account_id)
        mock_account_repo.update_password.assert_called_once()

    async def test_change_password_invalid_old_password_raises_error(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        account_id = 10001
        test_account = account_factory(id=account_id, password="hashed_old")
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])

        with patch('bcrypt.checkpw', return_value=False):
            with pytest.raises(common.ErrInvalidPassword):
                await account_service.change_password(account_id, "new_password", "wrong_old_password")

        mock_account_repo.update_password.assert_not_called()

    async def test_change_password_verifies_old_before_updating(
        self,
        account_service,
        mock_account_repo,
        account_factory
    ):
        account_id = 10001
        test_account = account_factory(id=account_id, password="hashed_old")
        mock_account_repo.account_by_id = AsyncMock(return_value=[test_account])
        utils.setup_account_repo_update_password(mock_account_repo)

        with patch('bcrypt.checkpw', return_value=True) as mock_verify:
            with patch('bcrypt.hashpw', return_value=b"hashed_new"):
                with patch('bcrypt.gensalt'):
                    await account_service.change_password(account_id, "new_password", "old_password")

            mock_verify.assert_called_once()
            mock_account_repo.update_password.assert_called_once()
