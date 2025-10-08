import bcrypt
from typing import Any
from unittest.mock import MagicMock


def hash_password(password: str, secret_key: str = "test_secret") -> str:
    peppered_password = secret_key + password
    hashed_password = bcrypt.hashpw(peppered_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def create_mock_db_row(**kwargs) -> Any:
    mock_row = MagicMock()
    for key, value in kwargs.items():
        setattr(mock_row, key, value)
    return mock_row


def assert_called_with_partial(mock_call, **expected_kwargs):
    actual_call = mock_call.call_args
    if actual_call is None:
        raise AssertionError("Mock was not called")

    actual_kwargs = actual_call.kwargs
    for key, expected_value in expected_kwargs.items():
        if key not in actual_kwargs:
            raise AssertionError(f"Expected kwarg '{key}' not found in call")
        if actual_kwargs[key] != expected_value:
            raise AssertionError(
                f"Expected {key}={expected_value}, got {key}={actual_kwargs[key]}"
            )
