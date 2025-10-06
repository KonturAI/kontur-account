from contextvars import ContextVar

from internal import model
from internal import interface
from pkg.client.client import AsyncHTTPClient
from pkg.trace_wrapper import traced_method


class LoomAuthorizationClient(interface.ILoomAuthorizationClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            host: str,
            port: int,
            log_context: ContextVar[dict],
    ):
        logger = tel.logger()
        self.client = AsyncHTTPClient(
            host,
            port,
            prefix="/api/authorization",
            use_tracing=True,
            logger=logger,
            log_context=log_context
        )
        self.tracer = tel.tracer()

    @traced_method()
    async def authorization(
            self,
            account_id: int,
            two_fa_status: bool,
            role: str
    ) -> model.JWTTokens:
        body = {
            "account_id": account_id,
            "two_fa_status": two_fa_status,
            "role": role
        }
        response = await self.client.post("", json=body)
        json_response = response.json()

        return model.JWTTokens(**json_response)

    @traced_method()
    async def authorization_tg(
            self,
            account_id: int,
            two_fa_status: bool,
            role: str
    ) -> model.JWTTokens:
        body = {
            "account_id": account_id,
            "two_fa_status": two_fa_status,
            "role": role
        }
        response = await self.client.post("/tg", json=body)
        json_response = response.json()

        return model.JWTTokens(**json_response)

    @traced_method()
    async def check_authorization(self, access_token: str) -> model.AuthorizationData:
        cookies = {"Access-Token": access_token}
        response = await self.client.get("/check", cookies=cookies)
        json_response = response.json()

        return model.AuthorizationData(**json_response)
