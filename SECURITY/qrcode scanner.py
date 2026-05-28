from flask import Flask, render_template
import json
from datetime import date


app = Flask(__name__)


qr_database = "qr_database.json"


def load_database():
    try:
        with open(qr_database, "r") as file:
            return json.load(file)
    except:
        return {}


@app.route("/")
def scanner():
    return render_template("scanner.html")


@app.route("/scan/<token>")
def validate(token):

    qr_database = load_database()

    if token not in qr_database:
        return "<h1>Invalid QR Code</h1>"

    token_date = qr_database[token]

    if token_date != str(date.today()):
        return "<h1>QR Code Expired</h1>"

    return "<h1>Attendance Accepted</h1>"


if __name__ == "__main__":
    app.run(debug=True)
