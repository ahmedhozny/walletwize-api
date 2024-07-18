from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, BINARY, DateTime
from sqlalchemy.orm import relationship

from app.models import BaseModel


class AccountDetails(BaseModel):
    __tablename__ = 'account_details'

    _id = Column(Integer, name="id", primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)

    email = Column(String(320), nullable=False, unique=True)
    phone = Column(String(32), nullable=False, unique=True)
    account_uuid = Column(BINARY(16), nullable=False)

    registered_on = Column(DateTime, nullable=False, default=lambda: datetime.utcnow())
    account_status = Column(String(50), nullable=False, default="Verified")
