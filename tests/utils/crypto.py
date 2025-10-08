import bcrypt

from internal import model


def hash_password(password: str, secret_key: str = "test_secret") -> str:
    peppered_password = secret_key + password
    hashed_password = bcrypt.hashpw(peppered_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def make_hashed_account(
    login: str,
    password: str,
    secret_key: str = "test_secret",
    **kwargs
) -> model.Account:
    from tests.factories.account_factory import AccountFactory

    hashed = hash_password(password, secret_key)
    return AccountFactory(login=login, password=hashed, **kwargs)
