import requests
import os
from datetime import datetime, timedelta

def download_history():
    target_folder = 'Orlen_Prices'
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Start date: Feb 1, 2026
    current_date = datetime(2026, 2, 1)
    # End date: March 31, 2026
    end_date = datetime(2026, 3, 31)

    print(f"Starting historical download from {current_date.date()} to {end_date.date()}...")

    while current_date <= end_date:
        year = current_date.strftime('%Y')
        month = current_date.strftime('%m')
        day = current_date.strftime('%d')

        file_name = f"{year}_{month}_{day}_LT.pdf"
        # Using your confirmed working URL structure
        url = f"https://www.orlenlietuva.lt/LT/Wholesale/Prices/Kainos%20{year}%20{month}%20{day}%20realizacija%20internet.pdf"
        
        file_path = os.path.join(target_folder, file_name)

        # Skip if we already have it
        if os.path.exists(file_path):
            current_date += timedelta(days=1)
            continue

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Saved: {file_name}")
            else:
                # Silently skip 404s (weekends/holidays)
                pass
        except Exception as e:
            print(f"⚠️ Error on {file_name}: {e}")

        current_date += timedelta(days=1)

    print("Done!")

if __name__ == "__main__":
    download_history()
