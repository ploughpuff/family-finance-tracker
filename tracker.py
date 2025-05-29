import csv
import chardet
from io import TextIOWrapper
from models import Transaction
from sqlalchemy.orm import Session


class Tracker:
    def __init__(self, db_session: Session):
        self.session = db_session

    def process_csv_file(self, file_storage):
        # Read a sample to detect encoding
        raw_data = file_storage.read()
        detected = chardet.detect(raw_data)
        encoding = detected["encoding"] or "utf-8"

        # Rewind and decode with detected encoding
        file_storage.seek(0)
        file_stream = TextIOWrapper(file_storage, encoding=encoding)
        reader = csv.DictReader(file_stream)

        for row in reader:
            amount = row["Billing Amount"].replace("£", "").strip()
            transaction = Transaction(
                transaction_date=row["Transaction Date"],
                posting_date=row["Posting Date"],
                billing_amount=float(amount),
                merchant=row["Merchant"],
                merchant_city=row["Merchant City"],
                merchant_county=row["Merchant County"],
                merchant_postal_code=row["Merchant Postal Code"],
                reference_number=row["Reference Number"],
                debit_credit_flag=row["Debit/Credit Flag"],
                sicmcc_code=row["SICMCC Code"],
            )
            self.session.add(transaction)

        self.session.commit()
