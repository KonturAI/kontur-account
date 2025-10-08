from internal import model


class MockLoomAuthorizationClient:
    def __init__(self):
        self._authorization_responses = {}
        self._authorization_tg_responses = {}
        self._check_authorization_responses = {}
        self._call_history = []

    async def authorization(
        self,
        account_id: int,
        two_fa_status: bool,
        role: str
    ) -> model.JWTTokens:
        self._call_history.append({
            "method": "authorization",
            "account_id": account_id,
            "two_fa_status": two_fa_status,
            "role": role
        })

        key = (account_id, two_fa_status, role)
        if key in self._authorization_responses:
            return self._authorization_responses[key]

        # Дефолтный ответ
        return model.JWTTokens(
            access_token=f"access_token_{account_id}",
            refresh_token=f"refresh_token_{account_id}"
        )

    async def authorization_tg(
        self,
        account_id: int,
        two_fa_status: bool,
        role: str
    ) -> model.JWTTokens:
        self._call_history.append({
            "method": "authorization_tg",
            "account_id": account_id,
            "two_fa_status": two_fa_status,
            "role": role
        })

        key = (account_id, two_fa_status, role)
        if key in self._authorization_tg_responses:
            return self._authorization_tg_responses[key]

        return model.JWTTokens(
            access_token=f"tg_access_token_{account_id}",
            refresh_token=f"tg_refresh_token_{account_id}"
        )

    async def check_authorization(self, access_token: str) -> model.AuthorizationData:
        self._call_history.append({
            "method": "check_authorization",
            "access_token": access_token
        })

        if access_token in self._check_authorization_responses:
            return self._check_authorization_responses[access_token]

        # Дефолтный ответ
        return model.AuthorizationData(
            account_id=1,
            two_fa_status=False,
            role="employee",
            message="OK",
            status_code=200
        )

    def set_authorization_response(
        self,
        account_id: int,
        two_fa_status: bool,
        role: str,
        response: model.JWTTokens
    ) -> None:
        key = (account_id, two_fa_status, role)
        self._authorization_responses[key] = response

    def set_authorization_tg_response(
        self,
        account_id: int,
        two_fa_status: bool,
        role: str,
        response: model.JWTTokens
    ) -> None:
        key = (account_id, two_fa_status, role)
        self._authorization_tg_responses[key] = response

    def set_check_authorization_response(
        self,
        access_token: str,
        response: model.AuthorizationData
    ) -> None:
        self._check_authorization_responses[access_token] = response

    def get_call_history(self) -> list:
        return self._call_history

    def clear_call_history(self) -> None:
        self._call_history = []
