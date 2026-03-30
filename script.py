import requests
import os
import pdfplumber
import csv
from datetime import datetime, timedelta

# --- CONFIGURATION ---
PRICE_BOX = (480, 215, 545, 231) 
TARGET_FOLDER = 'Orlen_Prices'
CSV_FOLDER = 'Price_Data'
CSV_FILE = os.path.join(CSV_FOLDER, 'price_history.csv')

def extract_price(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            cropped = page.within_bbox(PRICE_BOX)
            raw_text = cropped.extract_text()
            if raw_text:
                return raw_text.replace(" ", "").replace(",", "").strip()
    except Exception as e:
        print(f"Error extracting: {e}")
    return None

def is_duplicate(date_str):
    """Checks if the date already exists in the CSV file."""
    if not os.path.isfile(CSV_FILE):
        return False
    with open(CSV_FILE, 'r', newline='') as f:
        reader = csv.reader(f)
        # Skip header, then check first column (Date)
        next(reader, None) 
        for row in reader:
            if row and row[0] == date_str:
                return True
    return False

def update_csv(date_str, price):
    """Appends a new row only if the date is new."""
    if not os.path.exists(CSV_FOLDER):
        os.makedirs(CSV_FOLDER)
        
    if is_duplicate(date_str):
        print(f"⏭️ Skipping {date_str}: Already exists in CSV.")
        return False

    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Date', 'Kaina_su_PVM']) 
        writer.writerow([date_str, price])
        print(f"💾 Saved {date_str} to CSV.")
    return True

def try_process_date(target_date):
    date_str = target_date.strftime('%Y-%m-%d')
    file_name = target_date.strftime('%Y_%m_%d_LT.pdf')
    
    # Check if we even need to bother downloading
    if is_duplicate(date_str):
        print(f"⏭️ {date_str} is already recorded. Skipping download.")
        return True # Return True to stop the "Lookback" loop

    year = target_date.strftime('%Y')
    month = target_date.strftime('%m')
    day = target_date.strftime('%d')
    url = f"https://www.orlenlietuva.lt/LT/Wholesale/Prices/Kainos%20{year}%20{month}%20{day}%20realizacija%20internet.pdf"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            if not os.path.exists(TARGET_FOLDER):
                os.makedirs(TARGET_FOLDER)
            path = os.path.join(TARGET_FOLDER, file_name)
            with open(path, 'wb') as f:
                f.write(response.content)
            
            price = extract_price(path)
            if price:
                update_csv(date_str, price)
                return True
        else:
            print(f"🔍 No file for {date_str} (404)")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    return False

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    today = datetime.now()
    print(f"--- Starting Scraper Run: {today.strftime('%Y-%m-%d')} ---")
    
    # Look back 5 days to find the most recent protocol not yet in our CSV
    for i in range(5):
        target_date = today - timedelta(days=i)
        if try_process_date(target_date):
            # If we successfully found a new file OR found a duplicate, we stop.
            break 
            
    print("--- Scraper Run Finished ---")
