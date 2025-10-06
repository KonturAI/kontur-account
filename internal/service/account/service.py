import bcrypt
import pyotp
import qrcode
import io

from internal import interface, model, common

from pkg.trace_wrapper import traced_method


class AccountService(interface.IAccountService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            account_repo: interface.IAccountRepo,
            loom_authorization_client: interface.ILoomAuthorizationClient,
            password_secret_key: str
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.account_repo = account_repo
        self.loom_authorization_client = loom_authorization_client
        self.password_secret_key = password_secret_key

    @traced_method()
    async def register(self, login: str, password: str) -> model.AuthorizationDataDTO:
        hashed_password = self.__hash_password(password)
        account_id = await self.account_repo.create_account(login, hashed_password)

        jwt_token = await self.loom_authorization_client.authorization(
            account_id,
            False,
            "employee"
        )

        return model.AuthorizationDataDTO(
            account_id=account_id,
            access_token=jwt_token.access_token,
            refresh_token=jwt_token.refresh_token,
        )

    @traced_method()
    async def register_from_tg(self, login: str, password: str) -> model.AuthorizationDataDTO:
        hashed_password = self.__hash_password(password)
        account_id = await self.account_repo.create_account(login, hashed_password)

        jwt_token = await self.loom_authorization_client.authorization_tg(
            account_id,
            False,
            "employee"
        )

        return model.AuthorizationDataDTO(
            account_id=account_id,
            access_token=jwt_token.access_token,
            refresh_token=jwt_token.refresh_token,
        )

    @traced_method()
    async def login(self, login: str, password: str) -> model.AuthorizationDataDTO | None:
        account = await self.account_repo.account_by_login(login)
        if not account:
            self.logger.info("Аккаунт не найден")
            raise common.ErrAccountNotFound()
        account = account[0]

        if not self.__verify_password(account.password, password):
            self.logger.info("Неверный пароль")
            raise common.ErrInvalidPassword()

        jwt_token = await self.loom_authorization_client.authorization(
            account.id,
            True if account.google_two_fa_key else False,
            "employee"
        )

        return model.AuthorizationDataDTO(
            account_id=account.id,
            access_token=jwt_token.access_token,
            refresh_token=jwt_token.refresh_token,
        )

    @traced_method()
    async def generate_two_fa_key(self, account_id: int) -> tuple[str, io.BytesIO]:
        two_fa_key = pyotp.random_base32()
        totp_auth = pyotp.totp.TOTP(two_fa_key).provisioning_uri(
            name=f"account_id-{account_id}",
            issuer_name="crmessenger"
        )

        qr_image = io.BytesIO()
        qrcode.make(totp_auth).save(qr_image)
        qr_image.seek(0)

        return two_fa_key, qr_image

    @traced_method()
    async def set_two_fa_key(self, account_id: int, google_two_fa_key: str, google_two_fa_code: str) -> None:
        account = (await self.account_repo.account_by_id(account_id))[0]

        if account.google_two_fa_key:
            self.logger.info("2FA уже включена")
            raise common.ErrTwoFaAlreadyEnabled()

        is_two_fa_verified = self.__verify_two_fa(google_two_fa_code, google_two_fa_key)
        if not is_two_fa_verified:
            self.logger.info("Неверный код 2FA")
            raise common.ErrTwoFaCodeInvalid()

        await self.account_repo.set_two_fa_key(account_id, google_two_fa_key)

    @traced_method()
    async def delete_two_fa_key(self, account_id: int, google_two_fa_code: str) -> None:
        account = (await self.account_repo.account_by_id(account_id))[0]
        if not account.google_two_fa_key:
            self.logger.info("2FA не включена")
            raise common.ErrTwoFaNotEnabled()

        is_two_fa_verified = self.__verify_two_fa(google_two_fa_code, account.google_two_fa_key)
        if not is_two_fa_verified:
            self.logger.info("Неверный код 2FA")
            raise common.ErrTwoFaCodeInvalid()

        await self.account_repo.delete_two_fa_key(account_id)

    @traced_method()
    async def verify_two(self, account_id: int, google_two_fa_code: str) -> bool:
        account = (await self.account_repo.account_by_id(account_id))[0]
        if not account.google_two_fa_key:
            self.logger.info("2FA не включена")
            raise common.ErrTwoFaNotEnabled()

        is_two_fa_verified = self.__verify_two_fa(google_two_fa_code, account.google_two_fa_key)
        return is_two_fa_verified

    @traced_method()
    async def recovery_password(self, account_id: int, new_password: str) -> None:
        new_hashed_password = self.__hash_password(new_password)
        await self.account_repo.update_password(account_id, new_hashed_password)

    @traced_method()
    async def change_password(self, account_id: int, new_password: str, old_password: str) -> None:
        account = (await self.account_repo.account_by_id(account_id))[0]

        if not self.__verify_password(account.password, old_password):
            self.logger.info("Неверный старый пароль")
            raise common.ErrInvalidPassword()

        new_hashed_password = self.__hash_password(new_password)
        await self.account_repo.update_password(account_id, new_hashed_password)

    def __verify_password(self, hashed_password: str, password: str) -> bool:
        peppered_password = self.password_secret_key + password
        return bcrypt.checkpw(peppered_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def __verify_two_fa(self, two_fa_code: str, two_fa_key: str) -> bool:
        totp = pyotp.TOTP(two_fa_key)
        return totp.verify(two_fa_code)

    def __hash_password(self, password: str) -> str:
        peppered_password = self.password_secret_key + password
        hashed_password = bcrypt.hashpw(peppered_password.encode('utf-8'), bcrypt.gensalt())

        return hashed_password.decode('utf-8')
