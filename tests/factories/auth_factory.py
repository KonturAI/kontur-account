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

        # Trait: With 2FA enabled
        with_2fa = Trait(
            two_fa_status=True
        )

        # Role traits
        admin = Trait(role="admin")
        employee = Trait(role="employee")
        manager = Trait(role="manager")


class AuthorizationDataDTOFactory(factory.Factory):
    class Meta:
        model = model.AuthorizationDataDTO

    account_id = factory.Sequence(lambda n: n + 1)
    access_token = Faker("uuid4")
    refresh_token = Faker("uuid4")
