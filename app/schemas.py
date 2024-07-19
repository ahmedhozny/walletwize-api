from pydantic import BaseModel, EmailStr


class AccountCredentials(BaseModel):
    email: EmailStr
    password: str


class AccountCreate(AccountCredentials):
    pass


class TokenRevoke(BaseModel):
    token: str


class TokenCreate(TokenRevoke):
    token_type: str
