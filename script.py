import requests
import os
import pdfplumber
import csv
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# Replace these coordinates with the ones you find using the "Visual Debug"
# Format: (x0, top, x1, bottom)
PRICE_BOX = (440, 315, 520, 335) 
CSV_FILE = 'price_history.csv'
TARGET_FOLDER = 'Orlen_Prices'

def extract_price(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            # Crop to the particular place
            cropped = page.within_bbox(PRICE_BOX)
            text = cropped.extract_text()
            return text.strip() if text else None
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

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
