from typing import Optional, Any

from internal import model


def assert_authorization_dto(
    dto: model.AuthorizationDataDTO,
    account_id: Optional[int] = None,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None
) -> None:
    assert dto is not None, "AuthorizationDataDTO must not be None"
    assert dto.access_token, "Access token must not be empty"
    assert dto.refresh_token, "Refresh token must not be empty"
    assert dto.account_id > 0, f"Account ID must be positive, got {dto.account_id}"

    if account_id is not None:
        assert dto.account_id == account_id, (
            f"Account ID mismatch: expected {account_id}, got {dto.account_id}"
        )

    if access_token is not None:
        assert dto.access_token == access_token, (
            f"Access token mismatch: expected {access_token}, got {dto.access_token}"
        )

    if refresh_token is not None:
        assert dto.refresh_token == refresh_token, (
            f"Refresh token mismatch: expected {refresh_token}, got {dto.refresh_token}"
        )


def assert_account_valid(
    account: model.Account,
    account_id: Optional[int] = None,
    login: Optional[str] = None,
    has_2fa: Optional[bool] = None
) -> None:
    assert account is not None, "Account must not be None"
    assert account.id > 0, f"Account ID must be positive, got {account.id}"
    assert account.login, "Account login must not be empty"
    assert account.password, "Account password must not be empty"

    if account_id is not None:
        assert account.id == account_id, (
            f"Account ID mismatch: expected {account_id}, got {account.id}"
        )

    if login is not None:
        assert account.login == login, (
            f"Login mismatch: expected {login}, got {account.login}"
        )

    if has_2fa is not None:
        actual_has_2fa = bool(account.google_two_fa_key)
        assert actual_has_2fa == has_2fa, (
            f"2FA status mismatch: expected {has_2fa}, got {actual_has_2fa}"
        )


def assert_jwt_tokens_valid(
    tokens: model.JWTTokens,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None
) -> None:
    assert tokens is not None, "JWTTokens must not be None"
    assert tokens.access_token, "Access token must not be empty"
    assert tokens.refresh_token, "Refresh token must not be empty"

    if access_token is not None:
        assert tokens.access_token == access_token, (
            f"Access token mismatch: expected {access_token}, got {tokens.access_token}"
        )

    if refresh_token is not None:
        assert tokens.refresh_token == refresh_token, (
            f"Refresh token mismatch: expected {refresh_token}, got {tokens.refresh_token}"
        )


def assert_response_has_cookie(
    response: Any,
    cookie_name: str,
    cookie_value: Optional[str] = None
) -> None:
    assert hasattr(response, 'cookies'), "Response must have cookies attribute"

    if hasattr(response.cookies, 'get'):
        cookie_found = response.cookies.get(cookie_name) is not None
        assert cookie_found, f"Cookie '{cookie_name}' not found in response"

        if cookie_value is not None:
            actual_value = response.cookies.get(cookie_name)
            assert actual_value == cookie_value, (
                f"Cookie '{cookie_name}' value mismatch: expected {cookie_value}, got {actual_value}"
            )
    else:
        raise AssertionError("Response cookies format not supported")
