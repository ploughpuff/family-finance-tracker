import csv
import json
import re
import hashlib
import logging
from datetime import datetime
from decimal import Decimal
from io import TextIOWrapper
from typing import Any, Dict

import chardet
from sqlalchemy.orm import Session

from models import Transaction


class Tracker:
    def __init__(self, db_session: Session):
        self.session = db_session
        self.logger = logging.getLogger(__name__)

        with open("account_mappings.json", "r", encoding="utf-8") as f:
            self.accounts = json.load(f)

    def get_accounts(self):
        return self.accounts

    def parse_transaction(self, row: Dict[str, str], mapping: Dict):
        try:
            # Parse date
            date_col = mapping["date"]["column"]
            date_fmt = mapping["date"]["strptime_format"]
            date_str = row.get(date_col)
            if not date_str:
                raise ValueError(f"Missing date column '{date_col}' in CSV row")
            date = datetime.strptime(date_str, date_fmt).date()

            # Parse amount
            amount_col = mapping["amount"]["column"]
            amount_raw = row.get(amount_col, "")
            regex = mapping["amount"].get("regex", "-?\\d+(\\.\\d+)?")
            inverse = mapping["amount"].get("inverse", False)

            match = re.search(regex, amount_raw)
            if not match:
                raise ValueError(
                    f"Amount regex '{regex}' did not match value '{amount_raw}'"
                )
            amount = float(match.group())
            if inverse:
                amount = -amount

            # Parse merchant (may be multiple columns joined)
            merchant_cols = mapping["merchant"]["column"]
            if isinstance(merchant_cols, str):
                merchant_cols = [merchant_cols]
            delimiter = mapping["merchant"].get("join_delimiter", " ")
            merchant = delimiter.join(
                row.get(col, "").strip() for col in merchant_cols
            ).strip()

            return {
                "date": date,
                "amount": amount,
                "merchant": merchant,
            }, None

        except ValueError as e:
            return None, str(e)

    def generate_transaction_hash(self, trans_data: dict, unique_col: str):

        parts = []
        parts.append(unique_col)
        parts.append(str(trans_data["date"]))
        parts.append(str(trans_data["amount"]))

        unique_string = "|".join(parts)
        return hashlib.md5(unique_string.encode("utf-8")).hexdigest()

    def process_csv_file(self, file_storage, account_name):
        try:
            # Detect encoding
            raw_data = file_storage.read()
            encoding = chardet.detect(raw_data)["encoding"] or "utf-8"
            file_storage.seek(0)
            file_stream = TextIOWrapper(file_storage, encoding=encoding)
            reader = csv.DictReader(file_stream)

            if account_name not in self.accounts:
                raise ValueError(f"Account {account_name} not found")

            mappings = self.accounts[account_name]["mappings"]

            with self.session.begin():  # transaction scope
                for csv_row in reader:
                    transaction_data, error = self.parse_transaction(csv_row, mappings)

                    if error:
                        # Raise to trigger rollback
                        raise ValueError(f"Error parsing row: {error}")

                    csv_row.get(mappings["unique_column"])

                    trans_hash = self.generate_transaction_hash(
                        transaction_data, csv_row.get(mappings["unique_column"])
                    )

                    existing = (
                        self.session.query(Transaction)
                        .filter_by(trans_hash=trans_hash)
                        .first()
                    )

                    if existing:
                        self.logger.info(
                            f"Duplicate transaction detected for account '{account_name}': {trans_hash} - skipping."
                        )
                        continue

                    else:
                        transaction = Transaction(
                            date=transaction_data["date"],
                            amount=transaction_data["amount"],
                            merchant=transaction_data["merchant"],
                            account_name=account_name,
                            trans_hash=trans_hash,
                        )
                        self.session.add(transaction)

            # If we get here, commit was successful
            return None  # no error
        except Exception as e:
            # The transaction will rollback automatically on exception
            return str(e)
