import pytest
import respx

from pkg.client.internal.loom_authorization.client import LoomAuthorizationClient


@pytest.fixture(autouse=True)
def enable_respx():
    with respx.mock:
        yield


@pytest.fixture
def loom_authorization_client(tel, log_context):
    return LoomAuthorizationClient(
        tel=tel,
        host="localhost",
        port=8080,
        log_context=log_context
    )
