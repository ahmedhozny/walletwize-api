from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class AccountCredentials(BaseModel):
    email: EmailStr
    password: str


class AccountCreate(AccountCredentials):
    pass


class TokenRevoke(BaseModel):
    access_token: str


class TokenCreate(TokenRevoke):
    token_type: str
