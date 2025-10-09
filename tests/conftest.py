import pytest
from contextvars import ContextVar

from internal import interface
from tests.factories import AccountFactory


TEST_PASSWORD_SECRET = "test_secret_key_for_testing"


@pytest.fixture(autouse=True)
def reset_log_context(log_context):
    yield
    try:
        log_context.set({})
    except LookupError:
        pass


@pytest.fixture(autouse=True)
def reset_factory_counter():
    AccountFactory.reset_counter()
    yield


@pytest.fixture(scope="session")
def log_context() -> ContextVar[dict]:
    return ContextVar('log_context', default={})


@pytest.fixture
def password_secret() -> str:
    return TEST_PASSWORD_SECRET