import bcrypt

from internal import model
from tests.conftest import TEST_PASSWORD_SECRET


def hash_password(password: str, secret_key: str = TEST_PASSWORD_SECRET) -> str:
    peppered_password = secret_key + password
    hashed_password = bcrypt.hashpw(peppered_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def verify_password(password: str, hashed: str, secret_key: str = TEST_PASSWORD_SECRET) -> bool:
    peppered_password = secret_key + password
    return bcrypt.checkpw(peppered_password.encode('utf-8'), hashed.encode('utf-8'))


def make_hashed_account(
    login: str,
    password: str,
    secret_key: str = TEST_PASSWORD_SECRET,
    **kwargs
) -> model.Account:
    from tests.factories.account_factory import AccountFactory

    hashed = hash_password(password, secret_key)
    return AccountFactory(login=login, password=hashed, **kwargs)
