import asyncio
from playwright.async_api import async_playwright
from rich import print
import csv
from datetime import datetime, date, timedelta
import re


START_URL = "http://kayak.com/"
CSV_FILENAME = "iata_codes.csv"

async def kayak_to_english(playwright, browser):
    """Launches browser, navigates to Kayak, and sets the language to English. Returns the Playwright page instance."""
    page = await browser.new_page()
    await page.goto(START_URL)
    
    try:
        # Click the navigation menu based on language
        await page.click("//div[contains(@aria-label, 'navegación')] | "
                         "//div[contains(@aria-label, 'menu principale')] | "
                         "//div[contains(@aria-label, 'navegação')]")  

        # Click language selection
        await page.click("//div[contains(@aria-label, 'Español')] | "
                         "//div[contains(@aria-label, 'Français')] | "
                         "//div[contains(@aria-label, 'English')] | "
                         "//div[contains(@aria-label, 'Português')]")

        # Select 'United States' as the region
        await page.fill('input#country-picker-search', 'United States')
        await page.press('input#country-picker-search', 'Enter')

        await page.wait_for_load_state("domcontentloaded")  # Ensure page is loaded
        await asyncio.sleep(2)  # Small delay to ensure elements render

        return page  # Return the Playwright page instance

    except Exception as e:
        print(f"❌ Error while changing page to English: {e}")
        await browser.close()
        return None  # Return None in case of failure

def process_input_text_airport(csv_input) -> str:
    """Gets user input and ensures it is uppercase."""
    try:
        if not csv_input:
            raise ValueError('Input is empty')
        return csv_input.upper().replace(' ', '')
    except Exception as e:
        return "ATL"

def check_airport(airport: str) -> bool:
    """Checks if the airport code exists in the CSV file."""
    try:
        with open(CSV_FILENAME, newline='') as f:
            reader = csv.reader(f)
            airport_data = [code[0] for code in reader]  # Flatten list
        
        if airport in airport_data:
            return True
        else:
            return False
    except Exception as e:
        print(f"❌ Error whilst checking if airport exists in the data: {e}")
        return False

async def start_airport(page, airport: str):
    """Interacts with the airport input field on the same Playwright instance. For the starting point."""
    try:
        await page.get_by_label("Remove value").click()
        await page.get_by_label('Flight origin input').fill(airport)
        await page.wait_for_load_state('load')
        await page.wait_for_timeout(2000)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(1000)  

    except Exception as e:
        print(f"❌ Error while interacting with the starting airport input field: {e}")

async def end_airport(page, airport: str):
    """Interacts with the destination airport input field."""
    try:
        await page.get_by_label('Flight destination input').fill(airport)
        await page.wait_for_load_state('load')
        await page.wait_for_timeout(1000)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(1000)  

    except Exception as e:
        print(f"❌ Error while interacting with the ending airport input field: {e}")


def check_date_input(date_input):
    try:
        '''Select a valid date in the format DD-MM-YYYY 🗓️'''
        date_input = (date_input).replace(' ', '')
        date_obj  = datetime.strptime(date_input, '%d-%m-%Y')
        # Stop execution and raise an error if the date is in the future or today
        if days_since_date(date_obj.date()) <= 0:
            return (datetime.strptime((datetime.today() + timedelta(days=1)).strftime('%d-%m-%Y'), '%d-%m-%Y')) #Returns Tomorrow's date
        if days_since_date(date_obj.date()) < 364:
            return date_obj  # Return the datetime object if valid
        else:
            return (datetime.strptime((datetime.today() + timedelta(days=362)).strftime('%d-%m-%Y'), '%d-%m-%Y'))
    except Exception as e:
        print(f"❌ Error while interacting with the date input field: {e}")

def days_since_date(date_obj: object) -> int:
    """
    Returns the absolute difference in days between the given date and today's date.
    Accounts for leap years automatically.
    """
    today = date.today()
    return ((date_obj - today).days)

async def move_calendar(page, n_moves: int):
    try:
        #await page.get_by_label("Previous month").click()
        for m in range(n_moves):
            await page.get_by_label("Next month").click()
    except Exception as e:
        print(f"❌ Error whilst moving calendar selector: {e}")
        
def calculate_move(initial_date: object, final_date: object) -> int:
    '''It calculates how many times the calendar has to be moved to arrive to the wanted month'''
    try:
        initial_month = initial_date.month
        initial_year = initial_date.year
        
        given_month, given_year = final_date.month, final_date.year
        
        return ((given_month - initial_month) + ((given_year - initial_year)*12))
    except Exception as e:
        print(f"❌ Error while interacting whilst selecting date: {e}")

async def select_date(page, date_obj1: object, date_obj2: object, browser):
    try:
        if date_obj1 >= date_obj2:
            date_obj2 = date_obj1 + timedelta(1)

        # Wait for the page to load
        await page.wait_for_load_state('load')

        # Select the start date
        await page.get_by_role("button", name="Departure", exact=True).click()

        # Move the calendar and select the first date
        await move_calendar(page, calculate_move(datetime.now(), date_obj1))
        await page.click(f"//div[contains(@aria-label, '{date_obj1.strftime('%B')} {date_obj1.day}')]")

        # Move the calendar and select the second date
        await move_calendar(page, calculate_move(date_obj1, date_obj2))
        await page.click(f"//div[contains(@aria-label, '{date_obj2.strftime('%B')} {date_obj2.day}')]")

        old_url = page.url
        new_urls = []

        # Ensure the browser is still open before adding event listeners
        if not browser.is_connected():
            raise Exception("Browser was closed unexpectedly.")

        # Function to handle new pages
        async def handle_new_page(new_page):
            try:
                await new_page.wait_for_load_state('load')
                new_urls.append(new_page.url)
            except Exception as e:
                print(f"❌ Error handling new page: {e}")

        # Attach event listener before clicking the search button
        context = browser.contexts[0]
        context.on("page", handle_new_page)

        # Click the search button
        await page.click('//button[contains(@aria-label, "Search")]')

        # Wait for a new URL to load
        await asyncio.sleep(7)  # Adjust if needed

        # Filter URLs to get the valid one
        valid_urls = [url for url in new_urls if url != old_url and "hotel" not in url.lower()]

        # Ensure the browser is still open before closing
        if browser.is_connected():
            await browser.close()

        return valid_urls[0] if valid_urls else page.url  # Return the valid new URL or fallback to the original

    except Exception as e:
        print(f"❌ Error whilst selecting date: {e}")
        return None



from datetime import datetime

async def select_travelers(page, initial_traveler_input, initial_class_input):
    values = get_travelers_list(initial_traveler_input)
    await page.get_by_text("adult, Economy").click()
    for n in range(values[0]):
        await page.locator("button:nth-child(3)").first.click()  #Adults
    for n in range(values[1]):
        await page.locator("div:nth-child(3) > .FkqV-inner > .T_3c > button:nth-child(3)").click() # Students
    for n in range(values[2]):
        await page.locator("div:nth-child(4) > .FkqV-inner > .T_3c > button:nth-child(3)").click() # Seniors
    for n in range(values[3]):
        await page.locator("div:nth-child(5) > .FkqV-inner > .T_3c > button:nth-child(3)").click() # Youths
    for n in range(values[4]):
        await page.locator("div:nth-child(6) > .FkqV-inner > .T_3c > button:nth-child(3)").click() # Children
    for n in range(values[5]):
        await page.locator("div:nth-child(7) > .FkqV-inner > .T_3c > button:nth-child(3)").click() # Todlers
    for n in range(values[6]):
        await page.locator("div:nth-child(8) > .FkqV-inner > .T_3c > button:nth-child(3)").click() # Infants
    match get_class_type(initial_class_input):
        case "1":
            await page.get_by_role("radio", name="Premium Economy").click() 
        case "2":
            await page.get_by_role("radio", name="Business").click()
        case "3":
            await page.get_by_role("radio", name="First").click()

    
    
    

def get_class_type(initial_input) -> str:
    input_class = re.sub(r"[^0-9]", "", initial_input)
    input_class = input_class[0]
    return input_class

def get_travelers_list(initial_input) -> list:
    traveler_input = re.sub(r"[^0-9,]", "", initial_input).split(',')
    traveler_values = [value if value != "" else "0" for value in traveler_input]
    traveler_values = [int(x) for x in traveler_values]
    #we need to make sure all values aren't negative
    traveler_values = [0 if value < 0 else value for value in traveler_values]
    if len(traveler_values) > 7:
        traveler_values = traveler_values[0:7]
    elif len(traveler_values) < 7:
        traveler_values.extend([0] * (7 - len(traveler_values))) 
    # 1 < Adults + Students + Seniors <= 9 by kayak's standards
    if (sum(traveler_values[:3]) < 1):
        traveler_values[0] = 1
    if (sum(traveler_values[:3])) > 9:
        #This part gets the index of the highest value \     this part reduces said value by its excess
        excess = sum(traveler_values[:3]) - 9
        for i in range(3):
            if traveler_values[i] > excess:
                traveler_values[i] -= excess
                break
            else:
                excess -= traveler_values[i]
                traveler_values[i] = 0
    # Children + Todlers + Infants <= 7 by kayak's standards
    if (sum(traveler_values[-4:]) > 7):
        excess = sum(traveler_values[-4:]) - 7
        for i in range(-4,0):
            if traveler_values[i] > excess:
                traveler_values[i] -= excess
                break
            else:
                excess -= traveler_values[i]
                traveler_values[i] = 0
    if sum(traveler_values[:3]) < (traveler_values[6]):
        traveler_values[6] = sum(traveler_values[:3])
    return traveler_values
    
async def get_flight_data(page, url):
    await page.goto(url)
    await page.pause()

    

async def get_link(starting_airport: str, ending_airport: str, 
                   start_date: str, end_date: str, passengers: str, flight_class: str) -> None:
    airport_input_start = process_input_text_airport(starting_airport)
    airport_input_end = process_input_text_airport(ending_airport) 
    
    date_input_start = check_date_input(start_date)
    date_input_end = check_date_input(end_date)
    
    
    """Main function to run the script asynchronously."""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False, slow_mo=50)
        page = await kayak_to_english(playwright, browser)  # Get the page instance

        if page is None:
            print("❌ Page failed to load.")
            return  # Exit if language setting failed


        
        if check_airport(airport_input_start) and check_airport(airport_input_end):
            await start_airport(page, airport_input_start)
            await end_airport(page, airport_input_end)
        else:
            await start_airport(page, 'ATL')
            await end_airport(page, 'DXB')
            
        
        await  select_travelers(page, passengers, flight_class)
        return (await select_date(page, date_input_start, date_input_end, browser) )

def save_url(url: str) -> None:
    file_path = 'generated_links.csv'
    
    data = [number_rows_file() - 1, url]
    
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def number_rows_file():
    file_path = 'generated_links.csv'
    
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        
        n_rows = sum(1 for row in reader)
        
    return n_rows
    
def create_file_save():
    file_path = 'generated_links.csv'
    
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Id", "URL"])

def get_multiple_inputs() -> list:
    file_path = 'multiple_links_input.csv'
    multiple_inputs = []
    
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for input in reader:    
            multiple_inputs.append(input[1:])
        return multiple_inputs


async def main():
    create_file_save()
    multiple_inputs = (get_multiple_inputs())
    for csv_input in multiple_inputs:
        starting_airport = csv_input[0]
        ending_airport = csv_input[1]
        start_date = csv_input[2]
        end_date = csv_input [3]
        passengers = ','.join(csv_input[4:11])
        flight_class = csv_input[11]
        new_link = await get_link(starting_airport, 
                                  ending_airport, 
                                  start_date, 
                                  end_date, 
                                  passengers, 
                                  flight_class)
        save_url(new_link)

if __name__ == "__main__":
    asyncio.run(main())
    