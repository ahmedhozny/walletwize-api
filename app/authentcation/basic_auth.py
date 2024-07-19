#!/usr/bin/env python3
"""
Authentication service module
"""
from datetime import datetime, timedelta
from typing import Union
from uuid import uuid4

from sqlalchemy.exc import NoResultFound

from app.exceptions import UserAlreadyExists, UserPasswordExpired, UserCredentialsMismatch, UserTokenInvalid, \
    AppException, UserTokenExpired
from app.models import AccountDetails
from app.schemas import AccountCreate, AccountCredentials
from app.storage import Storage
import bcrypt
import jwt


def _hash_password(password: str) -> bytes:
    """Hashes password.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def _generate_uuid() -> str:
    """Generates a UUID.
    """
    return str(uuid4())


class BasicAuthentication:
    def __init__(self, storage: Storage):
        """Initializes the Auth class.
        """
        self.__storage = storage
        self.__secret = "ff0d69562f59c8063554d63e190411ac7a78c1322c6cf5e864a6b7b0d9f756b7"
        self.__algorithm = "HS256"

    def register_user(self, schema: AccountCreate) -> AccountDetails:
        """Adds a new user to the database.
        """
        try:
            self.__storage.user_storage().find_user_by_email(schema.email)
            raise UserAlreadyExists(schema.email)
        except NoResultFound:
            return self.__storage.user_storage().add_user(schema, _hash_password(schema.password).decode('utf-8'))

    def validate_user(self, schema: AccountCredentials) -> AccountDetails:
        """Validates the login credentials.
        """
        try:
            user = self.__storage.user_storage().find_user_by_email(schema.email)
            cred = self.__storage.user_storage().get_user_credentials(user.id)
            if cred.expired:
                raise UserPasswordExpired(email=schema.email)
            res = bcrypt.checkpw(
                schema.password.encode('utf-8'), cred.password_hashed.encode('utf-8')
            )
            if res is False:
                raise UserCredentialsMismatch(email=schema.email)
            return user
        except NoResultFound:
            raise UserCredentialsMismatch(email=schema.email)

    def create_access_token(self, user: AccountDetails, iat: datetime, expires_delta: timedelta = None) -> str:
        to_encode = {"sub": user.email, "iat": iat}
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
            to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.__secret, self.__algorithm)
        return encoded_jwt

    def verify_access_token(self, authorization: str) -> dict:
        if authorization is None:
            raise None
        token_split = authorization.split()
        if token_split[0] != "Bearer":
            raise UserTokenInvalid
        token = token_split[1]
        try:
            payload = jwt.decode(token, self.__secret, algorithms=[self.__algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise UserTokenInvalid
            token_db = self.__storage.user_storage().get_token(token)
            if token_db.expired:
                raise UserTokenExpired
            self.__storage.user_storage().find_user_by_email(email)
            return {"email": email}
        except (jwt.exceptions.DecodeError, NoResultFound):
            raise UserTokenInvalid

    def revoke_token(self, authorization: str):
        token = authorization.split()[1]
        try:
            return self.__storage.user_storage().revoke_token(token)
        except NoResultFound:
            raise UserTokenInvalid
