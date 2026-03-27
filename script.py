import requests
import os
from datetime import datetime, timedelta

# 1. Configuration (Local folder in your GitHub repo)
target_folder = 'Orlen_Prices'
if not os.path.exists(target_folder):
    os.makedirs(target_folder)

# 2. Generate the Dynamic URL
today = datetime.now()
yesterday = today - timedelta(days=1)
year = yesterday.strftime('%Y')
month = yesterday.strftime('%m')
day = yesterday.strftime('%d')

# Using your tested file naming and URL logic
file_name = f"{year}_{month}_{day}_LT.pdf"
full_url = f"https://www.orlenlietuva.lt/LT/Wholesale/Prices/Kainos%20{year}%20{month}%20{day}%20realizacija%20internet.pdf"

print(f"Attempting to download: {full_url}")

# 3. Download and Save
try:
    response = requests.get(full_url, stream=True, timeout=15)
    
    if response.status_code == 200:
        file_path = os.path.join(target_folder, file_name)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ Success! Saved to: {file_path}")
    elif response.status_code == 404:
        print(f"❌ File not found: {full_url}")
    else:
        print(f"⚠️ Failed with status code: {response.status_code}")

except Exception as e:
    print(f"An error occurred: {e}")
