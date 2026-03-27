import pdfplumber

with pdfplumber.open("Orlen_Prices/2026_03_26_LT.pdf") as pdf:
    page = pdf.pages[0]
    # This prints every word with its exact box
    for word in page.extract_words():
        if "1 324.21" in word['text']:
            print(f"FOUND IT! Text: {word['text']} | Box: ({word['x0']}, {word['top']}, {word['x1']}, {word['bottom']})")
