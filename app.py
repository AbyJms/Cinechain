from flask import Flask, jsonify, send_from_directory, make_response
import csv
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

# Path to your CSV file
CSV_FILE = "bms_seatdata.csv"

# --- Serve main HTML page ---
@app.route('/')
def index():
    return send_from_directory('templates', 'cinechain.html')

# --- API route to send aggregated dashboard data ---
@app.route('/api/dashboard-data')
def get_dashboard_data():
    """Read CSV and return summarized data"""
    total_movies = set()
    total_attendance = 0
    total_revenue = 0

    # If file doesn't exist, return zeros
    if not os.path.exists(CSV_FILE):
        return jsonify({
            "movies_distributing": 0,
            "total_attendance": 0,
            "total_revenue": 0
        })

    # Read CSV and calculate totals
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie = row.get("Movie Name", "").strip()
            seats = row.get("Green Seats", "0").strip()
            revenue = row.get("Revenue", "0").strip()

            if movie:
                total_movies+=1

            try:
                total_attendance += int(seats)
                total_revenue += int(revenue)
            except ValueError:
                continue

    # Prevent browser caching (for live refresh)
    response = make_response(jsonify({
        "movies_distributing": total_movies,
        "total_attendance": total_attendance,
        "total_revenue": total_revenue
    }))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response


# --- Serve static files (JS, CSS) ---
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


# --- Run Flask server ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
