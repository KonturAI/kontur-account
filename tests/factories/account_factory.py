import factory
from factory import Faker, Trait, LazyAttribute
from datetime import datetime, timezone

from internal import model


class AccountFactory(factory.Factory):
    class Meta:
        model = model.Account

    id = factory.Sequence(lambda n: n + 10000)
    login = Faker("user_name")
    password = Faker("password", length=60)
    google_two_fa_key = ""
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Params:
        with_2fa = Trait(
            google_two_fa_key=Faker("pystr", min_chars=32, max_chars=32)
        )


class AccountWithTwoFAFactory(AccountFactory):
    google_two_fa_key = Faker("pystr", min_chars=32, max_chars=32)


def create_account(**kwargs) -> model.Account:
    return AccountFactory(**kwargs)


def create_account_with_2fa(**kwargs) -> model.Account:
    return AccountWithTwoFAFactory(**kwargs)


def create_accounts(count: int, **kwargs) -> list[model.Account]:
    return AccountFactory.create_batch(count, **kwargs)
