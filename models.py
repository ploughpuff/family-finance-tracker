from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    transaction_date = Column(String)
    billing_amount = Column(Float)
    merchant_full = Column(String)
