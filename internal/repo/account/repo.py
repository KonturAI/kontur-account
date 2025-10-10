from internal import common, interface, model
from pkg.trace_wrapper import traced_method

from .sql_query import *


class AccountRepo(interface.IAccountRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB,
    ):
        self.tracer = tel.tracer()
        self.db = db

    @traced_method()
    async def create_account(self, login: str, password: str) -> int:
        existing_accounts = await self.account_by_login(login)
        if existing_accounts:
            raise common.ErrAccountCreate()

        args = {
            'login': login,
            'password': password,
        }

        account_id = await self.db.insert(create_account, args)

        return account_id

    @traced_method()
    async def account_by_id(self, account_id: int) -> list[model.Account]:
        args = {'account_id': account_id}
        rows = await self.db.select(get_account_by_id, args)
        accounts = model.Account.serialize(rows) if rows else []

        return accounts

    @traced_method()
    async def account_by_login(self, login: str) -> list[model.Account]:
        args = {'login': login}
        rows = await self.db.select(get_account_by_login, args)
        accounts = model.Account.serialize(rows) if rows else []
        return accounts

    @traced_method()
    async def set_two_fa_key(self, account_id: int, google_two_fa_key: str) -> None:
        args = {
            'account_id': account_id,
            'google_two_fa_key': google_two_fa_key,
        }
        await self.db.update(set_two_fa_key, args)

    @traced_method()
    async def delete_two_fa_key(self, account_id: int) -> None:
        args = {'account_id': account_id}
        await self.db.update(delete_two_fa_key, args)

    @traced_method()
    async def update_password(self, account_id: int, new_password: str) -> None:
        args = {
            'account_id': account_id,
            'new_password': new_password,
        }
        await self.db.update(update_password, args)
