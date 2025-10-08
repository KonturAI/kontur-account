import pytest
from contextvars import ContextVar

from internal import interface


# ============================================================================
# БАЗОВЫЕ МОКИ для unit-тестов
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
    config.addinivalue_line(
        "markers",
        "unit: Unit tests (fast, isolated, with mocks)"
    )
    config.addinivalue_line(
        "markers",
        "integration: Integration tests (slower, with real components)"
    )
    config.addinivalue_line(
        "markers",
        "api: API integration tests (full HTTP stack)"
    )
    config.addinivalue_line(
        "markers",
        "repo: Repository integration tests (requires database)"
    )
    config.addinivalue_line(
        "markers",
        "client: Client integration tests (HTTP client tests with respx)"
    )
