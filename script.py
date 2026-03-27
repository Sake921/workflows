import requests
import os
import pdfplumber
import csv
from datetime import datetime, timedelta

# --- CONFIGURATION (Added the missing variables here) ---
PRICE_BOX = (480, 215, 545, 231)
TARGET_FOLDER = 'Orlen_Prices'
CSV_FOLDER = 'Price_Data'          # New folder name
CSV_FILE = os.path.join(CSV_FOLDER, 'price_history.csv')

def extract_price(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            cropped = page.within_bbox(PRICE_BOX)
            raw_text = cropped.extract_text()
            
            if raw_text:
                print(f"DEBUG: Found raw text: '{raw_text}'")
                # 1. Remove spaces: "1 324.21" -> "1324.21"
                # 2. Remove commas just in case: "1,324.21" -> "1324.21"
                clean_price = raw_text.replace(" ", "").replace(",", "").strip()
                return clean_price
    except Exception as e:
        print(f"Error: {e}")
    return None

if not os.path.exists(CSV_FOLDER):
    os.makedirs(CSV_FOLDER)

def update_csv(date_str, price):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Date', 'Price_EUR'])
        writer.writerow([date_str, price])

# --- MAIN LOGIC ---
today = datetime.now()
yesterday = today - timedelta(days=1)
date_str = yesterday.strftime('%Y-%m-%d')
file_name = yesterday.strftime('%Y_%m_%d_LT.pdf')

# Your tested URL logic
url = f"https://www.orlenlietuva.lt/LT/Wholesale/Prices/Kainos%20{yesterday.strftime('%Y')}%20{yesterday.strftime('%m')}%20{yesterday.strftime('%d')}%20realizacija%20internet.pdf"

if not os.path.exists(TARGET_FOLDER):
    os.makedirs(TARGET_FOLDER)

print(f"Checking: {url}")
response = requests.get(url, timeout=15)

if response.status_code == 200:
    path = os.path.join(TARGET_FOLDER, file_name)
    with open(path, 'wb') as f:
        f.write(response.content)
    
    # Extract and Save
    price = extract_price(path)
    if price:
        update_csv(date_str, price)
        print(f"✅ Success! Extracted Price: {price}")
    else:
        print(f"⚠️ PDF downloaded, but price not found at coordinates {PRICE_BOX}.")
else:
    print(f"❌ No file found for {date_str} (Status: {response.status_code})")
