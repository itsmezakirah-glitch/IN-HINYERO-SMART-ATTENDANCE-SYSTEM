from flask import Flask, render_template, send_file
import qrcode
import secrets
from datetime import date
import json
import os


app = Flask(__name__)


qr_database = "qr_database.json"


def save_database(data):
    with open(qr_database, "w") as file:
        json.dump(data, file)


@app.route("/")
def home():
    return render_template("generator.html")


@app.route("/generate")
def generate():

    token = secrets.token_urlsafe(12)
    db_file = qr_database 

    if os.path.exists(db_file):
        with open(db_file, "r") as file:
            data = json.load(file)
    else:
        data = {}

    data[token] = str(date.today())
    save_database(data)
    qr_data = f"http://127.0.0.1:5001/scan/{token}"

    img = qrcode.make(qr_data)
    filename = f"{token}.png"
    img.save(filename)

    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)