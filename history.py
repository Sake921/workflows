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
        print(f"Error reading {pdf_path}: {e}")
    return None

def rebuild_history():
    if not os.path.exists(TARGET_FOLDER):
        os.makedirs(TARGET_FOLDER)
    if not os.path.exists(CSV_FOLDER):
        os.makedirs(CSV_FOLDER)

    # 1. DOWNLOAD MISSING PDFs
    start_date = datetime(2026, 2, 1)
    end_date = datetime.now() # Goes up to today
    current_date = start_date

    print(f"📥 Checking for missing PDFs...")
    while current_date <= end_date:
        date_parts = current_date.strftime('%Y %m %d').split()
        file_name = f"{date_parts[0]}_{date_parts[1]}_{date_parts[2]}_LT.pdf"
        url = f"https://www.orlenlietuva.lt/LT/Wholesale/Prices/Kainos%20{date_parts[0]}%20{date_parts[1]}%20{date_parts[2]}%20realizacija%20internet.pdf"
        path = os.path.join(TARGET_FOLDER, file_name)

        if not os.path.exists(path):
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    with open(path, 'wb') as f:
                        f.write(r.content)
                    print(f"  ✅ Downloaded: {file_name}")
            except: pass
        current_date += timedelta(days=1)

    # 2. READ ALL PDFs AND CREATE CSV
    print(f"📝 Extracting data from all saved PDFs...")
    all_data = []
    
    # Get all PDF files and sort them so the CSV is in order
    pdf_files = sorted([f for f in os.listdir(TARGET_FOLDER) if f.endswith('.pdf')])

    for filename in pdf_files:
        path = os.path.join(TARGET_FOLDER, filename)
        # Extract date from filename: 2026_02_01_LT.pdf -> 2026-02-01
        date_str = filename.replace('_LT.pdf', '').replace('_', '-')
        
        price = extract_price(path)
        if price:
            all_data.append([date_str, price])
            print(f"  ✨ {date_str}: {price}")

    # Write fresh CSV (overwrites existing to ensure no duplicates)
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Kaina_su_PVM'])
        writer.writerows(all_data)

    print(f"🚀 Done! {len(all_data)} prices saved to {CSV_FILE}")

if __name__ == "__main__":
    rebuild_history()
