from sqlalchemy import Column, Integer, DateTime, DECIMAL

from app.models.backup_models import BaseModel


class TransactionsTable(BaseModel):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(DECIMAL, nullable=False)
    type = Column(DECIMAL, nullable=False)
    source = Column(DECIMAL, nullable=False)
    date = Column(DateTime, nullable=False)
    time = Column(DateTime, nullable=False)
    activity = Column(DECIMAL, nullable=False)
