#!/usr/bin/env python3
"""
Invoice OCR Extractor — CLI
Usage:
    python main.py invoice.pdf
    python main.py invoices/              # process entire folder
    python main.py invoice.png --out custom_output.xlsx
"""

import sys
import os
import argparse
from extractor import process_file, save_to_excel


def collect_files(path):
    supported = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    if os.path.isfile(path):
        return [path]
    elif os.path.isdir(path):
        files = []
        for f in sorted(os.listdir(path)):
            if os.path.splitext(f)[1].lower() in supported:
                files.append(os.path.join(path, f))
        return files
    else:
        print(f"Error: '{path}' is not a valid file or directory.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Extract invoice data to Excel.')
    parser.add_argument('input', help='PDF/image file or folder of invoices')
    parser.add_argument('--out', default='output/extracted.xlsx',
                        help='Output Excel path (default: output/extracted.xlsx)')
    args = parser.parse_args()

    files = collect_files(args.input)
    if not files:
        print("No supported files found.")
        sys.exit(1)

    print(f"Processing {len(files)} file(s)...\n")
    data_list = []
    for f in files:
        print(f"  → {f}")
        try:
            data = process_file(f)
            data_list.append(data)
            print(f"     Invoice: {data['invoice_no']}  |  Date: {data['date']}  |  Total: {data['total']}")
        except Exception as e:
            print(f"     [ERROR] {e}")

    if data_list:
        save_to_excel(data_list, out=args.out)
    else:
        print("No data extracted.")


if __name__ == '__main__':
    main()
