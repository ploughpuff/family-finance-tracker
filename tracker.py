import csv
import chardet
from io import TextIOWrapper
from models import Transaction
from sqlalchemy.orm import Session


class Tracker:
    def __init__(self, db_session: Session):
        self.session = db_session

    def process_csv_file(self, file_storage):
        raw_data = file_storage.read()
        encoding = chardet.detect(raw_data)["encoding"] or "utf-8"
        file_storage.seek(0)
        file_stream = TextIOWrapper(file_storage, encoding=encoding)
        reader = csv.DictReader(file_stream)

        for row in reader:
            amount = row["Billing Amount"].replace("£", "").strip()
            merchant_full = f"{row['Merchant']}, {row['Merchant City']}".strip(", ")
            transaction = Transaction(
                transaction_date=row["Transaction Date"],
                billing_amount=float(amount),
                merchant_full=merchant_full,
            )
            self.session.add(transaction)

        self.session.commit()
