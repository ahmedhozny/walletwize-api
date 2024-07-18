from sqlalchemy import Column, Integer, DateTime, DECIMAL

from app.models.backup_models import BaseModel


class SourcesTable(BaseModel):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(DECIMAL, nullable=False)
    type = Column(DECIMAL, nullable=False)
    balance = Column(DECIMAL, nullable=False)
