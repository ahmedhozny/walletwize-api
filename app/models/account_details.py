from datetime import datetime

from sqlalchemy import Column, Integer, String, BINARY, DateTime

from app.models import BaseModel


class AccountDetails(BaseModel):
    __tablename__ = 'account_details'

    _id = Column(Integer, name="id", primary_key=True, autoincrement=True)
    full_name = Column(String(50), nullable=False)

    email = Column(String(320), nullable=False, unique=True)
    account_uuid = Column(BINARY(16), nullable=False)

    registered_on = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    account_status = Column(String(50), nullable=False, default="Verified")
