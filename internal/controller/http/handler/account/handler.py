from opentelemetry.trace import Status, StatusCode, SpanKind
from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse

from internal import interface
from internal.controller.http.handler.account.model import (
    RegisterBody, LoginBody, SetTwoFaBody, DeleteTwoFaBody,
    VerifyTwoFaBody, RecoveryPasswordBody, ChangePasswordBody
)


class AccountController(interface.IAccountController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            account_service: interface.IAccountService,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.account_service = account_service

    async def register(self, body: RegisterBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "AccountController.register",
                kind=SpanKind.INTERNAL,
                attributes={"login": body.login}
        ) as span:
            try:
                self.logger.info("регистрация")

                authorization_data = await self.account_service.register(
                    login=body.login,
                    password=body.password
                )

                self.logger.info("регистрация успешна")

                span.set_status(StatusCode.OK)
                response = JSONResponse(
                    status_code=201,
                    content={"account_id": authorization_data.account_id}
                )

                response.set_cookie(
                    key="Access-Token",
                    value=authorization_data.access_token,
                    httponly=True,
                    secure=True,
                    samesite="lax"
                )
                response.set_cookie(
                    key="Refresh-Token",
                    value=authorization_data.refresh_token,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                )

                return response

            except Exception as err:
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def register_from_tg(self, body: RegisterBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "AccountController.register_from_tg",
                kind=SpanKind.INTERNAL,
                attributes={"login": body.login}
        ) as span:
            try:
                self.logger.info("регистрация из тг")

                authorization_data = await self.account_service.register_from_tg(
                    login=body.login,
                    password=body.password
                )

                self.logger.info("регистрация из тг успешна")

                span.set_status(StatusCode.OK)
                response = JSONResponse(
                    status_code=201,
                    content={"account_id": authorization_data.account_id}
                )

                response.set_cookie(
                    key="Access-Token",
                    value=authorization_data.access_token,
                    httponly=True,
                    secure=True,
                    samesite="lax"
                )
                response.set_cookie(
                    key="Refresh-Token",
                    value=authorization_data.refresh_token,
                    httponly=True,
                    secure=True,
                    samesite="lax"
                )

                return response

            except Exception as err:
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def login(self, body: LoginBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "AccountController.login",
                kind=SpanKind.INTERNAL,
                attributes={"login": body.login}
        ) as span:
            try:
                self.logger.info("вход")

                authorization_data = await self.account_service.login(
                    login=body.login,
                    password=body.password
                )

                self.logger.info("вход успешен")

                span.set_status(StatusCode.OK)
                response = JSONResponse(
                    status_code=200,
                    content={"account_id": authorization_data.account_id}
                )

                response.set_cookie(
                    key="Access-Token",
                    value=authorization_data.access_token,
                    httponly=True,
                    secure=True,
                    samesite="lax"
                )
                response.set_cookie(
                    key="Refresh-Token",
                    value=authorization_data.refresh_token,
                    httponly=True,
                    secure=True,
                    samesite="lax"
                )

                return response

            except Exception as err:
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def generate_two_fa(self, request: Request) -> JSONResponse | StreamingResponse:
        with self.tracer.start_as_current_span(
                "AccountController.generate_two_fa",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                authorization_data = request.state.authorization_data
                account_id = authorization_data.account_id

                if account_id == 0:
                    return JSONResponse(
                        status_code=403,
                        content={}
                    )

                self.logger.info("генерация 2fa")

                two_fa_key, qr_image = await self.account_service.generate_two_fa_key(account_id)

                self.logger.info("генерация 2fa успешна")

                def iterfile():
                    try:
                        while True:
                            chunk = qr_image.read(8192)
                            if not chunk:
                                break
                            yield chunk
                    finally:
                        qr_image.close()

                span.set_status(StatusCode.OK)
                response = StreamingResponse(
                    iterfile(),
                    media_type="image/png",
                    headers={
                        "X-TwoFA-Key": two_fa_key,
                        "Content-Disposition": "inline; filename=qr_code.png"
                    }
                )

                return response

            except Exception as err:
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def set_two_fa(self, request: Request, body: SetTwoFaBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "AccountController.set_two_fa",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                authorization_data = request.state.authorization_data
                account_id = authorization_data.account_id

                if account_id == 0:
                    return JSONResponse(
                        status_code=403,
                        content={}
                    )

                self.logger.info("установка 2fa")

                await self.account_service.set_two_fa_key(
                    account_id=account_id,
                    google_two_fa_key=body.google_two_fa_key,
                    google_two_fa_code=body.google_two_fa_code
                )

                self.logger.info("установка 2fa успешна")

                span.set_status(StatusCode.OK)
                return JSONResponse(status_code=200, content={})

            except Exception as err:
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def delete_two_fa(self, request: Request, body: DeleteTwoFaBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "AccountController.delete_two_fa",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                authorization_data = request.state.authorization_data
                account_id = authorization_data.account_id

                if account_id == 0:
                    return JSONResponse(
                        status_code=403,
                        content={}
                    )

                self.logger.info("удаление 2fa")

                await self.account_service.delete_two_fa_key(
                    account_id=account_id,
                    google_two_fa_code=body.google_two_fa_code
                )

                self.logger.info("удаление 2fa успешно")

                span.set_status(StatusCode.OK)
                return JSONResponse(status_code=200, content={})

            except Exception as err:
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def verify_two_fa(self, request: Request, body: VerifyTwoFaBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "AccountController.verify_two_fa",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                authorization_data = request.state.authorization_data
                account_id = authorization_data.account_id

                if account_id == 0:
                    return JSONResponse(
                        status_code=403,
                        content={}
                    )

                self.logger.info("проверка 2fa")

                is_valid = await self.account_service.verify_two(
                    account_id=account_id,
                    google_two_fa_code=body.google_two_fa_code
                )

                self.logger.info("проверка 2fa успешна")

                span.set_status(StatusCode.OK)
                return JSONResponse(
                    status_code=200,
                    content={"is_valid": is_valid}
                )

            except Exception as err:
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def recovery_password(self, request: Request, body: RecoveryPasswordBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "AccountController.recovery_password",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                authorization_data = request.state.authorization_data
                account_id = authorization_data.account_id

                if account_id == 0:
                    return JSONResponse(
                        status_code=403,
                        content={}
                    )

                self.logger.info("восстановление пароля")

                await self.account_service.recovery_password(
                    account_id=account_id,
                    new_password=body.new_password
                )

                self.logger.info("восстановление пароля успешно")

                span.set_status(StatusCode.OK)
                return JSONResponse(status_code=200, content={})

            except Exception as err:
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def change_password(self, request: Request, body: ChangePasswordBody) -> JSONResponse:
        with self.tracer.start_as_current_span(
                "AccountController.change_password",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                authorization_data = request.state.authorization_data
                account_id = authorization_data.account_id

                if account_id == 0:
                    return JSONResponse(
                        status_code=403,
                        content={}
                    )

                self.logger.info("смена пароля")

                await self.account_service.change_password(
                    account_id=account_id,
                    new_password=body.new_password,
                    old_password=body.old_password
                )

                self.logger.info("смена пароля успешна")

                span.set_status(StatusCode.OK)
                return JSONResponse(status_code=200, content={})

            except Exception as err:
                span.set_status(StatusCode.ERROR, str(err))
                raise err