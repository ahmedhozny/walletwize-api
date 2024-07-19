from sqlalchemy import Column, Integer, DateTime, DECIMAL, String

from app.models.backup_models import BaseModel


class SourcesTable(BaseModel):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String, nullable=False)
    type = Column(String, nullable=False)
    balance = Column(DECIMAL, nullable=False)
