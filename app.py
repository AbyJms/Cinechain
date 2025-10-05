from flask import Flask, send_from_directory, jsonify
import csv
import os

app = Flask(__name__, static_url_path='', static_folder='.')

CSV_FILE = "bms_seatdata.csv"

@app.route('/')
def index():
    return send_from_directory('.', 'cinechain.html')

@app.route('/cinechain.css')
def css():
    return send_from_directory('.', 'cinechain.css')

@app.route('/cinechain.js')
def js():
    return send_from_directory('.', 'cinechain.js')

@app.route('/bms_seatdata.csv')
def get_csv():
    return send_from_directory('.', CSV_FILE)

@app.route('/api/dashboard-data')
def get_dashboard_data():
    total_movies = set()
    total_attendance = 0
    total_revenue = 0

    if not os.path.exists(CSV_FILE):
        return jsonify({
            "movies_distributing": 0,
            "total_attendance": 0,
            "total_revenue": 0
        })

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_movies.add(row["Movie Name"])
            total_attendance += int(row["Green Seats"])
            total_revenue += int(row["Revenue"])

    return jsonify({
        "movies_distributing": len(total_movies),
        "total_attendance": total_attendance,
        "total_revenue": total_revenue
    })

@app.route('/api/movies-data')
def get_movies_data():
    if not os.path.exists(CSV_FILE):
        return jsonify([])

    combined = {}
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["Theatre"], row["Movie Name"])
            seats = int(row["Green Seats"])
            revenue = int(row["Revenue"])
            price = int(row["Ticket Price"])

            if key in combined:
                combined[key]["seats"] += seats
                combined[key]["revenue"] += revenue
            else:
                combined[key] = {
                    "theatre": row["Theatre"],
                    "movie": row["Movie Name"],
                    "seats": seats,
                    "price": price,
                    "revenue": revenue
                }

    return jsonify(list(combined.values()))

if __name__ == '__main__':
    app.run(debug=True)
