# full_file: multi_tab_playwright_seat_scraper.py
# Run: python multi_tab_playwright_seat_scraper.py
#
# Requirements:
#   pip install playwright opencv-python numpy
#   python -m playwright install

from playwright.sync_api import sync_playwright
import time
import random
import csv
import os
import cv2
import numpy as np
from typing import List

# ---------- Configuration ----------
URLS: List[str] = [
    "https://in.bookmyshow.com/cinemas/kochi/vanitha-cineplex-rgb-laser-4k-3d-atmos-edappally/buytickets/VMHE/20251005",
    "https://in.bookmyshow.com/cinemas/kochi/four-star-movies-manjapra-angamaly/buytickets/FSMA/20251005",
    "https://in.bookmyshow.com/cinemas/kochi/pvr-forum-mall-kochi/buytickets/PVMF/20251005",
]

CSV_FILE = "multi_theatre_seat_data.csv"
VIEWPORT = {"width": 1280, "height": 900}
# clip region for seatmap screenshot (tweak to match your layout)
SEATMAP_CLIP = {"x": 300, "y": 180, "width": 800, "height": 1200}

# green detection (HSV)
LOWER_GREEN = np.array([35, 40, 40])
UPPER_GREEN = np.array([90, 255, 255])

# ---------- Helpers ----------

def human_sleep(min_s=0.8, max_s=2.0):
    """Sleep a short random time to mimic human pauses."""
    time.sleep(random.uniform(min_s, max_s))

def human_scroll(page, steps=6, step_pixels=600, delay_between=0.8):
    """Scroll the page slowly to trigger lazy-load."""
    for _ in range(steps):
        page.mouse.wheel(0, step_pixels)
        time.sleep(delay_between + random.uniform(0, 0.7))

def random_mouse_move(page, times=3):
    """Move mouse around the viewport randomly to mimic user movement."""
    for _ in range(times):
        x = random.randint(100, VIEWPORT["width"] - 100)
        y = random.randint(100, VIEWPORT["height"] - 100)
        page.mouse.move(x, y, steps=random.randint(5, 20))
        time.sleep(random.uniform(0.15, 0.5))

def analyze_green_seats(image_path: str) -> int:
    """OpenCV: count green blobs (seats) in the image."""
    img = cv2.imread(image_path)
    if img is None:
        print("⚠️ analyze_green_seats: image not found:", image_path)
        return 0
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_GREEN, UPPER_GREEN)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Filter by reasonable box size to reduce noise (adjust if needed)
    filtered = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # keep small-to-medium boxes (tweak min/max as needed)
        if 6 <= w <= 80 and 6 <= h <= 80:
            filtered.append(cnt)
    green_count = len(filtered)
    print(f"    🟢 Green seats detected (filtered): {green_count}")
    ac = int(green_count + (green_count / 2))
    wc = 300 - ac
    return ac

def ensure_csv_header(csv_file: str):
    if not os.path.exists(csv_file):
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Theatre", "Movie", "GreenSeats", "Screenshot"])

# ---------- Full flow ----------

def process_one_theatre(context, theatre_url: str, idx: int):
    """Open a new tab, navigate to theatre_url, and extract seat data."""
    page = context.new_page()
    page.set_viewport_size(VIEWPORT)
    # Set a common user agent (optional, to look more real)
    page.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
    human_sleep(0.5, 1.0)

    # simulate typing the URL into an address-like experience:
    # We cannot type into browser address bar directly; so we'll load via goto,
    # but add a short 'thinking' delay to mimic a human typing/pasting and pressing Enter.
    print(f"\n[{idx+1}] Opening new tab and navigating (human-like)...")
    human_sleep(0.6, 1.4)
    # Navigate
    page.goto("about:blank")
    human_sleep(0.2, 0.6)
    # simulate 'typing' delay before loading - helps throttle too-fast navigation
    for ch in theatre_url[:30]:
        # a tiny pause pretending to type the first characters (visual only)
        time.sleep(0.01)
    human_sleep(0.2, 0.5)
    page.goto(theatre_url, wait_until="networkidle")
    human_sleep(1.0, 2.0)

    # Slow human-like interactions to reduce detection
    random_mouse_move(page, times=2)
    human_scroll(page, steps=5, step_pixels=600, delay_between=0.6)
    human_sleep(0.5, 1.2)

    # Try to read movie name from page (robust fallback selectors)
    movie_name = "Unknown Movie"
    try:
        # prefer visible movie title elements
        if page.locator("h1").count():
            movie_name = page.locator("h1").first.inner_text().strip()
        elif page.locator("h2").count():
            movie_name = page.locator("h2").first.inner_text().strip()
        elif page.locator(".sc-1fakbrq-0").count():
            movie_name = page.locator(".sc-1fakbrq-0").first.inner_text().strip()
        elif page.locator(".__movie-name").count():
            movie_name = page.locator(".__movie-name").first.inner_text().strip()
    except Exception:
        movie_name = "Unknown Movie"

    print(f"    Theatre page loaded. Movie: {movie_name}")

    # Attempt to find showtime buttons (try several robust selectors)
    # We'll try a set of known selectors and a fallback wildcard class search
    showtime_selectors = [
        "div.sc-1skzbbo-0.eBWTPs",
        "div[class*='skzbbo']",
        "div[class*='showtime']",
        "button:has-text('Book')",
        "button:has-text('BOOK')",
    ]
    show_btn = None
    for sel in showtime_selectors:
        try:
            if page.locator(sel).count() > 0:
                # pick the first visible/clickable
                for i in range(page.locator(sel).count()):
                    candidate = page.locator(sel).nth(i)
                    try:
                        candidate.scroll_into_view_if_needed()
                        if candidate.is_visible() and candidate.is_enabled():
                            show_btn = candidate
                            break
                    except Exception:
                        continue
            if show_btn:
                print(f"    Found showtime selector: {sel}")
                break
        except Exception:
            continue

    if not show_btn:
        print("    ⚠️ No showtime button found for this theatre — closing tab.")
        page.close()
        return None

    # Click showtime (with retries)
    clicked = False
    for attempt in range(4):
        try:
            show_btn.click()
            clicked = True
            print("    ✅ Clicked showtime")
            break
        except Exception as e:
            print("    ⚠️ Click failed, retrying...", attempt, e)
            human_sleep(0.8, 1.8)
            # try to re-find the button in case DOM changed
            try:
                show_btn.scroll_into_view_if_needed()
            except:
                pass

    if not clicked:
        print("    ❌ Could not click showtime — closing tab.")
        page.close()
        return None

    human_sleep(0.8, 1.6)

    # Handle optional popup dialog (generic)
    try:
        # try common dialog selectors by text/role first
        dlg = page.locator("div[role='dialog'] >> text=Continue").first
        dlg.wait_for(state="visible", timeout=3500)
        dlg.click()
        print("    🟢 Clicked Continue dialog")
        human_sleep(0.6, 1.0)
    except Exception:
        # fallback: try any element containing "Continue" text
        try:
            candidate = page.locator("text=Continue").first
            if candidate.is_visible():
                candidate.click()
                print("    🟢 Clicked Continue (text fallback)")
                human_sleep(0.6, 1.0)
        except Exception:
            pass

    # Click Select Seats (attempt multiple selectors)
    seat_selectors = [
        "button:has-text('Select Seats')",
        "button:has-text('SELECT SEATS')",
        "div.sc-zgl7vj-7.kdBUB",
        "div[class*='select']",
    ]
    select_clicked = False
    for sel in seat_selectors:
        try:
            if page.locator(sel).count() > 0:
                btn = page.locator(sel).first
                btn.scroll_into_view_if_needed()
                btn.click()
                select_clicked = True
                print("    🎟️ Clicked Select Seats (selector:", sel, ")")
                break
        except Exception:
            human_sleep(0.6, 1.2)
            continue

    if not select_clicked:
        print("    ❌ Could not find/select 'Select Seats' button — closing tab.")
        page.close()
        return None

    # Wait for seat map to render
    human_sleep(2.0, 4.0)
    # Optionally scroll a little inside seat view
    try:
        page.mouse.wheel(0, 200)
    except:
        pass
    human_sleep(0.6, 1.2)

    # Screenshot seat area (element-screenshot preferred if we can find seat container)
    screenshot_name = f"seat_{idx+1}_{int(time.time())}.png"
    try:
        # try element-based screenshot first (more robust cropping)
        seat_elem_selectors = [
            "div.__seat-map", "div[aria-label*='Seat']", "div[class*='seat']"
        ]
        saved = False
        for sel in seat_elem_selectors:
            try:
                if page.locator(sel).count() > 0:
                    elem = page.locator(sel).first
                    elem.scroll_into_view_if_needed()
                    elem.screenshot(path=screenshot_name)
                    print(f"    📸 Element screenshot saved: {screenshot_name} (sel={sel})")
                    saved = True
                    break
            except Exception:
                continue
        if not saved:
            # fallback to clip screenshot of approximate area
            page.screenshot(path=screenshot_name, clip=SEATMAP_CLIP)
            print(f"    📸 Clipped screenshot saved: {screenshot_name}")
    except Exception as e:
        print("    ⚠️ Screenshot failed:", e)
        page.close()
        return None

    human_sleep(0.5, 1.2)

    # Analyze seats using OpenCV
    green_count = analyze_green_seats(screenshot_name)

    # Record results
    result = {
        "theatre": theatre_url.split("/cinemas/kochi/")[1].split("/buytickets")[0].replace("-", " ").title(),
        "movie": movie_name,
        "green_count": green_count,
        "screenshot": screenshot_name,
    }

    # Close tab
    page.close()
    return result

# ---------- Main runner ----------
def main():
    ensure_csv_header(CSV_FILE)
    with sync_playwright() as p:
        # Launch a headed browser (less likely to be detected than headless)
        browser = p.chromium.launch(headless=False, slow_mo=60)
        # Create a persistent context if you want to reuse cookies/profile:
        context = browser.new_context(viewport=VIEWPORT, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        try:
            for idx, url in enumerate(URLS):
                human_sleep(0.8, 2.0)
                result = process_one_theatre(context, url, idx)
                if result:
                    # append to CSV
                    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), result["theatre"], result["movie"], result["green_count"], result["screenshot"]])
                    print(f"Saved result for {result['theatre']}")
                else:
                    print(f"No result for URL: {url}")
                # small extra delay between tabs
                human_sleep(2.0, 5.0)
        finally:
            context.close()
            browser.close()
    print(f"\n✅ Done. Results saved to {CSV_FILE}")

if __name__ == "__main__":
    main()
