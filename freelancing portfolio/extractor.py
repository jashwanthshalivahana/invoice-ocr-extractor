import pytesseract
import re
import openpyxl
from PIL import Image
import pdf2image
import os
import sys

# ── Windows: set Tesseract path automatically ──────────────────────────────
if sys.platform == 'win32':
    _tess_default = r'C:\Program Files\Tesseract-OCR\tesseract.exe\tesseract.exe'
    if os.path.exists(_tess_default):
        pytesseract.pytesseract.tesseract_cmd = _tess_default
    else:
        # Search common locations
        for _drive in ['C', 'D']:
            _candidate = rf'{_drive}:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(_candidate):
                pytesseract.pytesseract.tesseract_cmd = _candidate
                break


def pdf_to_images(pdf_path):
    return pdf2image.convert_from_path(pdf_path, dpi=300)


def image_to_pil(image_path):
    img = Image.open(image_path)
    # Convert to RGB — Tesseract crashes on RGBA/palette PNGs on Windows
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')
    return [img]


def extract_text(image):
    # Ensure RGB before passing to tesseract
    if image.mode not in ('RGB', 'L'):
        image = image.convert('RGB')
    config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(image, config=config)


def parse_invoice(text):
    patterns = {
        'invoice_no': r'Invoice\s*#?\s*[:\-]?\s*([A-Z0-9\-]+)',
        'date':       r'Date\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        'vendor':     r'(?:From|Vendor|Bill\s*From|Company)\s*[:\-]?\s*([^\n]+)',
        'total':      r'Total\s*[:\-]?\s*(?:Rs\.?|₹|INR)?\s*([\d,]+\.?\d*)',
        'gst':        r'GST\s*(?:\(\d+%\))?\s*[:\-]?\s*(?:Rs\.?|₹|INR)?\s*([\d,]+\.?\d*)',
        'subtotal':   r'Sub\s*[Tt]otal\s*[:\-]?\s*(?:Rs\.?|₹|INR)?\s*([\d,]+\.?\d*)',
    }

    result = {}
    for key, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        result[key] = m.group(1).strip() if m else 'Not found'
    return result


def process_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        images = pdf_to_images(file_path)
    elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        images = image_to_pil(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    full_text = ''
    for img in images:
        try:
            full_text += extract_text(img) + '\n'
        except Exception as e:
            raise RuntimeError(
                f"Tesseract failed on {os.path.basename(file_path)}.\n"
                f"Make sure Tesseract is installed at:\n"
                f"  C:\\Program Files\\Tesseract-OCR\\tesseract.exe\n"
                f"Download: https://github.com/UB-Mannheim/tesseract/wiki\n"
                f"Original error: {e}"
            )

    data = parse_invoice(full_text)
    data['source_file'] = os.path.basename(file_path)
    data['raw_text'] = full_text[:500]
    return data


def save_to_excel(data_list, out='output/extracted.xlsx'):
    out_dir = os.path.dirname(out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Invoices'

    headers = ['Source File', 'Invoice No', 'Date', 'Vendor', 'Subtotal', 'GST', 'Total']
    keys    = ['source_file', 'invoice_no', 'date', 'vendor', 'subtotal', 'gst', 'total']

    from openpyxl.styles import Font, PatternFill, Alignment
    header_font = Font(bold=True, color='FFFFFF')
    header_fill = PatternFill('solid', start_color='2E4057')
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')

    for row_idx, d in enumerate(data_list, 2):
        for col_idx, key in enumerate(keys, 1):
            ws.cell(row=row_idx, column=col_idx, value=d.get(key, 'Not found'))

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    wb.save(out)
    print(f"Saved to {out}")
    return out