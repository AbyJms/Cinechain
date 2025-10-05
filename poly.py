import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError
import cv2
import numpy as np
import csv
import os

# --- Configuration ---
URLS = [
    "https://in.bookmyshow.com/cinemas/kochi/vanitha-cineplex-rgb-laser-4k-3d-atmos-edappally/buytickets/VMHE/20251005",
    "https://in.bookmyshow.com/cinemas/kochi/four-star-movies-manjapra-angamaly/buytickets/FSMA/20251005",
    "https://in.bookmyshow.com/cinemas/kochi/pvr-forum-mall-kochi/buytickets/PVMF/20251005"
]

CSV_FILE = "bms_seatdata.csv"
INTERVAL_HOURS = 3  # Run every 3 hours

# --- Initialize CSV ---
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Theatre", "Movie Name", "Green Seats", "Ticket Price", "Revenue"])

# --- Green seat detection ---
def analyze_seats(image_path, show_preview=False):
    """Detect green seats in screenshot."""
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

    if show_preview:
        vis = img.copy()
        cv2.drawContours(vis, contours, -1, (0, 255, 0), 2)
        cv2.imshow("Detected Green Seats", vis)
        cv2.imshow("Mask", mask)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()

    return 300 - int(green_count + (green_count / 2))

# --- Main scraping function ---
def run_scraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        for theatre_url in URLS:
            theatre_name = theatre_url.split("/cinemas/kochi/")[1].split("/buytickets")[0].replace("-", " ").title()
            print(f"\nProcessing: {theatre_name}")


            i = 0
            price = [250, 135, 210]
            page = browser.new_page()
            page.goto(theatre_url)
            page.wait_for_selector("div.sc-1skzbbo-0.eBWTPs")

            # --- Check for unavailable showtime message ---
            try:
                if page.locator("div.sc-1412vr2-0.knoRMk").is_visible():
                    print("Showtime unavailable or sold out — closing page.")
                    page.close()
                    continue
            except:
                pass

            # --- Click first showtime ---
            try:
                first_showtime_btn = page.locator("div.sc-1skzbbo-0.eBWTPs").first
                first_showtime_btn.scroll_into_view_if_needed()
                first_showtime_btn.click()
                time.sleep(2)
            except Exception as e:
                print(f"Couldn't click showtime: {e}")
                page.close()
                continue

            # --- Handle popup ---
            try:
                popup = page.locator("div.sc-ttkokf-2.sc-ttkokf-3.cwjwdu.hIYQmz").first
                popup.wait_for(state="visible", timeout=5000)
                with page.expect_navigation(wait_until="load"):
                    popup.click()
            except TimeoutError:
                pass
            except:
                pass

            # --- Click 'Select Seats' ---
            try:
                page.wait_for_selector("div.sc-zgl7vj-7.kdBUB", timeout=10000)
                page.locator("div.sc-zgl7vj-7.kdBUB").click()
                time.sleep(3)
            except:
                print("Couldn't reach seat page")
                page.close()
                continue

            # --- Extract movie name ---
            try:
                movie_name = page.locator("h1").first.inner_text()
                if not movie_name or len(movie_name.strip()) < 2:
                    raise ValueError("Invalid movie name")
            except:
                try:
                    movie_name = page.locator("div.sc-1412vr2-2.gwQhog").first.inner_text()
                except:
                    movie_name = "Unknown Movie"

            # --- Screenshot seat layout ---
            img_path = f"{theatre_name.replace(' ', '_')}_seats.png"
            page.screenshot(path=img_path, clip={"x": 300, "y": 180, "width": 800, "height": 1200})
            green_count = analyze_seats(img_path)

            # --- Extract ticket price ---
            try:
                price_text = page.locator("div.sc-1atac75-6.dnVSWP").first.inner_text()
                ticket_price = int(''.join(filter(str.isdigit, price_text)))
            except:
                ticket_price = price[i]
                i += 1

            revenue = green_count * ticket_price

            # --- Save data ---
            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    theatre_name,
                    movie_name,
                    green_count,
                    ticket_price,
                    revenue
                ])

            print(f"{movie_name} | {green_count} seats | ₹{ticket_price} | ₹{revenue}")
            page.close()

        browser.close()

# --- Infinite Loop (every 3 hours) ---
while True:
    print(f"\n=== Scraping started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    try:
        run_scraper()
    except Exception as e:
        print(f"Error during scraping: {e}")
    print(f"Sleeping for {INTERVAL_HOURS} hours...\n")
    time.sleep(INTERVAL_HOURS * 3600)