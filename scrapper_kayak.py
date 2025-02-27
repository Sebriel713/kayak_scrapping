import asyncio
from playwright.async_api import async_playwright, Page
from rich import print
from itertools import chain
import csv



from playwright.async_api import async_playwright

async def get_info(page: Page, url:str) -> list:
    all_flights = await page.locator('div.Fxw9-result-item-container').all()
    flights_data = []
    
    for flight in all_flights:
        try:
            single_flight_data = [url]
            await flight.scroll_into_view_if_needed()  # Ensure it's visible
            price = await flight.locator("div.f8F1-price-text").text_content(timeout=1000)
            single_flight_data.append(price)
            
            
            content_section_list = await flight.locator('.nrc6-content-section .hJSA-list .hJSA-item').all()

            for li in content_section_list:

                div_time_airline = li.locator('.VY2U')  # No await needed
                div_time = await div_time_airline.locator('.vmXl.vmXl-mod-variant-large').text_content()
                div_airline = await div_time_airline.locator('.c_cgF.c_cgF-mod-variant-default').text_content()
                div_stop = await li.locator('.JWEO .vmXl.vmXl-mod-variant-default').text_content()
                div_places_stop = await li.locator('.JWEO .c_cgF.c_cgF-mod-variant-default').text_content()
                div_duration = await li.locator('.xdW8 .vmXl.vmXl-mod-variant-default').text_content()

                # Append all extracted values to the temporary list
                single_flight_data.extend([div_time, div_airline, div_stop, div_places_stop, div_duration])
                single_flight_data = [item.replace("–", "-").replace("—", "-") for item in single_flight_data]
            
                flights_data.append(single_flight_data)
        except Exception as e:
            continue
    
    return flights_data
# Run your Playwright script as usual

def get_multiple_inputs() -> list:
    file_path = 'generated_links.csv'
    multiple_inputs = []
    
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for input in reader:    
            multiple_inputs.append(input[1:])
        return list(chain.from_iterable(multiple_inputs))
def store_info(info: list) -> None:
    file_path = 'kayak_flights_data.csv'
    header = [
    "Search_URL",
    "Price",
    "Outbound_Timing",
    "Outbound_Airline",
    "Outbound_Stops",
    "Outbound_Layover_Airport",
    "Outbound_Total_Duration",
    "Return_Timing",
    "Return_Airline",
    "Return_Stops",
    "Return_Layover_Airport",
    "Return_Total_Duration"
]
    
        

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for flight in info:
            writer.writerow(flight)
        

async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        
        page = await browser.new_page()
        for i, url in enumerate(get_multiple_inputs(), start=0):
            await page.goto(url)
            info = await get_info(page, url)
            store_info(info)
            print(info)
        await browser.close()

import asyncio
asyncio.run(main())
