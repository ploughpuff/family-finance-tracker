import csv
import io
import itertools
from datetime import datetime
from decimal import Decimal

import logging
import chardet
from flask import Flask, flash, redirect, render_template, request, session, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, joinedload, sessionmaker

from models import Base, Transaction
from tracker import Tracker

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)


app = Flask(__name__)
app.secret_key = "this-is-my-secret-key-for-dev"

engine = create_engine("sqlite:///app.db", echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
tracker = Tracker(Session())


@app.route("/")
@app.route("/transactions")
def show_transactions():
    with Session() as session:
        transactions = (
            session.query(Transaction).options(joinedload(Transaction.category)).all()
        )
        return render_template("transactions.html", transactions=transactions)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    with Session() as session:
        if request.method == "POST":
            file = request.files.get("file")
            account_name = request.form.get("account_name")

            if not file:
                flash("Missing file")
                return redirect(url_for("upload"))

            error = tracker.process_csv_file(file, account_name)

            if error:
                flash(
                    f"Failed to process CSV file for account '{account_name}'. {error}",
                    "warning",
                )
                return redirect(url_for("upload"))

            flash(f"Uploaded file for {account_name}")
            return redirect(url_for("upload"))

        return render_template("upload.html", accounts=tracker.get_accounts())


@app.route("/settings")
def settings():
    return render_template("settings.html", active_tab=None)


if __name__ == "__main__":
    app.run(debug=True)
