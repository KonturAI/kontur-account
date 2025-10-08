import factory
from factory import Faker, Trait
from internal import model


class JWTTokensFactory(factory.Factory):
    class Meta:
        model = model.JWTTokens

    access_token = Faker("uuid4")
    refresh_token = Faker("uuid4")


class AuthorizationDataFactory(factory.Factory):
    class Meta:
        model = model.AuthorizationData

    account_id = factory.Sequence(lambda n: n + 1)
    two_fa_status = False
    role = "employee"
    message = "OK"
    status_code = 200

    class Params:
        # Trait: Failed authorization
        failed = Trait(
            message="Unauthorized",
            status_code=401
        )

        # Trait: Forbidden
        forbidden = Trait(
            message="Forbidden",
            status_code=403
        )

        # Trait: С 2FA
        with_2fa = Trait(
            two_fa_status=True
        )

        # Параметр: роль (удобный способ установить роль)
        admin = Trait(role="admin")
        employee = Trait(role="employee")
        manager = Trait(role="manager")


class AuthorizationDataDTOFactory(factory.Factory):
    class Meta:
        model = model.AuthorizationDataDTO

    account_id = factory.Sequence(lambda n: n + 1)
    access_token = Faker("uuid4")
    refresh_token = Faker("uuid4")


# Convenience functions для частых сценариев

def create_jwt_tokens(**kwargs) -> model.JWTTokens:
    return JWTTokensFactory(**kwargs)


def create_authorization_data(
    account_id: int = None,
    two_fa: bool = False,
    role: str = "employee",
    **kwargs
) -> model.AuthorizationData:
    return AuthorizationDataFactory(
        account_id=account_id or factory.Sequence(lambda n: n + 1),
        two_fa_status=two_fa,
        role=role,
        **kwargs
    )


def create_authorization_dto(**kwargs) -> model.AuthorizationDataDTO:
    return AuthorizationDataDTOFactory(**kwargs)
