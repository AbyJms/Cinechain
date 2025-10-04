# PROGRAM FOR BOOKMYSHOW PVR CINEMA PAGE ONLY

from playwright.sync_api import sync_playwright
import time

# Replace with your PVR cinema page URL
URL = "https://in.bookmyshow.com/cinemas/kochi/vanitha-cineplex-rgb-laser-4k-3d-atmos-edappally/buytickets/VMHE/20251005"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # visible browser
    page = browser.new_page()
    page.goto(URL)

    # --- Wait for the showtime list to load ---
    page.wait_for_selector("div.sc-1skzbbo-0.eBWTPs")  # the time button class

    # --- Click the first showtime button ---
    first_showtime = page.locator("div.sc-1skzbbo-0.eBWTPs").first
    first_showtime.click()
    print("Clicked first showtime")

    # --- Handle optional 'Show has already started' popup ---
    popup = page.locator("div.sc-ttkokf-2.sc-ttkokf-3.cwjwdu.hIYQmz").first

    try:
        popup.wait_for(state="visible", timeout=5000)  # wait up to 5s for popup
        # click and wait for seat map to load
        with page.expect_navigation(wait_until="load"):
            popup.click()
        print("Clicked 'Continue' popup")
    except:
        print("No 'Show has already started' popup appeared")


    
    # --- Wait for 'Select Seats' button to appear ---
    bleh = page.locator("div.sc-zgl7vj-7.kdBUB")
    bleh.click()
    print("Clicked Select Seats")

    time.sleep(5)  # extra wait for rendering

    # --- Take screenshot of seat map ---
    
    page.screenshot(
    path="seatmap.png",
    clip={"x": 300, "y": 180, "width": 800, "height": 1200}
    )
    print("Screenshot saved: seatmap.png")

import cv2
import numpy as np

# --- Load the screenshot ---
img = cv2.imread("seatmap.png")

# --- Convert to HSV for color detection ---
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# --- Define green color range (tweak if needed) ---
# Typical green HSV range
lower_green = np.array([35, 0, 0])
upper_green = np.array([90, 255, 255])

# --- Threshold the green areas ---
mask = cv2.inRange(hsv, lower_green, upper_green)

# --- Optional: Morphology to clean up noise ---
kernel = np.ones((3,3), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

# --- Find contours (each green box/seat) ---
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# --- Count green boxes ---
green_count = len(contours)
print(f"Green / available seats detected: {green_count}")

# --- Optional: visualize detection ---
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)  # red rectangle around each green box

cv2.imshow("Detected Green Boxes", img)
cv2.waitKey(0)
cv2.destroyAllWindows()


browser.close()