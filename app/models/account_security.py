from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import Relationship

from app.models import BaseModel, AccountDetails


class AccountSecurity(BaseModel):
    __tablename__ = 'account_security'

    _id = Column(Integer, name="id", primary_key=True, autoincrement=True)

    account_id = Column(Integer, ForeignKey(AccountDetails._id), nullable=False, unique=True)

    # OAuth (For Basic Authentication)
    password_hashed = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.utcnow())
    expired = Column(Boolean, default=False)

    account = Relationship(AccountDetails, foreign_keys=[account_id])
