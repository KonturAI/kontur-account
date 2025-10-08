import pytest

from tests.factories.account_factory import AccountFactory, AccountWithTwoFAFactory
from tests.factories.auth_factory import (
    JWTTokensFactory,
    AuthorizationDataFactory,
    AuthorizationDataDTOFactory
)

@pytest.fixture
def account_factory():
    return AccountFactory


@pytest.fixture
def account_with_two_fa_factory():
    return AccountWithTwoFAFactory


@pytest.fixture
def jwt_tokens_factory():
    return JWTTokensFactory


@pytest.fixture
def authorization_data_factory():
    return AuthorizationDataFactory


@pytest.fixture
def authorization_data_dto_factory():
    return AuthorizationDataDTOFactory


@pytest.fixture
def test_account():
    return AccountFactory()


@pytest.fixture
def test_account_with_2fa():
    return AccountWithTwoFAFactory()


@pytest.fixture
def test_jwt_tokens():
    return JWTTokensFactory()
