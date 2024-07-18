from datetime import datetime
import os
import uuid

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker, Session

from app.models.backup_models import BaseModel, ChangeLog


class Backup:
    dir_path = 'data_storage/'
    os.makedirs(os.path.dirname(dir_path), exist_ok=True)

    def __init__(self, account_uuid: bytes):
        self.account_uuid = account_uuid
        database_path = f'{self.dir_path}/{uuid.UUID(bytes=account_uuid)}.db'
        print(os.path.abspath(database_path))
        self.__engine = create_engine(f"sqlite:///{database_path}")
        BaseModel.metadata.create_all(self.__engine)
        # session_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        # Session = scoped_session(session_factory)
        # self.__session = Session()

        SessionLocal = sessionmaker(bind=self.__engine)
        self.session = SessionLocal()

    def __call__(self, *args, **kwargs) -> Session:
        return self.session

    def sync_database(self, data: dict) -> None:
        log_id = data['log_id']
        table_name = data['table_name']
        operation = data["operation"]
        row_data = data["data"]
        last_mod = datetime.fromisoformat(data["timestamp"])

        table_sync = Table(table_name, MetaData(), autoload_with=self.__engine)

        # Convert date columns to datetime.date if present
        for column, value in row_data.items():
            if isinstance(value, str):
                try:
                    row_data[column] = datetime.fromisoformat(value).date()
                except ValueError:
                    continue  # Not a date string, continue

        if operation == 'I':
            insert_statement = table_sync.insert().values(**row_data)
            self.session.execute(insert_statement)
        elif operation == 'U':
            record_id = row_data.get('id')
            if not record_id:
                raise ValueError("Missing 'id' for update operation")
            update_statement = table_sync.update().where(table_sync.c.id == record_id).values(**row_data)
            self.session.execute(update_statement)
        elif operation == 'D':
            record_id = row_data.get('id')
            if not record_id:
                raise ValueError("Missing 'id' for delete operation")
            delete_statement = table_sync.delete().where(table_sync.c.id == record_id)
            self.session.execute(delete_statement)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

        log = ChangeLog(
            id=log_id,
            table_name=table_name,
            row_id=row_data["id"],
            operation=operation,
            change_time=last_mod,
            sync_time=datetime.utcnow()
        )
        self.session.add(log)

        self.session.commit()

    def load_data(self, offset_id: int) -> dict:
        # Query change_log for entries with ID greater than offset_id
        change_log = Table('change_log', MetaData(), autoload_with=self.__engine)
        query = change_log.select().where(change_log.c.id == offset_id + 1).order_by(change_log.c.id)
        result: ChangeLog | None = self.session.execute(query).fetchone()

        if not result:
            raise NoResultFound()

        payload = {
            "log_id": result.id,
            "table_name": result.table_name,
            "operation": result.operation,
            "row_id": result.row_id,
            "change_time": result.change_time.isoformat(),
            "sync_time": result.sync_time.isoformat()
        }

        table_name = result.table_name
        row_id = result.row_id

        # Fetch the actual data from the specified table based on row_id
        table = Table(table_name, MetaData(), autoload_with=self.__engine)
        record_query = table.select().where(table.c.id == row_id)
        record_result = self.session.execute(record_query).fetchone()

        if not record_result:
            raise ValueError("Change log is corrupted.")

        print(record_result)
        record_data = {key: value for key, value in record_result._mapping.items()}

        # Convert datetime fields to ISO format strings
        for key, value in record_data.items():
            if isinstance(value, datetime):
                record_data[key] = value.isoformat()

        payload["data"] = record_data

        return payload
