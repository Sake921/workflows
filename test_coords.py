import pdfplumber
import os

# Use the file you already have in your repo
pdf_path = "Orlen_Prices/2026_03_26_LT.pdf" 

if not os.path.exists(pdf_path):
    print(f"❌ Error: {pdf_path} not found. Run your main scraper first to download it.")
else:
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        print("--- SEARCHING FOR COORDINATES ---")
        found = False
        for word in page.extract_words():
            # We search for the known price to "map" the coordinates
            if "324.21" in word['text']:
                print(f"✅ MATCH FOUND!")
                print(f"Text: {word['text']}")
                print(f"Suggested PRICE_BOX: ({word['x0']}, {word['top']}, {word['x1']}, {word['bottom']})")
                found = True
        
        if not found:
            print("❌ Could not find '324.21'. Printing all words in that area...")
            # If it fails, this helps you see what IS there
            for word in page.extract_words():
                if 400 < word['x0'] < 600: # Only show words on the right side
                    print(f"{word['text']}: ({word['x0']}, {word['top']})")
