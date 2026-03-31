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

def get_csv_stats():
    """Counts how many data rows exist in the CSV."""
    if not os.path.isfile(CSV_FILE):
        return 0
    with open(CSV_FILE, 'r', newline='') as f:
        return sum(1 for row in csv.reader(f)) - 1 # Subtract header

def is_duplicate(date_str):
    if not os.path.isfile(CSV_FILE):
        return False
    with open(CSV_FILE, 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader, None) 
        for row in reader:
            if row and row[0] == date_str:
                return True
    return False

def update_csv(date_str, price):
    if not os.path.exists(CSV_FOLDER):
        os.makedirs(CSV_FOLDER)
        
    if is_duplicate(date_str):
        print(f"⏭️ Skipping {date_str}: Already in CSV.")
        return False

    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Date', 'Kaina_su_PVM']) 
        writer.writerow([date_str, price])
        print(f"💾 Saved {date_str}: {price}")
    return True

def try_process_date(target_date):
    date_str = target_date.strftime('%Y-%m-%d')
    file_name = target_date.strftime('%Y_%m_%d_LT.pdf')
    
    # Check duplicate before downloading to save time/bandwidth
    if is_duplicate(date_str):
        return "DUPLICATE"

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
                if update_csv(date_str, price):
                    return "SUCCESS"
        else:
            print(f"🔍 No file for {date_str} (Status 404)")
    except Exception as e:
        print(f"⚠️ Network error: {e}")
    return "NOT_FOUND"

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    today = datetime.now()
    print(f"--- Starting Scraper Run: {today.strftime('%Y-%m-%d %H:%M')} ---")
    
    found_new = False
    for i in range(5): # Look back up to 5 days
        target_date = today - timedelta(days=i)
        result = try_process_date(target_date)
        
        if result == "SUCCESS":
            found_new = True
            break # Stop once we find the newest available protocol
        elif result == "DUPLICATE":
            print(f"✅ Most recent protocol ({target_date.strftime('%Y-%m-%d')}) is already in CSV.")
            break

    # Summary Print
    total_records = get_csv_stats()
    print("---------------------------------------")
    print(f"📊 SUMMARY: CSV now contains {total_records} price records.")
    print("--- Scraper Run Finished ---")
