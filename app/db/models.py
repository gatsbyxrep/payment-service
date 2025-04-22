from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

# Define the named ENUM type
user_role_enum = Enum('user', 'admin', name='user_role', create_type=True)

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(user_role_enum, default="user")
    is_active = Column(Boolean, default=True)

class AccountDB(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    balance = Column(Numeric(10, 2), default=0.0)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)

class PaymentDB(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(36), unique=True, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())