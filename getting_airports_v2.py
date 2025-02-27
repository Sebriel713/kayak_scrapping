from playwright.sync_api import sync_playwright, Playwright
from rich import print
import re
import csv

# Constants are put in UPPER CASE
START_URL = "http://kayak.com/airports"
CSV_FILENAME = "iata_codes.csv"

#We define a function that needs an instance of Play wright and will return a list of strings, translated to english
def fetch_airport_codes(playwright: Playwright) -> list[str]:
    #The function scrapes IATA airport codes from Kayak and returns them as a list.
    navigator = playwright.chromium #you may choose another browser
    browser = navigator.launch(headless=True) #Headless because we don't need to see it for it to happen 
    
    try:
        page = browser.new_page()
        page.goto(START_URL)
        page.wait_for_selector("section")  # Ensure content is loaded
        
        # Extract text content of airport table
        airports_table = page.locator("section").filter(has_text="CityAirportIATA codeA CoruñaA").text_content()
        
        # Extract IATA codes using regex
        iata_codes = re.findall(r'[A-Z]{3}', airports_table)
        
        print(f"[bold green]✅ Successfully extracted {len(iata_codes)} IATA codes.[/bold green]")
        return iata_codes
    
    except Exception as e:
        print(f"[bold red]❌ Error while scraping: {e}[/bold red]")
        return []
    
    finally:
        browser.close()  # Ensure browser is closed properly

def save_to_csv(iata_codes: list[str], filename: str = CSV_FILENAME) -> None:
    """Saves a list of IATA codes to a CSV file."""
    if not iata_codes:
        print("[bold yellow]⚠ No data to write. Skipping CSV export.[/bold yellow]")
        return

    try:
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows([[code] for code in iata_codes[1:]])  # Write IATA codes, 1 for line
        
        print(f"[bold cyan]📁 CSV file '{filename}' created successfully![/bold cyan]")
    
    except Exception as e:
        print(f"[bold red]❌ Error while writing CSV: {e}[/bold red]")



def main():
    """Main function to run the script."""
    with sync_playwright() as playwright:
        #First we run the function to get the IATA code
        iata_codes = fetch_airport_codes(playwright)
        save_to_csv(iata_codes)

if __name__ == "__main__":
    main()
