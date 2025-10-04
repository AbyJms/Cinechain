import requests
import random
import time
import json

API_ENDPOINT = "http://127.0.0.1:5000/api/sales"

MOVIES = ["Jawan", "LEO", "Salaar", "Kalki 2898-AD"]
THEATERS = ["PVR_Angamaly", "Shenoys_Kochi", "INOX_Thrissur", "Carnival_Thalayolaparambu"]

print("Starting live box office data feed...")

while True:
    try:
        sale_data = {
            "movie_id": random.choice(MOVIES),
            "theater_id": random.choice(THEATERS),
            "tickets_sold": random.randint(1, 8),
            "gross_revenue": random.randint(150, 1200)
        }
        
        response = requests.post(API_ENDPOINT, json=sale_data)
        
        if response.status_code == 200:
            print(f"SUCCESS: Sent data -> {sale_data}")
        else:
            print(f"ERROR: Failed to send data. Status: {response.status_code}")
            
        time.sleep(random.uniform(1, 4))
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Connection failed. Is the Flask server running?")
        time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopping data feeder.")
        break