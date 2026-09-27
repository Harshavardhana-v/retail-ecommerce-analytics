from flask import Flask, jsonify
from flask_cors import CORS

from pathlib import Path
import json


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

# Allow frontend to access API
CORS(app)


# ============================================================
# FILE PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "top20_realtime.json"
)


# ============================================================
# HOME ROUTE
# ============================================================

@app.route("/")
def home():

    return jsonify({
        "message": "Retail E-Commerce Analytics API",
        "status": "running"
    })


# ============================================================
# TOP PRODUCTS API
# ============================================================

@app.route("/api/top-products")
def top_products():

    # Check whether data file exists

    if not DATA_FILE.exists():

        return jsonify({
            "error": "Real-time data not available yet"
        }), 404


    # Read JSON file

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return jsonify(data)


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("RETAIL E-COMMERCE ANALYTICS API")
    print("=" * 60)

    print(f"\nReading data from:")
    print(DATA_FILE)

    print("\nStarting Flask server...")
    print("API: http://localhost:5000")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )