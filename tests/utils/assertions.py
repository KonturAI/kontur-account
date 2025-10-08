from typing import Optional

from internal import model


def assert_authorization_dto(
    dto: model.AuthorizationDataDTO,
    account_id: Optional[int] = None
) -> None:
    assert dto is not None, "AuthorizationDataDTO must not be None"
    assert dto.access_token, "Access token must not be empty"
    assert dto.refresh_token, "Refresh token must not be empty"

    if account_id is not None:
        assert dto.account_id == account_id, (
            f"Account ID mismatch: expected {account_id}, got {dto.account_id}"
        )


def assert_account_valid(
    account: model.Account,
    login: Optional[str] = None,
    has_2fa: Optional[bool] = None
) -> None:
    assert account is not None, "Account must not be None"
    assert account.id > 0, f"Account ID must be positive, got {account.id}"
    assert account.login, "Account login must not be empty"
    assert account.password, "Account password must not be empty"

    if login is not None:
        assert account.login == login, (
            f"Login mismatch: expected {login}, got {account.login}"
        )

    if has_2fa is not None:
        actual_has_2fa = bool(account.google_two_fa_key)
        assert actual_has_2fa == has_2fa, (
            f"2FA status mismatch: expected {has_2fa}, got {actual_has_2fa}"
        )


def assert_jwt_tokens_valid(tokens: model.JWTTokens) -> None:
    assert tokens is not None, "JWTTokens must not be None"
    assert tokens.access_token, "Access token must not be empty"
    assert tokens.refresh_token, "Refresh token must not be empty"


def assert_response_has_cookie(
    response,
    cookie_name: str,
    cookie_value: Optional[str] = None
) -> None:
    cookies = response.headers.getlist("set-cookie")
    cookie_found = any(cookie_name in cookie for cookie in cookies)

    assert cookie_found, (
        f"Cookie '{cookie_name}' not found in response. "
        f"Available cookies: {[c.split('=')[0] for c in cookies]}"
    )

    if cookie_value is not None:
        cookie_with_value = any(
            cookie_name in cookie and cookie_value in cookie
            for cookie in cookies
        )
        assert cookie_with_value, (
            f"Cookie '{cookie_name}' exists but value '{cookie_value}' not found"
        )
