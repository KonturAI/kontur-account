from internal import model


class MockAccountRepo:
    def __init__(self):
        self._accounts = {}
        self._next_id = 1
        self._call_history = []

    async def create_account(self, login: str, password: str) -> int:
        self._call_history.append({
            "method": "create_account",
            "login": login,
            "password": password
        })

        for account in self._accounts.values():
            if account.login == login:
                from internal.common import ErrAccountCreate
                raise ErrAccountCreate()

        account_id = self._next_id
        self._next_id += 1

        from datetime import datetime
        self._accounts[account_id] = model.Account(
            id=account_id,
            login=login,
            password=password,
            google_two_fa_key="",
            created_at=datetime.now()
        )

        return account_id

    async def account_by_id(self, account_id: int) -> list[model.Account]:
        self._call_history.append({
            "method": "account_by_id",
            "account_id": account_id
        })

        if account_id in self._accounts:
            return [self._accounts[account_id]]
        return []

    async def account_by_login(self, login: str) -> list[model.Account]:
        self._call_history.append({
            "method": "account_by_login",
            "login": login
        })

        for account in self._accounts.values():
            if account.login == login:
                return [account]
        return []

    async def set_two_fa_key(self, account_id: int, google_two_fa_key: str) -> None:
        self._call_history.append({
            "method": "set_two_fa_key",
            "account_id": account_id,
            "google_two_fa_key": google_two_fa_key
        })

        if account_id in self._accounts:
            account = self._accounts[account_id]
            self._accounts[account_id] = model.Account(
                id=account.id,
                login=account.login,
                password=account.password,
                google_two_fa_key=google_two_fa_key,
                created_at=account.created_at
            )

    async def delete_two_fa_key(self, account_id: int) -> None:
        self._call_history.append({
            "method": "delete_two_fa_key",
            "account_id": account_id
        })

        if account_id in self._accounts:
            account = self._accounts[account_id]
            self._accounts[account_id] = model.Account(
                id=account.id,
                login=account.login,
                password=account.password,
                google_two_fa_key="",
                created_at=account.created_at
            )

    async def update_password(self, account_id: int, new_password: str) -> None:
        self._call_history.append({
            "method": "update_password",
            "account_id": account_id,
            "new_password": new_password
        })

        if account_id in self._accounts:
            account = self._accounts[account_id]
            self._accounts[account_id] = model.Account(
                id=account.id,
                login=account.login,
                password=new_password,
                google_two_fa_key=account.google_two_fa_key,
                created_at=account.created_at
            )

    def add_account(self, account: model.Account) -> None:
        self._accounts[account.id] = account
        if account.id >= self._next_id:
            self._next_id = account.id + 1

    def get_call_history(self) -> list:
        return self._call_history

    def clear_call_history(self) -> None:
        self._call_history = []

    def clear_accounts(self) -> None:
        self._accounts = {}
        self._next_id = 1
