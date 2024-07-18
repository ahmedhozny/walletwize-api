from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class AccountCredentials(BaseModel):
    email: EmailStr
    password: str


class AccountCreate(AccountCredentials):
    first_name: str
    middle_name: str
    last_name: str
    phone: PhoneNumber


class TokenRevoke(BaseModel):
    access_token: str


class TokenCreate(TokenRevoke):
    token_type: str
