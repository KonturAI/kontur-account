import factory
from factory import Faker
from datetime import datetime
from internal import model


class AccountFactory(factory.Factory):
    class Meta:
        model = model.Account

    id = factory.Sequence(lambda n: n + 1)
    login = Faker("user_name")
    password = Faker("password")
    google_two_fa_key = ""
    created_at = factory.LazyFunction(datetime.now)


class AccountWithTwoFAFactory(AccountFactory):
    google_two_fa_key = Faker("pystr", max_chars=32)
