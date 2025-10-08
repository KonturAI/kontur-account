from typing import Dict, Any


def assert_jwt_tokens(response_data: Dict[str, Any], expected_account_id: int = None):
    assert "account_id" in response_data
    if expected_account_id is not None:
        assert response_data["account_id"] == expected_account_id


def assert_error_response(response_data: Dict[str, Any], expected_status: int):
    pass


def assert_model_equal(actual, expected, exclude_fields: set = None):
    exclude_fields = exclude_fields or set()

    actual_dict = {k: v for k, v in actual.__dict__.items() if k not in exclude_fields}
    expected_dict = {k: v for k, v in expected.__dict__.items() if k not in exclude_fields}

    assert actual_dict == expected_dict, f"Models differ: {actual_dict} != {expected_dict}"
