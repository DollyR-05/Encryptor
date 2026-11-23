"""Encryptor: a small Flask text converter for classical ciphers.

Run:  pip install -r requirements.txt  &&  python app.py   ->  http://127.0.0.1:5000
"""
from flask import Flask, jsonify, render_template, request

import encryption

app = Flask(__name__)
MAX_LEN = 5000


@app.errorhandler(ValueError)
def bad_request(err):
    return jsonify(error=str(err)), 400


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/convert")
def convert():
    d = request.get_json(force=True)
    mode, text, key = d.get("mode"), d.get("text") or "", d.get("key") or ""
    if mode not in encryption.MODES:
        raise ValueError("Unknown cipher")
    if len(text) > MAX_LEN:
        raise ValueError(f"Text is too long (limit {MAX_LEN} characters)")
    table = encryption.key_table(mode, key)
    if not text.strip():
        return jsonify(output="", table=table)
    output = encryption.convert(mode, text, key, decrypt=d.get("action") == "decrypt")
    return jsonify(output=output, table=table)


if __name__ == "__main__":
    app.run(debug=False)