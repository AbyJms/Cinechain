# PROGRAM FOR BOOKMYSHOW MULTI-THEATRE SEAT ANALYSIS
# Loops through multiple theatre URLs, detects green seats, saves to CSV

from playwright.sync_api import sync_playwright
import time
import cv2
import numpy as np
import csv
import os

# --- List of theatre URLs ---
URLS = [
    "https://in.bookmyshow.com/cinemas/kochi/vanitha-cineplex-rgb-laser-4k-3d-atmos-edappally/buytickets/VMHE/20251005",
    "https://in.bookmyshow.com/cinemas/kochi/four-star-movies-manjapra-angamaly/buytickets/FSMA/20251005",
    "https://in.bookmyshow.com/cinemas/kochi/pvr-forum-mall-kochi/buytickets/PVMF/20251005"
]

# --- Output CSV file ---
CSV_FILE = "theatre_seat_data.csv"

# Initialize CSV with headers if it doesn’t exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Theatre", "Movie Name", "Green Seat Count"])


def analyze_seats(image_path):
    """Analyzes green seats in the screenshot and returns count."""
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # --- Define green color range (tuned for seats) ---
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([90, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    green_count = len(contours)

    print(f"🟢 Detected {green_count} green seats")

    # (Optional) Draw bounding boxes
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

    cv2.imshow("Detected Green Boxes", img)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()

    return green_count


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    for theatre_url in URLS:
        print(f"\n🎭 Visiting: {theatre_url}")
        page.goto(theatre_url)

        # --- Extract theatre name from URL ---
        theatre_name = theatre_url.split("/cinemas/kochi/")[1].split("/buytickets")[0].replace("-", " ").title()

        # --- Wait for movies to load ---
        page.wait_for_selector("div.sc-1skzbbo-0.eBWTPs")

        # --- Try to get the first movie name ---
        try:
            movie_name = page.locator(".__movie-name, .sc-1fakbrq-0").first.inner_text()
        except:
            movie_name = "Unknown Movie"

        print(f"🎬 Theatre: {theatre_name}")
        print(f"📽️ Movie: {movie_name}")

        # --- Try clicking the first showtime ---
        try:
            showtime = page.locator("div.sc-1skzbbo-0.eBWTPs").first
            showtime.scroll_into_view_if_needed()
            showtime.click()
            print("✅ Clicked first showtime")

            # --- Handle optional popup ---
            popup = page.locator("div.sc-ttkokf-2.sc-ttkokf-3.cwjwdu.hIYQmz").first
            try:
                popup.wait_for(state="visible", timeout=5000)
                with page.expect_navigation(wait_until="load"):
                    popup.click()
                print("🟢 Clicked 'Continue' popup")
            except:
                print("No popup appeared")

            # --- Click Select Seats ---
            page.wait_for_selector("div.sc-zgl7vj-7.kdBUB", timeout=10000)
            select_btn = page.locator("div.sc-zgl7vj-7.kdBUB")
            select_btn.click()
            print("🎟️ Clicked Select Seats")

            # --- Wait for seats to load ---
            time.sleep(3)

            # --- Screenshot seat map ---
            img_path = f"{theatre_name.replace(' ', '_')}_seatmap.png"
            page.screenshot(path=img_path, clip={"x": 300, "y": 180, "width": 800, "height": 1200})
            print(f"📸 Screenshot saved: {img_path}")

            # --- Analyze seats using CV2 ---
            green_count = analyze_seats(img_path)

            # --- Write result to CSV ---
            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([theatre_name, movie_name, green_count])

            print(f"✅ Data saved for {theatre_name}")

            # --- Go back for next theatre ---
            page.go_back()

        except Exception as e:
            print(f"❌ Error with {theatre_name}: {e}")
            continue

    browser.close()

print(f"\n✅ All data collected and saved to {CSV_FILE}")
