from sqlalchemy import Column, Integer, DateTime, DECIMAL, String

from app.models.backup_models import BaseModel


class TransactionsTable(BaseModel):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(DECIMAL, nullable=False)
    type = Column(String, nullable=False)
    source = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    activity = Column(String, nullable=False)
