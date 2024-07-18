from app.storage.database_engine import DBStorage
from app.storage.user_storage import UserStorage


class Storage:
    def __init__(self):
        self.__db = DBStorage()
        self.__user_storage = UserStorage(self.__db)

    def user_storage(self) -> UserStorage:
        return self.__user_storage
