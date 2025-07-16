import asyncio
from datetime import date, timedelta
from playwright.async_api import async_playwright

# Hardcoded credentials for debug — replace with env vars or secure store later
EMAIL = "shubhambhatia94@gmail.com"
PASSWORD = "p5s7gPbNxBA**s"

# Pass slot via environment or hardcode for debug
import os
BOOK_SLOT = os.getenv("BOOK_SLOT", "8-9")  # "8-9" or "9-10"

def get_next_saturday():
    today = date.today()
    days_ahead = (5 - today.weekday()) % 7 - 2  # Saturday=5, always get next Saturday
    return today + timedelta(days=days_ahead)

def format_date_to_ddmm(d: date):
    return d.strftime("%d/%m")  # e.g. "26/07"

async def book_badminton():
    next_saturday = get_next_saturday()
    target_date = format_date_to_ddmm(next_saturday)
    slot_time = "08:00 AM" if BOOK_SLOT == "8-9" else "09:00 AM"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headed for debug
        context = await browser.new_context()
        page = await context.new_page()

        # Go to booking page
        await page.goto("https://statesportcentres.perfectgym.com.au/ClientPortal2/#/FacilityBooking?clubId=1&zoneTypeId=28")
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(3000)

        # Login
        await page.fill("input[name='Login']", EMAIL)
        await page.fill("input[name='Password']", PASSWORD)
        await page.click("#confirm")

        # Wait for login to complete & page to load
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(5000)

        # Find all date headers
        date_boxes = page.locator("td.cp-calendar-date-box")
        date_count = await date_boxes.count()

        slot_booked = False

        print(f"Looking for date: {target_date}")
        for i in range(date_count):
            date_text = await date_boxes.nth(i).locator("div.cp-calendar-date").inner_text()
            print(f"Date header {i}: '{date_text}'")
            if date_text == target_date:
                day_col = page.locator("td.cp-calendar-day-col").nth(i)
                booking_items = day_col.locator("cp\\:facility-booking-item")
                item_count = await booking_items.count()
                print(f"Found {item_count} slots on {date_text}")
                for j in range(item_count):
                    start_time = await booking_items.nth(j).locator("div.calendar-item-start").inner_text()
                    print(f"Slot {j}: '{start_time}'")
                    if start_time.strip() == slot_time:
                        print(f"Booking slot {start_time} on {date_text}")
                        await booking_items.nth(j).locator("text=Book now").click()
                        slot_booked = True
                        break
                if slot_booked:
                    break

        for i in range(date_count):
            date_text = await date_boxes.nth(i).locator("div.cp-calendar-date").inner_text()
            if date_text == target_date:
                # Found next Saturday column index
                day_col = page.locator("td.cp-calendar-day-col").nth(i)
                booking_items = day_col.locator("cp\\:facility-booking-item")
                item_count = await booking_items.count()

                for j in range(item_count):
                    start_time = await booking_items.nth(j).locator("div.calendar-item-start").inner_text()
                    if start_time == slot_time:
                        print(f"Attempting to book slot {slot_time} on {target_date}...")
                        await booking_items.nth(j).locator("text=Book now").click()
                        slot_booked = True
                        break
                break

        if not slot_booked:
            print(f"⚠️ Could not find slot {slot_time} on {target_date}")
            await browser.close()
            return

        # Pause here for you to inspect or handle confirmation/payment steps
        print("✅ Slot selected, waiting for booking confirmation/payment...")
        await page.pause()

        # TODO: Automate confirmation modal + payment input here as needed

        # Close browser after done or keep open for debugging
        # await browser.close()

asyncio.run(book_badminton())
