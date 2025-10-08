import factory
from factory import Faker, Trait
from datetime import datetime
from internal import model


class AccountFactory(factory.Factory):
    class Meta:
        model = model.Account

    id = factory.Sequence(lambda n: n + 1)
    login = Faker("user_name")
    password = Faker("password", length=20)
    google_two_fa_key = ""
    created_at = factory.LazyFunction(datetime.now)

    class Params:
        # Trait: Account с 2FA
        with_2fa = Trait(
            google_two_fa_key=Faker("pystr", max_chars=32)
        )

    @factory.lazy_attribute
    def created_at(self):
        return datetime.now()


class AccountWithTwoFAFactory(AccountFactory):
    google_two_fa_key = Faker("pystr", max_chars=32)


# Convenience functions для частых сценариев
def create_account(**kwargs) -> model.Account:
    return AccountFactory(**kwargs)


def create_account_with_2fa(**kwargs) -> model.Account:
    return AccountWithTwoFAFactory(**kwargs)


def create_accounts(count: int, **kwargs) -> list[model.Account]:
    return AccountFactory.create_batch(count, **kwargs)
