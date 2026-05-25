#!/usr/bin/env python3
"""
Generates 3 sample invoice PDFs using only Pillow (no reportlab needed).
Run once: python sample_invoices/generate_samples.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.dirname(__file__)

INVOICES = [
    {
        'invoice_no': 'INV-2024-001',
        'date': '15/01/2024',
        'vendor': 'TechSolutions Pvt Ltd',
        'items': [('Web Development', 45000), ('Hosting (1yr)', 6000)],
        'gst_pct': 18,
    },
    {
        'invoice_no': 'INV-2024-042',
        'date': '03/03/2024',
        'vendor': 'CloudPrint Services',
        'items': [('Brochure Printing x500', 12500), ('Design Fee', 3000)],
        'gst_pct': 12,
    },
    {
        'invoice_no': 'INV-2024-107',
        'date': '22/06/2024',
        'vendor': 'DataVault Analytics',
        'items': [('Monthly Analytics Report', 8000), ('Dashboard Setup', 15000), ('Training Session', 5000)],
        'gst_pct': 18,
    },
]


def make_invoice_image(inv):
    W, H = 794, 1123  # A4 at 96dpi
    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)

    # Try to use a basic font; fall back to default
    try:
        font_big   = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
        font_med   = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    except Exception:
        font_big = font_med = font_small = ImageFont.load_default()

    # Header band
    d.rectangle([0, 0, W, 90], fill='#2E4057')
    d.text((40, 22), 'TAX INVOICE', font=font_big, fill='white')
    d.text((W - 280, 28), inv['vendor'], font=font_small, fill='#a8d8ea')

    # Meta info
    y = 110
    d.text((40, y),       f"Invoice No : {inv['invoice_no']}", font=font_med, fill='#222')
    d.text((40, y + 30),  f"Date       : {inv['date']}",       font=font_med, fill='#222')
    d.text((40, y + 60),  f"Vendor     : {inv['vendor']}",     font=font_med, fill='#222')
    d.text((40, y + 90),  'Bill To    : Sample Client Co.',    font=font_med, fill='#222')

    # Table header
    ty = 260
    d.rectangle([40, ty, W - 40, ty + 30], fill='#dce8f5')
    d.text((50,  ty + 6), 'Description',    font=font_small, fill='#2E4057')
    d.text((500, ty + 6), 'Amount (INR)',   font=font_small, fill='#2E4057')

    subtotal = 0
    ty += 40
    for desc, amt in inv['items']:
        d.text((50,  ty), desc,        font=font_small, fill='#333')
        d.text((500, ty), f'Rs. {amt:,}', font=font_small, fill='#333')
        subtotal += amt
        ty += 30

    # Totals
    gst_amt = int(subtotal * inv['gst_pct'] / 100)
    total   = subtotal + gst_amt

    ty += 10
    d.line([40, ty, W - 40, ty], fill='#aaa', width=1)
    ty += 10
    d.text((400, ty),      f'Sub Total  : Rs. {subtotal:,}',         font=font_small, fill='#333')
    d.text((400, ty + 26), f'GST ({inv["gst_pct"]}%) : Rs. {gst_amt:,}', font=font_small, fill='#333')

    d.rectangle([390, ty + 54, W - 40, ty + 84], fill='#2E4057')
    d.text((400, ty + 60), f'Total      : Rs. {total:,}',            font=font_small, fill='white')

    # Footer
    d.text((40, H - 60), 'Thank you for your business!', font=font_small, fill='#888')
    d.text((40, H - 38), 'GSTIN: 36AAABC1234D1ZX  |  PAN: AAABC1234D', font=font_small, fill='#aaa')

    return img


def main():
    import pdf2image
    # We'll save as high-res PNG (acts as mock PDF input for the extractor)
    for i, inv in enumerate(INVOICES, 1):
        img = make_invoice_image(inv)
        path = os.path.join(OUT, f'sample{i}.png')
        img.save(path, dpi=(300, 300))
        print(f'Created {path}')


if __name__ == '__main__':
    main()
