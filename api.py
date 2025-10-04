from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import random
from apscheduler.schedulers.background import BackgroundScheduler
from playwright.sync_api import sync_playwright

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('cinechain.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id TEXT NOT NULL,
        theater_id TEXT NOT NULL,
        total_seats INTEGER,
        booked_seats INTEGER,
        gross_revenue REAL
    )
    ''')
    conn.commit()
    conn.close()

init_db()

def scrape_bms_seat_data():
    URL = "https://in.bookmyshow.com/buytickets/kalki-2898-ad-kochi/movie-koch-ET00352941-MT/20251004"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(URL, timeout=90000)
            
            try:
                page.locator("#btn-accept").click(timeout=10000)
            except Exception:
                print("T&C pop-up not found or already accepted.")

            page.wait_for_selector("#seat-layout", timeout=20000)
            
            booked_seats_elements = page.locator("a._sold")
            booked_seats = booked_seats_elements.count()
            
            available_seats_elements = page.locator("a._available")
            available_seats = available_seats_elements.count()
            
            total_seats = booked_seats + available_seats
            
            avg_ticket_price = 350
            revenue = booked_seats * avg_ticket_price
            
            scraped_data = {
                "movie_id": "Kalki 2898 AD",
                "theater_id": "PVR Lulu, Kochi",
                "total_seats": total_seats,
                "booked_seats": booked_seats,
                "gross_revenue": revenue
            }
            
            print(f"SCRAPE SUCCESS: {scraped_data}")
            browser.close()
            return scraped_data

        except Exception as e:
            print(f"SCRAPER FAILED: {e}")
            browser.close()
            return None

def record_show_data():
    data = scrape_bms_seat_data()
    
    if data is None:
        print("Skipping database entry due to scrape failure.")
        return
        
    conn = sqlite3.connect('cinechain.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO shows (movie_id, theater_id, total_seats, booked_seats, gross_revenue) VALUES (?, ?, ?, ?, ?)",
        (data['movie_id'], data['theater_id'], data['total_seats'], data['booked_seats'], data['gross_revenue'])
    )
    conn.commit()
    conn.close()

@app.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data():
    conn = sqlite3.connect('cinechain.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(gross_revenue) FROM shows")
    total_revenue = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(booked_seats) FROM shows")
    total_attendance = cursor.fetchone()[0] or 0
    cursor.execute("SELECT theater_id, SUM(gross_revenue) FROM shows GROUP BY theater_id")
    revenue_by_theater = cursor.fetchall()
    conn.close()
    chart_data = {
        "labels": [row[0] for row in revenue_by_theater],
        "data": [row[1] for row in revenue_by_theater]
    }
    return jsonify({
        "totalRevenue": f"${total_revenue:,.0f}",
        "totalAttendance": f"{total_attendance:,}",
        "chartData": chart_data
    })

scheduler = BackgroundScheduler()
scheduler.add_job(func=record_show_data, trigger="interval", seconds=300)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)