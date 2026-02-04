"""
Coretax Invoice Parser Module - Ultra Robust Version
Deskripsi: Ekstraksi data Faktur Pajak Coretax dari PDF.
Fitur Unggulan: 
1. Penanganan Multiline (teks terpisah baris).
2. Penanganan Multiple Items (No 8 & 9 dalam satu sel).
3. Snap Tolerance tinggi untuk menangani spasi/gap antar baris.
4. Validasi kalkulasi otomatis.
"""

import pdfplumber
import re
from typing import Dict, List, Any
from io import BytesIO


def clean_number(num_str: str) -> float:
    """Membersihkan dan mengkonversi string angka format Indonesia ke float"""
    if not num_str:
        return 0.0
    # Menghilangkan titik ribuan dan mengubah koma desimal menjadi titik
    num_str = str(num_str).replace('.', '').replace(',', '.')
    try:
        return float(num_str)
    except ValueError:
        return 0.0


def format_idr(number: float) -> str:
    """Format angka ke format mata uang Indonesia (Contoh: 1.500.000,00)"""
    return f"{number:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def extract_invoice_metadata(full_text: str) -> Dict[str, Any]:
    """Ekstrak metadata invoice (Nomor, Tanggal, Supplier, Pembeli)"""
    metadata = {
        "invoice_number": None,
        "invoice_date": None,
        "supplier_name": None,
        "supplier_npwp": None,
        "buyer_name": None,
        "buyer_npwp": None
    }
    
    # 1. Kode dan Nomor Seri Faktur Pajak
    invoice_match = re.search(r'(?:Kode dan )?Nomor Seri Faktur Pajak:\s*(\d+)', full_text)
    if invoice_match:
        metadata["invoice_number"] = invoice_match.group(1)
    
    # 2. Tanggal Faktur (Contoh: 17 Januari 2025)
    date_match = re.search(r'(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})', full_text)
    if date_match:
        metadata["invoice_date"] = date_match.group(1)
    
    # 3. Informasi Supplier (Pengusaha Kena Pajak)
    supplier_section = re.search(r'Pengusaha Kena Pajak:.*?Nama\s*:\s*([^\n]+).*?NPWP\s*:\s*([\d\.-]+)', full_text, re.DOTALL)
    if supplier_section:
        metadata["supplier_name"] = supplier_section.group(1).strip()
        metadata["supplier_npwp"] = supplier_section.group(2).replace('.', '').replace('-', '').strip()
    
    # 4. Informasi Pembeli (Buyer)
    buyer_section = re.search(r'Pembeli Barang Kena Pajak.*?Nama\s*:\s*([^\n]+).*?NPWP\s*:\s*([\d\.-]+)', full_text, re.DOTALL)
    if buyer_section:
        metadata["buyer_name"] = buyer_section.group(1).strip()
        metadata["buyer_npwp"] = buyer_section.group(2).replace('.', '').replace('-', '').strip()
    
    return metadata


def process_item_buffer(buffer: dict) -> List[dict]:
    """
    Memproses buffer teks item untuk mengekstrak data barang.
    Sangat krusial untuk memisahkan item 8 dan 9 yang sering menumpuk di satu sel.
    """
    extracted = []
    # Bersihkan detail_text dari newline agar Regex tidak terputus
    detail_text = " ".join(buffer["detail"].split())
    
    # Pattern Utama: Nama Barang + Rp Harga x Qty Unit
    # Lookahead (?=Potongan Harga|PPnBM|Rp|$) memastikan pemisahan antar item jika menumpuk
    pattern = r"(.*?)Rp\s+([\d\.,]+)\s+[x×]\s+([\d\.,]+)\s+([\w\s/]+?)(?=Potongan Harga|PPnBM|Rp|$)"
    matches = list(re.finditer(pattern, detail_text, re.IGNORECASE))
    
    # Memecah nomor urut, kode, dan total yang mungkin menumpuk (split by newline/space)
    no_lines = [n.strip() for n in buffer["no"].split() if n.strip()]
    code_lines = [c.strip() for c in buffer["code"].split() if c.strip()]
    total_lines = [t.strip() for t in buffer["total_col"].split() if t.strip()]
    
    # Mencari semua Potongan Harga dalam buffer ini
    discount_pattern = r"Potongan Harga\s*(?:=)?\s*Rp\s+([\d\.,]+)"
    discounts_found = re.findall(discount_pattern, detail_text)
    
    for i, match in enumerate(matches):
        raw_name = match.group(1).strip()
        unit_price = clean_number(match.group(2))
        quantity = clean_number(match.group(3))
        unit = match.group(4).strip()
        
        # Bersihkan nama dari sisa-sisa angka nomor urut di awal string
        clean_name = re.sub(r'^\d+\s+', '', raw_name)
        clean_name = " ".join(clean_name.split()).strip()

        # Ambil data pendukung berdasarkan urutan temuan (index i)
        current_no = no_lines[i] if i < len(no_lines) else (no_lines[-1] if no_lines else "0")
        current_code = code_lines[i] if i < len(code_lines) else (code_lines[-1] if code_lines else "000000")
        current_discount = clean_number(discounts_found[i]) if i < len(discounts_found) else 0.0
        current_total_raw = total_lines[i] if i < len(total_lines) else "0"
        
        extracted.append({
            "no": current_no,
            "item_code": current_code,
            "nama_barang": clean_name or "Detail Item",
            "quantity": quantity,
            "unit": unit,
            "unit_price": unit_price,
            "unit_price_formatted": f"Rp {format_idr(unit_price)}",
            "discount": current_discount,
            "discount_formatted": f"Rp {format_idr(current_discount)}",
            "total": clean_number(current_total_raw),
            "total_formatted": f"Rp {format_idr(clean_number(current_total_raw))}"
        })
    return extracted


def extract_invoice_data(pdf_file: BytesIO, filename: str = "invoice.pdf") -> Dict[str, Any]:
    """Fungsi utama untuk mengekstrak data dari PDF ke Dictionary"""
    items_list = []
    pdf_summary_total = 0.0
    metadata = {}
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += (page.extract_text() or "") + "\n"
            
            # Ekstrak Metadata
            metadata = extract_invoice_metadata(full_text)
            
            # Pengolahan Tabel per Halaman
            for page in pdf.pages:
                table = page.extract_table({
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "snap_tolerance": 5, # Toleransi ditingkatkan untuk mengatasi space lebar/garis tebal
                })
                
                if not table: continue

                current_buffer = None

                for row in table:
                    if not row or len(row) < 4: continue
                    
                    # Ambil data mentah per kolom
                    no_val = str(row[0] or "").strip()
                    code_val = str(row[1] or "").strip()
                    detail_val = str(row[2] or "").strip()
                    total_val = str(row[3] or "").strip()

                    # Cek apakah ini awal item baru (kolom No berisi angka)
                    is_start = any(c.isdigit() for c in no_val) and len(no_val) < 10

                    if is_start:
                        # Jika ada item sebelumnya yang menggantung, proses dulu
                        if current_buffer:
                            items_list.extend(process_item_buffer(current_buffer))
                        
                        current_buffer = {
                            "no": no_val,
                            "code": code_val,
                            "detail": detail_val,
                            "total_col": total_val
                        }
                    elif current_buffer:
                        # Baris lanjutan (multiline/space), gabungkan ke buffer yang aktif
                        if no_val: current_buffer["no"] += "\n" + no_val
                        if code_val: current_buffer["code"] += "\n" + code_val
                        if detail_val: current_buffer["detail"] += "\n" + detail_val
                        if total_val: current_buffer["total_col"] += "\n" + total_val

                # Simpan buffer terakhir di setiap halaman
                if current_buffer:
                    items_list.extend(process_item_buffer(current_buffer))
            
            # Ekstrak Total DPP dari teks summary (bawah tabel)
            total_match = re.search(r'Harga Jual / Penggantian / Uang Muka / Termin\s+([\d\.,]+)', full_text)
            if total_match:
                pdf_summary_total = clean_number(total_match.group(1))

        # Kalkulasi Total dari semua item yang ditemukan
        calculated_sum = sum(item['total'] for item in items_list)
        is_valid = abs(calculated_sum - pdf_summary_total) < 2.0
        
        return {
            "status": "success",
            "filename": filename,
            "metadata": metadata,
            "items": items_list,
            "total_items": len(items_list),
            "validation": {
                "calculated_total": calculated_sum,
                "calculated_total_formatted": f"Rp {format_idr(calculated_sum)}",
                "pdf_total": pdf_summary_total,
                "pdf_total_formatted": f"Rp {format_idr(pdf_summary_total)}",
                "is_valid": is_valid,
                "difference": abs(calculated_sum - pdf_summary_total),
                "difference_formatted": f"Rp {format_idr(abs(calculated_sum - pdf_summary_total))}"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "filename": filename,
            "error": str(e),
            "metadata": {},
            "items": [],
            "total_items": 0,
            "validation": None
        }


def parse_pdf_file(file_content: bytes, filename: str) -> Dict[str, Any]:
    """Wrapper untuk memproses satu file PDF dari bytes"""
    return extract_invoice_data(BytesIO(file_content), filename)


def parse_multiple_pdfs(files: List[tuple]) -> Dict[str, Any]:
    """Wrapper untuk memproses banyak file sekaligus"""
    results = []
    total_success = 0
    total_failed = 0
    
    for filename, file_content in files:
        result = parse_pdf_file(file_content, filename)
        results.append(result)
        if result["status"] == "success":
            total_success += 1
        else:
            total_failed += 1
    
    return {
        "status": "completed",
        "total_files": len(files),
        "total_success": total_success,
        "total_failed": total_failed,
        "results": results
    }