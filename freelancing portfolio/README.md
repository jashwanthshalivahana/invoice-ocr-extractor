# 🧾 Invoice OCR Extractor

Automatically extract data from invoice PDFs or images into structured Excel files.
No manual data entry. Processes 100+ invoices in minutes.

---

## What it extracts

- **Vendor name** · Invoice date · Invoice number
- Line item subtotal · GST amounts · **Grand total**

---

## Setup

### 1. Install system dependencies

**Ubuntu / Debian**
```bash
sudo apt update
sudo apt install tesseract-ocr poppler-utils
```

**macOS**
```bash
brew install tesseract poppler
```

**Windows**
- Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Download poppler: https://github.com/oschwartz10612/poppler-windows/releases
- Add both to your system PATH

### 2. Install Python packages
```bash
pip install -r requirements.txt
```

---

## Usage

### CLI (Command Line)
```bash
# Single invoice (PDF or image)
python main.py sample_invoices/sample1.pdf

# Entire folder of invoices
python main.py sample_invoices/

# Custom output file
python main.py invoices/ --out results/my_invoices.xlsx
```

### GUI (Graphical Interface)
```bash
python gui.py
```
- Click **+ Add Files** to add PDFs/images
- Click **+ Add Folder** to batch-add a folder
- Click **⬇ Extract → Excel** to run OCR and save output

### Generate sample invoices (for demo/testing)
```bash
python sample_invoices/generate_samples.py
```

---

## Project structure

```
invoice-ocr-extractor/
├── README.md
├── requirements.txt        ← pytesseract, pillow, openpyxl, pdf2image
├── main.py                 ← CLI: python main.py invoice.pdf
├── gui.py                  ← Tkinter drag-and-drop GUI
├── extractor.py            ← core OCR + parsing logic
├── sample_invoices/
│   ├── generate_samples.py ← creates 3 demo invoice PNGs
│   └── sample1.png …       ← sample files (after running generator)
└── output/                 ← extracted Excel files land here
```

---

## How it works

1. **PDF → Images** — `pdf2image` converts each PDF page to a high-res image (300 DPI)
2. **OCR** — `pytesseract` (Google Tesseract) reads text from each image
3. **Parse** — Regex patterns extract invoice number, date, vendor, subtotal, GST, total
4. **Export** — `openpyxl` writes everything to a formatted `.xlsx` file

---

## Built by

[Your name] — Python Automation Developer, Hyderabad  
Upwork: [link] | Fiverr: [link] | GitHub: [link]
