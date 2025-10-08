import factory
from factory import Faker
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


class AuthorizationDataDTOFactory(factory.Factory):
    class Meta:
        model = model.AuthorizationDataDTO

    account_id = factory.Sequence(lambda n: n + 1)
    access_token = Faker("uuid4")
    refresh_token = Faker("uuid4")
