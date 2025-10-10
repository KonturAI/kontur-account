from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse

from internal import interface
from internal.controller.http.handler.account.model import (
    ChangePasswordBody,
    DeleteTwoFaBody,
    LoginBody,
    RecoveryPasswordBody,
    RegisterBody,
    SetTwoFaBody,
    VerifyTwoFaBody,
)
from pkg.log_wrapper import auto_log
from pkg.trace_wrapper import traced_method


class AccountController(interface.IAccountController):
    def __init__(
        self,
        tel: interface.ITelemetry,
        account_service: interface.IAccountService,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.account_service = account_service

    @auto_log()
    @traced_method()
    async def register(self, body: RegisterBody) -> JSONResponse:
        authorization_data = await self.account_service.register(login=body.login, password=body.password)

        response = JSONResponse(status_code=201, content={"account_id": authorization_data.account_id})

        response.set_cookie(
            key="Access-Token", value=authorization_data.access_token, httponly=True, secure=True, samesite="lax"
        )
        response.set_cookie(
            key="Refresh-Token",
            value=authorization_data.refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )

        return response

    @auto_log()
    @traced_method()
    async def register_from_tg(self, body: RegisterBody) -> JSONResponse:
        authorization_data = await self.account_service.register_from_tg(login=body.login, password=body.password)

        response = JSONResponse(status_code=201, content={"account_id": authorization_data.account_id})

        response.set_cookie(
            key="Access-Token", value=authorization_data.access_token, httponly=True, secure=True, samesite="lax"
        )
        response.set_cookie(
            key="Refresh-Token", value=authorization_data.refresh_token, httponly=True, secure=True, samesite="lax"
        )

        return response

    @auto_log()
    @traced_method()
    async def login(self, body: LoginBody) -> JSONResponse:
        authorization_data = await self.account_service.login(login=body.login, password=body.password)

        response = JSONResponse(status_code=200, content={"account_id": authorization_data.account_id})

        response.set_cookie(
            key="Access-Token", value=authorization_data.access_token, httponly=True, secure=True, samesite="lax"
        )
        response.set_cookie(
            key="Refresh-Token", value=authorization_data.refresh_token, httponly=True, secure=True, samesite="lax"
        )

        return response

    @auto_log()
    @traced_method()
    async def generate_two_fa(self, request: Request):
        authorization_data = request.state.authorization_data
        account_id = authorization_data.account_id

        if account_id == 0:
            return JSONResponse(status_code=403, content={})
        two_fa_key, qr_image = await self.account_service.generate_two_fa_key(account_id)

        def iterfile():
            try:
                while True:
                    chunk = qr_image.read(8192)
                    if not chunk:
                        break
                    yield chunk
            finally:
                qr_image.close()

        response = StreamingResponse(
            iterfile(),
            media_type="image/png",
            headers={"X-TwoFA-Key": two_fa_key, "Content-Disposition": "inline; filename=qr_code.png"},
        )

        return response

    @auto_log()
    @traced_method()
    async def set_two_fa(self, request: Request, body: SetTwoFaBody) -> JSONResponse:
        authorization_data = request.state.authorization_data
        account_id = authorization_data.account_id

        if account_id == 0:
            return JSONResponse(status_code=403, content={})

        await self.account_service.set_two_fa_key(
            account_id=account_id, google_two_fa_key=body.google_two_fa_key, google_two_fa_code=body.google_two_fa_code
        )
        return JSONResponse(status_code=200, content={})

    @auto_log()
    @traced_method()
    async def delete_two_fa(self, request: Request, body: DeleteTwoFaBody) -> JSONResponse:
        authorization_data = request.state.authorization_data
        account_id = authorization_data.account_id

        if account_id == 0:
            return JSONResponse(status_code=403, content={})

        await self.account_service.delete_two_fa_key(account_id=account_id, google_two_fa_code=body.google_two_fa_code)

        return JSONResponse(status_code=200, content={})

    @auto_log()
    @traced_method()
    async def verify_two_fa(self, request: Request, body: VerifyTwoFaBody) -> JSONResponse:
        authorization_data = request.state.authorization_data
        account_id = authorization_data.account_id

        if account_id == 0:
            return JSONResponse(status_code=403, content={})

        is_valid = await self.account_service.verify_two(
            account_id=account_id, google_two_fa_code=body.google_two_fa_code
        )

        return JSONResponse(status_code=200, content={"is_valid": is_valid})

    @auto_log()
    @traced_method()
    async def recovery_password(self, request: Request, body: RecoveryPasswordBody) -> JSONResponse:
        authorization_data = request.state.authorization_data
        account_id = authorization_data.account_id

        if account_id == 0:
            return JSONResponse(status_code=403, content={})

        await self.account_service.recovery_password(account_id=account_id, new_password=body.new_password)

        return JSONResponse(status_code=200, content={})

    @auto_log()
    @traced_method()
    async def change_password(self, request: Request, body: ChangePasswordBody) -> JSONResponse:
        authorization_data = request.state.authorization_data
        account_id = authorization_data.account_id

        if account_id == 0:
            return JSONResponse(status_code=403, content={})

        await self.account_service.change_password(
            account_id=account_id, new_password=body.new_password, old_password=body.old_password
        )

        return JSONResponse(status_code=200, content={})
