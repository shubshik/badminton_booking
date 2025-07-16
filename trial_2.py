import asyncio
from datetime import date, timedelta
from playwright.async_api import async_playwright

EMAIL = "shubhambhatia94@gmail.com"
PASSWORD = "p5s7gPbNxBA**s"
import os
BOOK_SLOT = os.getenv("BOOK_SLOT", "8-9")  # "8-9" or "9-10"

def get_next_saturday():
    today = date.today()
    days_ahead = (5 - today.weekday()) % 7 -1  # Saturday=5, always next Saturday
    return today + timedelta(days=days_ahead)

def format_date_to_ddmm(d: date):
    return d.strftime("%d/%m")

async def book_badminton():
    next_saturday = get_next_saturday()
    target_date = format_date_to_ddmm(next_saturday)
    slot_time = "08:00 AM" if BOOK_SLOT == "8-9" else "09:00 AM"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://statesportcentres.perfectgym.com.au/ClientPortal2/#/FacilityBooking?clubId=1&zoneTypeId=28")
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(3000)

        # Login
        await page.fill("input[name='Login']", EMAIL)
        await page.fill("input[name='Password']", PASSWORD)
        await page.click("#confirm")

        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(5000)

        # 1. Find date column index for target_date
        date_boxes = page.locator("td.cp-calendar-date-box")
        date_count = await date_boxes.count()
        date_col_index = None
        for i in range(date_count):
            date_text = await date_boxes.nth(i).locator("div.cp-calendar-date").inner_text()
            print(f"Date header {i}: '{date_text}'")
            if date_text == target_date:
                date_col_index = i
                print(f"Found target date '{target_date}' at column index {date_col_index}")
                break

        if date_col_index is None:
            print(f"❌ Could not find target date column for {target_date}")
            await browser.close()
            return

        # 2. Find row index for slot_time in left time column
        time_cells = page.locator("td.cp-calendar-side-col > div.cp-calendar-hour")
        time_count = await time_cells.count()
        row_index = None
        for r in range(time_count):
            time_text = await time_cells.nth(r).inner_text()
            print(f"Time row {r}: '{time_text}'")
            if time_text.strip() == slot_time:
                row_index = r
                print(f"Found slot time '{slot_time}' at row index {row_index}")
                break

        if row_index is None:
            print(f"❌ Could not find row for slot time {slot_time}")
            await browser.close()
            return

        # 3. Select calendar row for slot time
        rows = page.locator("tr")  # adjust if necessary
        row = rows.nth(row_index)

        # 4. Select the date column cell inside that row
        cells = row.locator("td.cp-calendar-day-col")
        cell = cells.nth(date_col_index)

        # 5. Inside cell, find booking items with Book now button
        book_items = cell.locator("cp\\:facility-booking-item")
        item_count = await book_items.count()
        slot_booked = False

        for j in range(item_count):
            btn = book_items.nth(j).locator("text=Book now")
            if await btn.count() > 0:
                print(f"Booking slot {slot_time} on {target_date} (item {j})...")
                await btn.click()
                slot_booked = True
                break

        if not slot_booked:
            print(f"⚠️ No bookable slot found at {slot_time} on {target_date}")

        # Pause here to inspect or manually confirm
        print("✅ Reached booking step. Inspect or complete further steps manually.")
        await page.pause()

        # await browser.close()

asyncio.run(book_badminton())
