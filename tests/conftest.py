import pytest
from contextvars import ContextVar

from tests.mocks.telemetry_mock import MockTelemetry, MockOtelLogger
from tests.mocks.loom_authorization_mock import MockLoomAuthorizationClient
from tests.mocks.db_mock import MockDB
from tests.mocks.repo_mock import MockAccountRepo

@pytest.fixture
def mock_logger():
    return MockOtelLogger()


@pytest.fixture
def mock_telemetry():
    return MockTelemetry()


@pytest.fixture
def mock_loom_authorization_client():
    return MockLoomAuthorizationClient()


@pytest.fixture
def mock_db():
    return MockDB()


@pytest.fixture
def mock_account_repo():
    return MockAccountRepo()

@pytest.fixture
def test_password_secret():
    return "test_secret_key"


@pytest.fixture
def log_context():
    return ContextVar('log_context', default={})


@pytest.fixture(autouse=True)
def reset_mocks(
    mock_logger,
    mock_loom_authorization_client,
    mock_db,
    mock_account_repo
):
    yield
    if hasattr(mock_logger, 'clear_logs'):
        mock_logger.clear_logs()
    if hasattr(mock_loom_authorization_client, 'clear_call_history'):
        mock_loom_authorization_client.clear_call_history()
    if hasattr(mock_db, 'clear_call_history'):
        mock_db.clear_call_history()
        mock_db.reset_id_counter()
    if hasattr(mock_account_repo, 'clear_call_history'):
        mock_account_repo.clear_call_history()
        mock_account_repo.clear_accounts()
