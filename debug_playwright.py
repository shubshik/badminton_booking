import asyncio
from playwright.async_api import async_playwright

async def debug_page():
    async with async_playwright() as p:
        # Launch in headed mode for debugging
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        # Go to the badminton booking page
        await page.goto("https://statesportcentres.perfectgym.com.au/ClientPortal2/#/FacilityBooking?clubId=1&zoneTypeId=28")
        await page.wait_for_load_state('networkidle')

        # Pause here so you can inspect manually
        await page.goto("https://statesportcentres.perfectgym.com.au/ClientPortal2/#/FacilityBooking?clubId=1&zoneTypeId=28")
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(3000)  # extra wait for UI to render

        # Fill username & password
        await page.wait_for_selector("input[name='Login']")
        await page.fill("input[name='Login']", "shubhambhatia94@gmail.com")
        await page.fill("input[name='Password']", "p5s7gPbNxBA**s")

        # Click login button
        await page.click("#confirm")
        
        # Wait for login to complete
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(3000)

        await page.pause()  

        await browser.close()

asyncio.run(debug_page())
