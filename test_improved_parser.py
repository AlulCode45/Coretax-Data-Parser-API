#!/usr/bin/env python3
"""
Test script untuk parser yang sudah diperbaiki
"""
import parser as pdf_parser
import json

# Test dengan sample PDF
pdf_file = 'sample_pdf/InputTaxInvoice-007704dc-6653-4c9e-b1d9-603814e7cac5-0021057187122000-04002500373856589-0637531807118000.pdf'

print("=" * 80)
print(f"Testing parser with: {pdf_file}")
print("=" * 80)

with open(pdf_file, 'rb') as f:
    content = f.read()
    result = pdf_parser.parse_pdf_file(content, 'test.pdf')

print("\n📋 METADATA:")
print(json.dumps(result.get('metadata', {}), indent=2, ensure_ascii=False))

print("\n📦 ITEMS:")
for item in result.get('items', []):
    print(f"\n  Item #{item['no']}: {item['nama_barang']}")
    print(f"    - Item Code: {item.get('item_code', 'N/A')}")
    print(f"    - Quantity: {item.get('quantity', 'N/A')} {item.get('unit', '')}")
    print(f"    - Unit Price: Rp {item.get('unit_price', 0):,.2f}")
    print(f"    - Discount: Rp {item.get('discount', 0):,.2f}")
    print(f"    - Total: Rp {item.get('total', 0):,.2f}")

print("\n✅ VALIDATION:")
validation = result.get('validation', {})
print(f"  Calculated Total: {validation.get('calculated_total_formatted', 'N/A')}")
print(f"  PDF Total: {validation.get('pdf_total_formatted', 'N/A')}")
print(f"  Is Valid: {validation.get('is_valid', False)}")
print(f"  Difference: {validation.get('difference_formatted', 'N/A')}")

print("\n" + "=" * 80)
print("FULL JSON OUTPUT:")
print("=" * 80)
print(json.dumps(result, indent=2, ensure_ascii=False))
