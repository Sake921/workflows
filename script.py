import requests
import os
import pdfplumber
import csv
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# These coordinates are the "Box" where the price lives in the PDF
# (Left, Top, Right, Bottom)
PRICE_BOX = (450, 300, 535, 315) 

def extract_price(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        # 1. "Crop" the PDF to only look at that specific cell
        cropped_area = page.within_bbox(PRICE_BOX)
        
        # 2. Grab the text (e.g., "1 494.62" today, "1 502.10" tomorrow)
        raw_text = cropped_area.extract_text()
        
        if raw_text:
            # Clean up: remove spaces so "1 494.62" becomes "1494.62" (a clean number)
            clean_price = raw_text.replace(" ", "").strip()
            return clean_price
            
    return None # Return None if the box is empty

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
    
    # NEW: Extract and Save
    price = extract_price(path)
    if price:
        update_csv(date_str, price)
        print(f"✅ Success! Extracted Price: {price}")
    else:
        print("⚠️ PDF downloaded, but price not found at coordinates.")
else:
    print(f"❌ No file found for {date_str}")
