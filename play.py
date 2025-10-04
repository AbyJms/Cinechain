# PROGRAM: BookMyShow Multi-Tab Seat & Revenue Analyzer
# Opens a new tab per showtime to scrape movie info, green seats, ticket cost, and revenue.

from playwright.sync_api import sync_playwright, TimeoutError
import time
import random
import cv2
import numpy as np
import csv
import os

# List of theatre URLs
URLS = [
    "https://in.bookmyshow.com/cinemas/kochi/vanitha-cineplex-rgb-laser-4k-3d-atmos-edappally/buytickets/VMHE/20251005",
    "https://in.bookmyshow.com/cinemas/kochi/four-star-movies-manjapra-angamaly/buytickets/FSMA/20251005",
    "https://in.bookmyshow.com/cinemas/kochi/pvr-forum-mall-kochi/buytickets/PVMF/20251005"
]

CSV_FILE = "bms_seatdata.csv"

# Initialize CSV if it doesn't exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Theatre", "Movie Name", "Green Seats", "Ticket Price", "Revenue"])


def analyze_seats(image_path):
    """Detect green seats in screenshot and return count."""
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_green = np.array([35, 0, 0])
    upper_green = np.array([90, 250, 250])

    mask = cv2.inRange(hsv, lower_green, upper_green)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    green_count = len(contours)

    ac = int(green_count + (green_count / 2))
    wc = 300 - ac
    return ac


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    
    for theatre_url in URLS:
        print(f"\n🎭 Visiting: {theatre_url}")
        theatre_name = theatre_url.split("/cinemas/kochi/")[1].split("/buytickets")[0].replace("-", " ").title()

        page = browser.new_page()
        page.goto(theatre_url)
        page.wait_for_selector("div.sc-1skzbbo-0.eBWTPs")

        # Get showtime buttons
        showtimes = page.locator("div.sc-1skzbbo-0.eBWTPs")
        total_buttons = showtimes.count()
        print(f"Found {total_buttons} showtime buttons")

        for i in range(min(total_buttons, 3)):  # top 3 showtimes
            print(f"\nProcessing showtime #{i + 1}")
            try:
                # Open a fresh tab per showtime
                tab = browser.new_page()
                tab.goto(theatre_url)
                tab.wait_for_selector("div.sc-1skzbbo-0.eBWTPs")
                
                showtime_btn = tab.locator("div.sc-1skzbbo-0.eBWTPs").nth(i)
                showtime_btn.scroll_into_view_if_needed()
                showtime_btn.click()
                time.sleep(random.uniform(1.5, 3.0))  # random delay

                # Handle optional popup
                popup = tab.locator("div.sc-ttkokf-2.sc-ttkokf-3.cwjwdu.hIYQmz").first
                try:
                    popup.wait_for(state="visible", timeout=5000)
                    with tab.expect_navigation(wait_until="load"):
                        popup.click()
                    print("🟢 Clicked popup")
                except TimeoutError:
                    print("No popup appeared")

                # Click 'Select Seats'
                tab.wait_for_selector("div.sc-zgl7vj-7.kdBUB", timeout=10000)
                tab.locator("div.sc-zgl7vj-7.kdBUB").click()
                time.sleep(2)

                # Take screenshot
                img_path = f"{theatre_name.replace(' ', '_')}_showtime_{i+1}.png"
                tab.screenshot(path=img_path, clip={"x": 300, "y": 180, "width": 800, "height": 1200})
                time.sleep(3)
                
                # Analyze green seats
                green_count = analyze_seats(img_path)

                # Extract movie name
                try:
                    movie_name = tab.locator(".__movie-name, .sc-1fakbrq-0").first.inner_text()
                except:
                    movie_name = "Unknown Movie"

                # Extract ticket price
                try:
                    ticket_price_text = tab.locator("div.sc-hKFxyN-1, .__ticket-price").first.inner_text()
                    ticket_price = int(''.join(filter(str.isdigit, ticket_price_text)))
                except:
                    ticket_price = 200  # fallback

                revenue = green_count * ticket_price

                print(f"Showtime_{i+1}: Movie='{movie_name}', Seats={green_count}, Ticket={ticket_price}, Revenue={revenue}")

                # Append to CSV
                with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([theatre_name, movie_name, green_count, ticket_price, revenue])

                tab.close()
                time.sleep(random.uniform(3, 6))  # avoid bot detection

            except Exception as e:
                print(f"❌ Error processing showtime #{i+1}: {e}")
                tab.close()
                continue

        page.close()

    browser.close()
    print(f"\n✅ Data collection complete. Saved to {CSV_FILE}")
