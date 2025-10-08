import pytest
from contextvars import ContextVar

from internal import interface

# ============================================================================
# FACTORIES - для создания тестовых данных
# ============================================================================

@pytest.fixture
def account_factory():
    from tests.factories.account_factory import AccountFactory
    return AccountFactory


@pytest.fixture
def account_with_2fa_factory():
    from tests.factories.account_factory import AccountWithTwoFAFactory
    return AccountWithTwoFAFactory


@pytest.fixture
def jwt_tokens_factory():
    from tests.factories.auth_factory import JWTTokensFactory
    return JWTTokensFactory


@pytest.fixture
def authorization_data_factory():
    from tests.factories.auth_factory import AuthorizationDataFactory
    return AuthorizationDataFactory


@pytest.fixture
def authorization_data_dto_factory():
    from tests.factories.auth_factory import AuthorizationDataDTOFactory
    return AuthorizationDataDTOFactory


# ============================================================================
# ГОТОВЫЕ ДАННЫЕ - готовые экземпляры для быстрого использования
# ============================================================================

@pytest.fixture
def account(account_factory):
    return account_factory()


@pytest.fixture
def account_with_2fa(account_with_2fa_factory):
    return account_with_2fa_factory()


@pytest.fixture
def jwt_tokens(jwt_tokens_factory):
    return jwt_tokens_factory()


@pytest.fixture
def authorization_data(authorization_data_factory):
    return authorization_data_factory()


@pytest.fixture
def authorization_data_dto(authorization_data_dto_factory):
    return authorization_data_dto_factory()


# ============================================================================
# БАЗОВЫЕ МОКИ - используем pytest-mock
# ============================================================================

@pytest.fixture
def mock_telemetry(mocker):
    mock_logger = mocker.MagicMock(spec=interface.IOtelLogger)
    mock_tracer = mocker.MagicMock()
    mock_meter = mocker.MagicMock()

    mock_tel = mocker.MagicMock(spec=interface.ITelemetry)
    mock_tel.logger.return_value = mock_logger
    mock_tel.tracer.return_value = mock_tracer
    mock_tel.meter.return_value = mock_meter

    return mock_tel


@pytest.fixture
def mock_db(mocker):
    return mocker.AsyncMock(spec=interface.IDB)


@pytest.fixture
def mock_account_repo(mocker):
    return mocker.AsyncMock(spec=interface.IAccountRepo)


@pytest.fixture
def mock_loom_authorization_client(mocker):
    return mocker.AsyncMock(spec=interface.ILoomAuthorizationClient)


# ============================================================================
# КОНСТАНТЫ И КОНФИГУРАЦИЯ
# ============================================================================

@pytest.fixture
def password_secret() -> str:
    return "test_secret_key_for_testing"


@pytest.fixture
def log_context() -> ContextVar[dict]:
    return ContextVar('log_context', default={})


# ============================================================================
# PYTEST КОНФИГУРАЦИЯ
# ============================================================================

def pytest_configure(config):
    config.addinivalue_line("markers", "unit: Unit tests (быстрые, с моками)")
    config.addinivalue_line("markers", "integration: Integration tests (медленные, с реальными компонентами)")
    config.addinivalue_line("markers", "api: API integration tests")
    config.addinivalue_line("markers", "repo: Repository integration tests (testcontainers)")
    config.addinivalue_line("markers", "client: Client integration tests (respx)")
