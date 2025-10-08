from internal import model


def assert_authorization_dto(
    dto: model.AuthorizationDataDTO,
    account_id: int = None
) -> None:
    assert dto is not None, "AuthorizationDataDTO must not be None"
    assert dto.access_token, "Access token must not be empty"
    assert dto.refresh_token, "Refresh token must not be empty"

    if account_id is not None:
        assert dto.account_id == account_id, (
            f"Account ID: {dto.account_id} != {account_id}"
        )