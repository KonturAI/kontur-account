import pytest
import pyotp

from internal import model


class TestAccountApiRegister:
    async def test_register_success(self, test_client, mock_loom_authorization_client):
        # Arrange
        login = "test_user"
        password = "test_password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_access_token",
            refresh_token="test_refresh_token"
        )

        # Act
        response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "account_id" in data
        assert data["account_id"] > 0

        # Verify cookies are set
        assert "Access-Token" in response.cookies
        assert response.cookies["Access-Token"] == "test_access_token"
        assert "Refresh-Token" in response.cookies
        assert response.cookies["Refresh-Token"] == "test_refresh_token"

        # Verify authorization client was called
        mock_loom_authorization_client.authorization.assert_called_once_with(
            data["account_id"],
            False,
            "employee"
        )

    async def test_register_duplicate_login(self, test_client, mock_loom_authorization_client):
        # Arrange
        login = "duplicate_user"
        password = "test_password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_access_token",
            refresh_token="test_refresh_token"
        )

        # Create first account
        await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )

        # Act - try to register with same login
        response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )

        # Assert
        assert response.status_code == 500

    @pytest.mark.parametrize("login,password", [
        pytest.param("", "password", id="empty_login"),
        pytest.param("user", "", id="empty_password"),
        pytest.param("a" * 100, "password", id="long_login"),
        pytest.param("user", "b" * 200, id="long_password"),
    ])
    async def test_register_edge_cases(
        self, test_client, mock_loom_authorization_client, login, password
    ):
        # Arrange
        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_access_token",
            refresh_token="test_refresh_token"
        )

        # Act
        response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )

        # Assert - should succeed for all cases
        assert response.status_code == 201
        data = response.json()
        assert data["account_id"] > 0

    async def test_register_invalid_json(self, test_client):
        # Act
        response = await test_client.post(
            "/api/account/register",
            json={"login": "user"}  # missing password
        )

        # Assert
        assert response.status_code == 422


class TestAccountApiLogin:
    async def test_login_success(self, test_client, mock_loom_authorization_client):
        # Arrange
        login = "login_user"
        password = "login_password"

        # First register the user
        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="register_access_token",
            refresh_token="register_refresh_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        account_id = register_response.json()["account_id"]

        # Mock login authorization
        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="login_access_token",
            refresh_token="login_refresh_token"
        )

        # Act
        response = await test_client.post(
            "/api/account/login",
            json={"login": login, "password": password}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["account_id"] == account_id

        # Verify cookies
        assert response.cookies["Access-Token"] == "login_access_token"
        assert response.cookies["Refresh-Token"] == "login_refresh_token"

        # Verify authorization was called with two_fa_status=False
        assert mock_loom_authorization_client.authorization.call_count == 2

    async def test_login_nonexistent_user(self, test_client):
        # Act
        response = await test_client.post(
            "/api/account/login",
            json={"login": "nonexistent", "password": "password"}
        )

        # Assert
        assert response.status_code == 500

    async def test_login_invalid_password(self, test_client, mock_loom_authorization_client):
        # Arrange
        login = "password_test_user"
        password = "correct_password"

        # Register user
        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )

        # Act - login with wrong password
        response = await test_client.post(
            "/api/account/login",
            json={"login": login, "password": "wrong_password"}
        )

        # Assert
        assert response.status_code == 500

    async def test_login_with_2fa_enabled(self, test_client, mock_loom_authorization_client):
        # Arrange
        login = "user_with_2fa"
        password = "password"

        # Register user
        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="register_token",
            refresh_token="register_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        # Enable 2FA
        two_fa_key = pyotp.random_base32()
        totp = pyotp.TOTP(two_fa_key)
        two_fa_code = totp.now()

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        await test_client.post(
            "/api/account/2fa/set",
            json={
                "google_two_fa_key": two_fa_key,
                "google_two_fa_code": two_fa_code
            },
            cookies={"Access-Token": access_token}
        )

        # Mock login with 2FA enabled
        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="login_token_with_2fa",
            refresh_token="refresh_token_with_2fa"
        )

        # Act
        response = await test_client.post(
            "/api/account/login",
            json={"login": login, "password": password}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["account_id"] == account_id

        # Verify authorization was called with two_fa_status=True
        last_call = mock_loom_authorization_client.authorization.call_args
        assert last_call[0][1] == True  # two_fa_status


class TestAccountApiTwoFactorAuth:
    async def test_generate_two_fa_success(self, test_client, mock_loom_authorization_client):
        # Arrange - create and login user
        login = "2fa_gen_user"
        password = "password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        # Act
        response = await test_client.get(
            "/api/account/2fa/generate",
            cookies={"Access-Token": access_token}
        )

        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert "X-TwoFA-Key" in response.headers
        assert len(response.headers["X-TwoFA-Key"]) == 32  # Base32 key length
        assert len(response.content) > 0  # QR code image

    async def test_generate_two_fa_unauthorized(self, test_client):
        # Act - without access token
        response = await test_client.get("/api/account/2fa/generate")

        # Assert
        assert response.status_code == 403

    async def test_set_two_fa_success(self, test_client, mock_loom_authorization_client):
        # Arrange - create user and generate 2FA key
        login = "2fa_set_user"
        password = "password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        gen_response = await test_client.get(
            "/api/account/2fa/generate",
            cookies={"Access-Token": access_token}
        )
        two_fa_key = gen_response.headers["X-TwoFA-Key"]

        # Generate valid TOTP code
        totp = pyotp.TOTP(two_fa_key)
        two_fa_code = totp.now()

        # Act
        response = await test_client.post(
            "/api/account/2fa/set",
            json={
                "google_two_fa_key": two_fa_key,
                "google_two_fa_code": two_fa_code
            },
            cookies={"Access-Token": access_token}
        )

        # Assert
        assert response.status_code == 200

    async def test_set_two_fa_invalid_code(self, test_client, mock_loom_authorization_client):
        # Arrange
        login = "2fa_invalid_user"
        password = "password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        two_fa_key = pyotp.random_base32()

        # Act - use invalid code
        response = await test_client.post(
            "/api/account/2fa/set",
            json={
                "google_two_fa_key": two_fa_key,
                "google_two_fa_code": "000000"  # invalid
            },
            cookies={"Access-Token": access_token}
        )

        # Assert
        assert response.status_code == 500

    async def test_set_two_fa_already_enabled(self, test_client, mock_loom_authorization_client):
        # Arrange - enable 2FA first
        login = "2fa_already_user"
        password = "password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        # Enable 2FA
        two_fa_key = pyotp.random_base32()
        totp = pyotp.TOTP(two_fa_key)
        two_fa_code = totp.now()

        await test_client.post(
            "/api/account/2fa/set",
            json={
                "google_two_fa_key": two_fa_key,
                "google_two_fa_code": two_fa_code
            },
            cookies={"Access-Token": access_token}
        )

        # Act - try to enable again
        new_key = pyotp.random_base32()
        new_totp = pyotp.TOTP(new_key)
        new_code = new_totp.now()

        response = await test_client.post(
            "/api/account/2fa/set",
            json={
                "google_two_fa_key": new_key,
                "google_two_fa_code": new_code
            },
            cookies={"Access-Token": access_token}
        )

        # Assert
        assert response.status_code == 500

    async def test_delete_two_fa_success(self, test_client, mock_loom_authorization_client):
        # Arrange - enable 2FA first
        login = "2fa_delete_user"
        password = "password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        two_fa_key = pyotp.random_base32()
        totp = pyotp.TOTP(two_fa_key)
        two_fa_code = totp.now()

        await test_client.post(
            "/api/account/2fa/set",
            json={
                "google_two_fa_key": two_fa_key,
                "google_two_fa_code": two_fa_code
            },
            cookies={"Access-Token": access_token}
        )

        # Act - delete 2FA
        delete_code = totp.now()  # Generate new code for deletion
        response = await test_client.delete(
            "/api/account/2fa/delete",
            json={"google_two_fa_code": delete_code},
            cookies={"Access-Token": access_token}
        )

        # Assert
        assert response.status_code == 200

    async def test_delete_two_fa_not_enabled(self, test_client, mock_loom_authorization_client):
        # Arrange
        login = "2fa_not_enabled_user"
        password = "password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        # Act - try to delete when not enabled
        response = await test_client.delete(
            "/api/account/2fa/delete",
            json={"google_two_fa_code": "123456"},
            cookies={"Access-Token": access_token}
        )

        # Assert
        assert response.status_code == 500

    async def test_delete_two_fa_invalid_code(self, test_client, mock_loom_authorization_client):
        # Arrange - enable 2FA
        login = "2fa_delete_invalid_user"
        password = "password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        two_fa_key = pyotp.random_base32()
        totp = pyotp.TOTP(two_fa_key)
        two_fa_code = totp.now()

        await test_client.post(
            "/api/account/2fa/set",
            json={
                "google_two_fa_key": two_fa_key,
                "google_two_fa_code": two_fa_code
            },
            cookies={"Access-Token": access_token}
        )

        # Act - delete with invalid code
        response = await test_client.delete(
            "/api/account/2fa/delete",
            json={"google_two_fa_code": "000000"},
            cookies={"Access-Token": access_token}
        )

        # Assert
        assert response.status_code == 500

    async def test_verify_two_fa_success(self, test_client, mock_loom_authorization_client):
        # Arrange - enable 2FA
        login = "2fa_verify_user"
        password = "password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        two_fa_key = pyotp.random_base32()
        totp = pyotp.TOTP(two_fa_key)
        two_fa_code = totp.now()

        await test_client.post(
            "/api/account/2fa/set",
            json={
                "google_two_fa_key": two_fa_key,
                "google_two_fa_code": two_fa_code
            },
            cookies={"Access-Token": access_token}
        )

        # Act - verify with valid code
        verify_code = totp.now()
        response = await test_client.post(
            "/api/account/2fa/verify",
            json={"google_two_fa_code": verify_code},
            cookies={"Access-Token": access_token}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] == True

    async def test_verify_two_fa_invalid_code(self, test_client, mock_loom_authorization_client):
        # Arrange - enable 2FA
        login = "2fa_verify_invalid_user"
        password = "password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        two_fa_key = pyotp.random_base32()
        totp = pyotp.TOTP(two_fa_key)
        two_fa_code = totp.now()

        await test_client.post(
            "/api/account/2fa/set",
            json={
                "google_two_fa_key": two_fa_key,
                "google_two_fa_code": two_fa_code
            },
            cookies={"Access-Token": access_token}
        )

        # Act - verify with invalid code
        response = await test_client.post(
            "/api/account/2fa/verify",
            json={"google_two_fa_code": "000000"},
            cookies={"Access-Token": access_token}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] == False

    async def test_verify_two_fa_not_enabled(self, test_client, mock_loom_authorization_client):
        # Arrange
        login = "2fa_verify_not_enabled"
        password = "password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        # Act - verify when 2FA not enabled
        response = await test_client.post(
            "/api/account/2fa/verify",
            json={"google_two_fa_code": "123456"},
            cookies={"Access-Token": access_token}
        )

        # Assert
        assert response.status_code == 500


class TestAccountApiPassword:
    async def test_recovery_password_success(self, test_client, mock_loom_authorization_client):
        # Arrange - create user
        login = "password_recovery_user"
        password = "old_password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        # Act - recovery password (no old password needed)
        new_password = "new_password"
        response = await test_client.post(
            "/api/account/password/recovery",
            json={"new_password": new_password},
            cookies={"Access-Token": access_token}
        )

        # Assert
        assert response.status_code == 200

        # Verify can login with new password
        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="new_login_token",
            refresh_token="new_refresh_token"
        )
        login_response = await test_client.post(
            "/api/account/login",
            json={"login": login, "password": new_password}
        )
        assert login_response.status_code == 200

        # Verify cannot login with old password
        old_login_response = await test_client.post(
            "/api/account/login",
            json={"login": login, "password": password}
        )
        assert old_login_response.status_code == 500

    async def test_recovery_password_unauthorized(self, test_client):
        # Act - without access token
        response = await test_client.post(
            "/api/account/password/recovery",
            json={"new_password": "new_password"}
        )

        # Assert
        assert response.status_code == 403

    async def test_change_password_success(self, test_client, mock_loom_authorization_client):
        # Arrange - create user
        login = "password_change_user"
        old_password = "old_password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": old_password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        # Act - change password with old password verification
        new_password = "new_password"
        response = await test_client.put(
            "/api/account/password/change",
            json={
                "old_password": old_password,
                "new_password": new_password
            },
            cookies={"Access-Token": access_token}
        )

        # Assert
        assert response.status_code == 200

        # Verify can login with new password
        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="new_login_token",
            refresh_token="new_refresh_token"
        )
        login_response = await test_client.post(
            "/api/account/login",
            json={"login": login, "password": new_password}
        )
        assert login_response.status_code == 200

    async def test_change_password_invalid_old_password(
        self, test_client, mock_loom_authorization_client
    ):
        # Arrange - create user
        login = "password_change_invalid_user"
        password = "correct_password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        # Act - change with wrong old password
        response = await test_client.put(
            "/api/account/password/change",
            json={
                "old_password": "wrong_password",
                "new_password": "new_password"
            },
            cookies={"Access-Token": access_token}
        )

        # Assert
        assert response.status_code == 500

    async def test_change_password_unauthorized(self, test_client):
        # Act - without access token
        response = await test_client.put(
            "/api/account/password/change",
            json={
                "old_password": "old",
                "new_password": "new"
            }
        )

        # Assert
        assert response.status_code == 403

    @pytest.mark.parametrize("new_password", [
        pytest.param("", id="empty"),
        pytest.param("a", id="single_char"),
        pytest.param("x" * 1000, id="very_long"),
        pytest.param("?0@>;L123", id="unicode"),
    ])
    async def test_change_password_edge_cases(
        self, test_client, mock_loom_authorization_client, new_password
    ):
        # Arrange
        login = f"edge_case_user_{new_password[:10]}"
        old_password = "old_password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="test_token",
            refresh_token="test_token"
        )
        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": old_password}
        )
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        # Act
        response = await test_client.put(
            "/api/account/password/change",
            json={
                "old_password": old_password,
                "new_password": new_password
            },
            cookies={"Access-Token": access_token}
        )

        # Assert
        assert response.status_code == 200


class TestAccountApiFullFlow:
    async def test_complete_user_lifecycle(self, test_client, mock_loom_authorization_client):
        """Test complete user lifecycle: register -> login -> enable 2FA -> change password -> login with new password"""

        # Step 1: Register
        login = "lifecycle_user"
        password = "initial_password"

        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="register_token",
            refresh_token="register_refresh"
        )

        register_response = await test_client.post(
            "/api/account/register",
            json={"login": login, "password": password}
        )
        assert register_response.status_code == 201
        account_id = register_response.json()["account_id"]
        access_token = register_response.cookies["Access-Token"]

        # Step 2: Login
        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="login_token",
            refresh_token="login_refresh"
        )

        login_response = await test_client.post(
            "/api/account/login",
            json={"login": login, "password": password}
        )
        assert login_response.status_code == 200
        assert login_response.json()["account_id"] == account_id

        # Step 3: Enable 2FA
        mock_loom_authorization_client.check_authorization.return_value = model.AuthorizationData(
            account_id=account_id,
            two_fa_status=False,
            role="employee",
            message="ok",
            status_code=200
        )

        gen_response = await test_client.get(
            "/api/account/2fa/generate",
            cookies={"Access-Token": access_token}
        )
        assert gen_response.status_code == 200
        two_fa_key = gen_response.headers["X-TwoFA-Key"]

        totp = pyotp.TOTP(two_fa_key)
        two_fa_code = totp.now()

        set_response = await test_client.post(
            "/api/account/2fa/set",
            json={
                "google_two_fa_key": two_fa_key,
                "google_two_fa_code": two_fa_code
            },
            cookies={"Access-Token": access_token}
        )
        assert set_response.status_code == 200

        # Step 4: Verify 2FA
        verify_code = totp.now()
        verify_response = await test_client.post(
            "/api/account/2fa/verify",
            json={"google_two_fa_code": verify_code},
            cookies={"Access-Token": access_token}
        )
        assert verify_response.status_code == 200
        assert verify_response.json()["is_valid"] == True

        # Step 5: Change password
        new_password = "new_secure_password"
        change_response = await test_client.put(
            "/api/account/password/change",
            json={
                "old_password": password,
                "new_password": new_password
            },
            cookies={"Access-Token": access_token}
        )
        assert change_response.status_code == 200

        # Step 6: Login with new password (2FA should be enabled)
        mock_loom_authorization_client.authorization.return_value = model.JWTTokens(
            access_token="final_login_token",
            refresh_token="final_refresh"
        )

        final_login_response = await test_client.post(
            "/api/account/login",
            json={"login": login, "password": new_password}
        )
        assert final_login_response.status_code == 200

        # Verify authorization was called with two_fa_status=True
        last_call = mock_loom_authorization_client.authorization.call_args
        assert last_call[0][1] == True  # two_fa_status

        # Step 7: Delete 2FA
        delete_code = totp.now()
        delete_response = await test_client.delete(
            "/api/account/2fa/delete",
            json={"google_two_fa_code": delete_code},
            cookies={"Access-Token": access_token}
        )
        assert delete_response.status_code == 200
