from sqlalchemy import Column, Integer, String, DateTime

from app.models.backup_models import BaseModel


class ClientTableExample(BaseModel):
    __tablename__ = 'client_table'
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_name = Column(String(255), nullable=False)
    last_modified = Column(DateTime, nullable=False)
