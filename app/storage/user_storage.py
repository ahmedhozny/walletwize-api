import uuid

from sqlalchemy.exc import NoResultFound, IntegrityError

from app.exceptions import AppException
from app.models import AccountDetails
from app.models.account_bearer import AccountBearer
from app.models.account_security import AccountSecurity
from app.schemas import AccountCreate
from app.storage import DBStorage


class UserStorage:
    def __init__(self, db_engine: DBStorage):
        self.db_engine = db_engine

    def find_user_by_email(self, email: str) -> AccountDetails | None:
        users = self.db_engine.search_for(AccountDetails, {AccountDetails.email: email})
        if len(users) == 0:
            raise NoResultFound
        return users[0]

    def add_user(self, schema: AccountCreate, hashed_password: str) -> AccountDetails:
        new_user = AccountDetails(
            email=schema.email,
            account_uuid=uuid.uuid4().bytes,
        )

        try:
            self.db_engine.new(new_user, True)
            user_cred = AccountSecurity(
                account_id=new_user.id,
                password_hashed=hashed_password
            )

            self.db_engine.new(user_cred, True)
        except IntegrityError as e:
            self.db_engine.get_session().rollback()
            raise AppException(e)
        return new_user

    def get_user_credentials(self, account_id: int) -> AccountSecurity:
        users = self.db_engine.search_for(AccountSecurity, {AccountSecurity.account_id: account_id})
        if len(users) == 0:
            raise NoResultFound
        return users[0]

    def add_token(self, account: AccountDetails, token: str) -> AccountBearer:
        bearer = AccountBearer(
            account_id=account.id,
            access_token=token,
        )
        try:
            self.db_engine.new(bearer)
        except IntegrityError as e:
            self.db_engine.get_session().rollback()
            raise AppException(e)

    def get_token(self, access_token: str) -> AccountBearer:
        token_objs = self.db_engine.search_for(AccountBearer, {
            AccountBearer.access_token: access_token
        })
        if len(token_objs) == 0:
            raise NoResultFound
        return token_objs[0]

    def revoke_token(self, access_token: str) -> bool:
        token = self.get_token(access_token)
        if token.expired:
            return False
        token.expired = True
        self.db_engine.update(token)
        return True
