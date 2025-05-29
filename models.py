from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    transaction_date = Column(String)
    posting_date = Column(String)
    billing_amount = Column(Float)
    merchant = Column(String)
    merchant_city = Column(String)
    merchant_county = Column(String)
    merchant_postal_code = Column(String)
    reference_number = Column(String)
    debit_credit_flag = Column(String)
    sicmcc_code = Column(String)
