# PROGRAM FOR BOOKMYSHOW PVR CINEMA PAGE ONLY
# Loops through top 3 movies, counts green seats, skips unclickable ones.

from playwright.sync_api import sync_playwright
import time
import cv2
import numpy as np

URL = "https://in.bookmyshow.com/cinemas/kochi/vanitha-cineplex-rgb-laser-4k-3d-atmos-edappally/buytickets/VMHE/20251005"

def analyze_seats(image_path):
    """Analyzes green seats in the screenshot."""
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # --- Define green color range ---
    lower_green = np.array([35, 0, 0])
    upper_green = np.array([90, 250, 250])

    mask = cv2.inRange(hsv, lower_green, upper_green)
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    gc = len(contours)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)

    cv2.imshow("Detected Green Boxes", img)
    cv2.waitKey(1500)
    cv2.destroyAllWindows()

    tc = 300
    ac = int(gc + (gc/2))
    wc = tc - ac
    return wc


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL)
    page.wait_for_selector("div.sc-1skzbbo-0.eBWTPs")

    showtimes = page.locator("div.sc-1skzbbo-0.eBWTPs")
    total_buttons = showtimes.count()
    print(f"Found {total_buttons} showtime buttons")

    for i in range(min(total_buttons, 3)):
        print(f"\nAttempting showtime #{i + 1}")

        try:
            showtime = showtimes.nth(i)
            showtime.scroll_into_view_if_needed()
            showtime.click()

            # Handle popup (if it appears)
            popup = page.locator("div.sc-ttkokf-2.sc-ttkokf-3.cwjwdu.hIYQmz").first
            try:
                popup.wait_for(state="visible", timeout=5000)
                with page.expect_navigation(wait_until="load"):
                    popup.click()
            except:
                print("No popup appeared")

            # Click 'Select Seats'
            page.wait_for_selector("div.sc-zgl7vj-7.kdBUB", timeout=10000)
            select_btn = page.locator("div.sc-zgl7vj-7.kdBUB")
            select_btn.click()

            time.sleep(3)

            # Take cropped screenshot
            img_path = f"seatmap_{i+1}.png"
            page.screenshot(path=img_path, clip={"x": 300, "y": 180, "width": 800, "height": 1200})

            # Analyze green seats
            green_count = analyze_seats(img_path)
            print(f"Showtime #{i + 1} green seats: {green_count}")

            # Go back for next movie
            page.go_back()
            page.wait_for_selector("div.sc-1skzbbo-0.eBWTPs")
            print("Returned to main page")

        except Exception as e:
            print(f"Skipping showtime #{i + 1} due to error: {e}")
            page.go_back()
            page.wait_for_selector("div.sc-1skzbbo-0.eBWTPs")

    browser.close()