from pydantic import BaseModel


class RegisterBody(BaseModel):
    login: str
    password: str


class LoginBody(BaseModel):
    login: str
    password: str


class SetTwoFaBody(BaseModel):
    google_two_fa_key: str
    google_two_fa_code: str


class DeleteTwoFaBody(BaseModel):
    google_two_fa_code: str


class VerifyTwoFaBody(BaseModel):
    google_two_fa_code: str


class RecoveryPasswordBody(BaseModel):
    new_password: str


class ChangePasswordBody(BaseModel):
    old_password: str
    new_password: str
