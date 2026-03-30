import requests
import os
import pdfplumber
import csv
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# The exact coordinates found for the price 1 324.21
PRICE_BOX = (480, 215, 545, 231) 
TARGET_FOLDER = 'Orlen_Prices'
CSV_FOLDER = 'Price_Data'
CSV_FILE = os.path.join(CSV_FOLDER, 'price_history.csv')

def extract_price(pdf_path):
    """Opens the PDF, crops to the PRICE_BOX, and cleans the text into a number."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            # Crop the page to the specific price cell
            cropped = page.within_bbox(PRICE_BOX)
            raw_text = cropped.extract_text()
            
            if raw_text:
                print(f"DEBUG: Found raw text in {pdf_path}: '{raw_text}'")
                # Remove spaces (1 324.21 -> 1324.21) and commas
                clean_price = raw_text.replace(" ", "").replace(",", "").strip()
                return clean_price
    except Exception as e:
        print(f"Error extracting from {pdf_path}: {e}")
    return None

def update_csv(date_str, price):
    """Appends a new row to the CSV. Creates folder/headers if they don't exist."""
    if not os.path.exists(CSV_FOLDER):
        os.makedirs(CSV_FOLDER)
        
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Date', 'Kaina_su_PVM']) 
        writer.writerow([date_str, price])

def try_process_date(target_date):
    """Attempts to download and parse the PDF for a specific date."""
    date_str = target_date.strftime('%Y-%m-%d')
    file_name = target_date.strftime('%Y_%m_%d_LT.pdf')
    
    # Orlen URL format: Kainos YYYY MM DD realizacija internet.pdf
    year = target_date.strftime('%Y')
    month = target_date.strftime('%m')
    day = target_date.strftime('%d')
    
    url = f"https://www.orlenlietuva.lt/LT/Wholesale/Prices/Kainos%20{year}%20{month}%20{day}%20realizacija%20internet.pdf"
    
    print(f"Checking: {url}")
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
                print(f"✅ Success for {date_str}: {price}")
                return True
            else:
                print(f"⚠️ PDF found for {date_str}, but box {PRICE_BOX} was empty.")
        else:
            print(f"❌ File not found for {date_str} (Status: {response.status_code})")
    except Exception as e:
        print(f"⚠️ Connection error for {date_str}: {e}")
    
    return False

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    today = datetime.now()
    
    print(f"--- Starting Scraper Run: {today.strftime('%Y-%m-%d %H:%M')} ---")
    
    # Step 1: Try Today
    if not try_process_date(today):
        print("Falling back to Yesterday's data...")
        # Step 2: Fallback to Yesterday if Today isn't published yet
        yesterday = today - timedelta(days=1)
        if not try_process_date(yesterday):
            print("Final Result: No new data found for Today or Yesterday.")
    
    print("--- Scraper Run Finished ---")
