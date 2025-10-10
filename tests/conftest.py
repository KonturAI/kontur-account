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

@pytest.fixture
def mock_loom_authorization_client(mocker):
    return mocker.AsyncMock(spec=interface.ILoomAuthorizationClient)

@pytest.fixture
def mock_tel(mocker):
    mock_logger = mocker.MagicMock(spec=interface.IOtelLogger)
    mock_tracer = mocker.MagicMock()
    mock_meter = mocker.MagicMock()

    mock_tel = mocker.MagicMock(spec=interface.ITelemetry)
    mock_tel.logger.return_value = mock_logger
    mock_tel.tracer.return_value = mock_tracer
    mock_tel.meter.return_value = mock_meter

    return mock_tel