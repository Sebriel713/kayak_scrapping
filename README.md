# Kayak Flights Web Scraping Project

## Overview

Welcome! This project was created to improve my coding skills through hands-on experience with web scraping. It is not the most efficient or optimized implementation, and there is room for improvement. Suggestions and contributions are always welcome! 😁

## ⚠️ Disclaimer 
(Better be safe than sorry😅)

This project scrapes data from [Kayak](https://www.kayak.com/) for educational purposes only. **Web scraping may violate the terms of service** of certain websites. It is the user's responsibility to ensure compliance with Kayak's terms before running the scraper. The developer assumes no responsibility for any legal issues that may arise from using this code.

---

## Project Structure

The project consists of two main components:
1. **Link Generation:** Automatically generates Kayak search URLs based on flight details.
2. **Data Scraping:** Extracts flight information from the generated URLs.

### 📂 Accessory Code

#### `getting_airports_v2.py`
- Scrapes all available airports from [Kayak's airport list](https://www.kayak.com/airports).
- Outputs a CSV file (`iata_codes.csv`) containing valid airport codes.
- Useful for then verifying the airports inputed exist

### 📂 Main Code

#### `MultipleLinks_kayakv2.py`
- Reads flight details from `multiple_links_input.csv` and generates corresponding Kayak search URLs.
- Outputs the generated URLs in `generated_links.csv`.
- **CSV Format:**

  ```csv
  id,starting_airport,ending_airport,start_date,end_date,adults,students,seniors,youths,children,toddlers,infants,flight_class
  1,JFK,LAX,22-06-2025,15-08-2025,1,0,0,0,1,0,0,1
  ```
  - The airports must be inputed with their **IATA code**.
  - The dates are in the format **DD-MM-YYYY**.  

  - The above entry corresponds to a round-trip flight from **John F. Kennedy (JFK) to Los Angeles (LAX)**, departing **June 22, 2025**, and returning **August 15, 2025**.
  - Passenger details: **1 adult, 1 child**.
  - Flight class: **Premium Economy** (`1`).



- **Flight Class Encoding:**
  - `0` = Economy  
  - `1` = Premium Economy  
  - `2` = Business Class  
  - `3` = First Class  

#### `scraper_kayak.py`
- Reads the generated URLs from `generated_links.csv`.
- Scrapes flight data from Kayak.
- Does **not** scrape all possible flights due to page load limitations.
    - This could potentially easily be solved, but in truth the actually important flights are the ones that kayak already loads.
- Focuses on the **best-ranked flight options** instead of scraping every available listing.

---

## 📌 Installation

### Prerequisites
Ensure you have Python installed (>= 3.7).

### Install Dependencies
Run the following command to install the required libraries:
```bash
pip install -r requirements.txt
```

```

---

## 🚀 Usage

### 1️⃣ Generate Flight Search URLs
Run the script to create Kayak search links based on your flight details:
```bash
python MultipleLinks_kayakv2.py
```

### 2️⃣ Scrape Flight Data
Once the URLs are generated, run the scraper:
```bash
python scraper_kayak.py
```

The extracted data will be stored in a CSV file for further analysis.



## 🤝 Contributions
Feel free to submit pull requests or open issues if you have suggestions! 

I cannot express how happy I'm with this experience. Doing the project was super fun and challenging. The code has many errors and could be improven on a lot. I'm in no way a senior developer or professional, so, really, any input is happily received. 

Alas, I wanted to thank the internet for helping creating this project, for I've benefited a lot from many platforms that could give insights or help to either format or make my code better/more efficient. Happy coding!

