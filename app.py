from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Transaction
from tracker import Tracker

app = Flask(__name__)

# Setup DB
engine = create_engine("sqlite:///database.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if uploaded_file:
            session = Session()
            tracker = Tracker(session)
            tracker.process_csv_file(uploaded_file.stream)
            return "CSV data saved to database."

        return "No file uploaded."

    return render_template("add.html")


@app.route("/transactions")
def transactions():
    session = Session()
    all_transactions = session.query(Transaction).all()
    return render_template("transactions.html", transactions=all_transactions)


if __name__ == "__main__":
    app.run(debug=True)
