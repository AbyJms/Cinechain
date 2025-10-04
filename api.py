from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

def init_db():
    conn = sqlite3.connect('cinechain.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id TEXT NOT NULL,
        theater_id TEXT NOT NULL,
        tickets_sold INTEGER,
        gross_revenue REAL
    )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/sales', methods=['POST'])
def add_sale():
    data = request.json
    conn = sqlite3.connect('cinechain.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sales (movie_id, theater_id, tickets_sold, gross_revenue) VALUES (?, ?, ?, ?)",
        (data['movie_id'], data['theater_id'], data['tickets_sold'], data['gross_revenue'])
    )
    conn.commit()
    conn.close()
    
    socketio.emit('dashboard_update', {'message': 'New sales data arrived!'})
    
    return jsonify({"status": "success"}), 200

@app.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data():
    conn = sqlite3.connect('cinechain.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(gross_revenue) FROM sales")
    total_revenue = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(tickets_sold) FROM sales")
    total_attendance = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT theater_id, SUM(gross_revenue) FROM sales GROUP BY theater_id")
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

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, use_reloader=False)