import pdfplumber
import re
import os
from tabulate import tabulate

def clean_number(num_str):
    if not num_str:
        return 0.0
    num_str = num_str.replace('.', '').replace(',', '.')
    try:
        return float(num_str)
    except ValueError:
        return 0.0

def format_idr(number):
    return f"{number:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def extract_invoice_with_validation(pdf_path):
    items_list = []
    pdf_summary_total = 0.0

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""

            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

                table = page.extract_table()
                if not table:
                    continue

                for row in table:
                    row_content = " ".join([str(c) for c in row[:-1] if c])
                    total_col = row[-1].strip() if row[-1] else "0"

                    pattern = r"(.*?)Rp\s+([\d\.,]+)\s+[x×]\s+([\d\.,]+)\s+(\w+)"
                    matches = re.finditer(pattern, row_content, re.DOTALL)

                    for match in matches:
                        raw_name = match.group(1).strip()

                        clean_name = re.sub(r'\d{6}', '', raw_name)
                        clean_name = re.sub(
                            r'Potongan Harga.*|PPnBM.*|^\d+\s+',
                            '',
                            clean_name,
                            flags=re.DOTALL
                        )
                        clean_name = " ".join(clean_name.split()).strip()

                        items_list.append([
                            len(items_list) + 1,
                            clean_name or "Detail Item",
                            total_col
                        ])

            total_match = re.search(
                r'Harga Jual / Penggantian / Uang Muka / Termin\s+([\d\.,]+)',
                full_text
            )
            if total_match:
                pdf_summary_total = clean_number(total_match.group(1))

        calculated_sum = sum(clean_number(item[2]) for item in items_list)

        print("\n" + tabulate(items_list,
            headers=["NO", "NAMA BARANG", "TOTAL BARIS (Rp)"],
            tablefmt="grid"
        ))

        summary_data = [
            ["TOTAL KALKULASI", f"Rp {format_idr(calculated_sum)}"],
            ["TOTAL PDF", f"Rp {format_idr(pdf_summary_total)}"]
        ]

        print("\n" + tabulate(summary_data, tablefmt="plain"))

        if abs(calculated_sum - pdf_summary_total) < 1.0:
            print("✅ STATUS: COCOK (VALID)")
        else:
            selisih = abs(calculated_sum - pdf_summary_total)
            print(f"❌ STATUS: TIDAK COCOK (Selisih Rp {format_idr(selisih)})")

    except Exception as e:
        print(f"❌ Error di file {os.path.basename(pdf_path)}: {e}")

def process_path(path):
    if os.path.isfile(path) and path.lower().endswith(".pdf"):
        print(f"\n📄 MEMPROSES FILE: {os.path.basename(path)}")
        extract_invoice_with_validation(path)

    elif os.path.isdir(path):
        pdf_files = [
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.lower().endswith(".pdf")
        ]

        if not pdf_files:
            print("⚠️ Tidak ada file PDF di folder.")
            return

        for pdf in pdf_files:
            print(f"\n📄 MEMPROSES FILE: {os.path.basename(pdf)}")
            extract_invoice_with_validation(pdf)

    else:
        print("❌ Path tidak valid atau bukan PDF/folder.")

# ===============================
# MAIN
# ===============================
path = input("Masukkan path file PDF atau folder: ").strip()
process_path(path)

