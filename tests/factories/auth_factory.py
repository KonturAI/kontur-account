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

    account_id = factory.Sequence(lambda n: n + 10000)
    two_fa_status = False
    role = "employee"
    message = "OK"
    status_code = 200

    class Params:
        failed = Trait(
            message="Unauthorized",
            status_code=401
        )

        forbidden = Trait(
            message="Forbidden",
            status_code=403
        )

        with_2fa = Trait(
            two_fa_status=True
        )

        admin = Trait(role="admin")
        employee = Trait(role="employee")
        manager = Trait(role="manager")


class AuthorizationDataDTOFactory(factory.Factory):
    class Meta:
        model = model.AuthorizationDataDTO

    account_id = factory.Sequence(lambda n: n + 10000)
    access_token = Faker("uuid4")
    refresh_token = Faker("uuid4")
