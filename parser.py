"""
Coretax Invoice Parser Module
Ekstraksi dan validasi data faktur pajak dari PDF Coretax
"""
import pdfplumber
import re
from typing import Dict, List, Any
from io import BytesIO


def clean_number(num_str: str) -> float:
    """
    Membersihkan dan mengkonversi string angka format Indonesia ke float
    
    Args:
        num_str: String angka dengan format Indonesia (contoh: "1.500.000,00")
    
    Returns:
        Float hasil konversi
    """
    if not num_str:
        return 0.0
    num_str = num_str.replace('.', '').replace(',', '.')
    try:
        return float(num_str)
    except ValueError:
        return 0.0


def format_idr(number: float) -> str:
    """
    Format angka ke format mata uang Indonesia
    
    Args:
        number: Angka yang akan diformat
    
    Returns:
        String dengan format IDR (contoh: "1.500.000,00")
    """
    return f"{number:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def extract_invoice_metadata(full_text: str) -> Dict[str, Any]:
    """
    Ekstrak metadata invoice dari teks PDF
    
    Args:
        full_text: Teks lengkap dari PDF
    
    Returns:
        Dictionary berisi metadata invoice
    """
    metadata = {
        "invoice_number": None,
        "invoice_date": None,
        "supplier_name": None,
        "supplier_npwp": None,
        "buyer_name": None,
        "buyer_npwp": None
    }
    
    # Ekstrak nomor faktur
    invoice_match = re.search(r'Kode dan Nomor Seri Faktur Pajak:\s*(\d+)', full_text)
    if invoice_match:
        metadata["invoice_number"] = invoice_match.group(1)
    
    # Ekstrak tanggal faktur (format: DD Month YYYY atau DD-MM-YYYY)
    date_patterns = [
        r'(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})',
        r'(\d{1,2}-\d{1,2}-\d{4})',
        r'(\d{1,2}/\d{1,2}/\d{4})'
    ]
    for pattern in date_patterns:
        date_match = re.search(pattern, full_text)
        if date_match:
            metadata["invoice_date"] = date_match.group(1)
            break
    
    # Ekstrak informasi supplier (Pengusaha Kena Pajak)
    supplier_section = re.search(r'Pengusaha Kena Pajak:.*?Nama\s*:\s*([^\n]+).*?NPWP\s*:\s*(\d+)', full_text, re.DOTALL)
    if supplier_section:
        metadata["supplier_name"] = supplier_section.group(1).strip()
        metadata["supplier_npwp"] = supplier_section.group(2).strip()
    
    # Ekstrak informasi buyer (Pembeli BKP/JKP)
    buyer_section = re.search(r'Pembeli Barang Kena Pajak.*?Nama\s*:\s*([^\n]+).*?NPWP\s*:\s*(\d+)', full_text, re.DOTALL)
    if buyer_section:
        metadata["buyer_name"] = buyer_section.group(1).strip()
        metadata["buyer_npwp"] = buyer_section.group(2).strip()
    
    return metadata


def extract_invoice_data(pdf_file: BytesIO, filename: str = "invoice.pdf") -> Dict[str, Any]:
    """
    Ekstrak data invoice dari PDF dan kembalikan sebagai dictionary
    
    Args:
        pdf_file: BytesIO object berisi data PDF
        filename: Nama file untuk referensi
    
    Returns:
        Dictionary berisi data invoice yang sudah diekstrak
    """
    items_list = []
    pdf_summary_total = 0.0
    metadata = {}
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            full_text = ""
            
            # Ekstrak teks dan tabel dari semua halaman
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            
            # Ekstrak metadata invoice
            metadata = extract_invoice_metadata(full_text)
            
            # Process tables untuk ekstrak items
            for page in pdf.pages:
                table = page.extract_table()
                if not table:
                    continue
                
                # Proses setiap baris dalam tabel
                for row in table:
                    if not row or len(row) < 4:
                        continue
                    
                    # Skip header dan non-item rows
                    if not row[0] or not str(row[0]).strip().isdigit():
                        continue
                    
                    item_no = str(row[0]).strip()
                    item_code = str(row[1]).strip() if row[1] else "000000"
                    item_detail = str(row[2]).strip() if row[2] else ""
                    total_col = str(row[3]).strip() if row[3] else "0"
                    
                    # Pattern untuk mendeteksi item barang dengan harga, quantity dan unit
                    # Format: NAMA BARANG\nRp HARGA x QUANTITY UNIT
                    pattern = r"(.*?)Rp\s+([\d\.,]+)\s+[x×]\s+([\d\.,]+)\s+(\w+)"
                    match = re.search(pattern, item_detail, re.DOTALL)
                    
                    if match:
                        raw_name = match.group(1).strip()
                        unit_price = clean_number(match.group(2))
                        quantity = clean_number(match.group(3))
                        unit = match.group(4).strip()
                        
                        # Bersihkan nama item
                        clean_name = re.sub(r'\d{6}', '', raw_name)
                        clean_name = re.sub(
                            r'Potongan Harga.*|PPnBM.*|^\d+\s+',
                            '',
                            clean_name,
                            flags=re.DOTALL
                        )
                        clean_name = " ".join(clean_name.split()).strip()
                        
                        # Ekstrak discount jika ada
                        discount = 0.0
                        discount_match = re.search(r'Potongan Harga\s*=\s*Rp\s+([\d\.,]+)', item_detail)
                        if discount_match:
                            discount = clean_number(discount_match.group(1))
                        
                        items_list.append({
                            "no": len(items_list) + 1,
                            "item_code": item_code,
                            "nama_barang": clean_name or "Detail Item",
                            "quantity": quantity,
                            "unit": unit,
                            "unit_price": unit_price,
                            "unit_price_formatted": f"Rp {format_idr(unit_price)}",
                            "discount": discount,
                            "discount_formatted": f"Rp {format_idr(discount)}",
                            "total_raw": total_col,
                            "total": clean_number(total_col),
                            "total_formatted": f"Rp {format_idr(clean_number(total_col))}"
                        })
            
            # Ekstrak total dari summary PDF
            # Ekstrak total dari summary PDF
            total_match = re.search(
                r'Harga Jual / Penggantian / Uang Muka / Termin\s+([\d\.,]+)',
                full_text
            )
            if total_match:
                pdf_summary_total = clean_number(total_match.group(1))
        
        # Hitung total kalkulasi
        calculated_sum = sum(item['total'] for item in items_list)
        
        # Validasi
        is_valid = abs(calculated_sum - pdf_summary_total) < 1.0
        selisih = abs(calculated_sum - pdf_summary_total)
        
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
                "difference": selisih,
                "difference_formatted": f"Rp {format_idr(selisih)}"
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
    """
    Parse single PDF file dari bytes
    
    Args:
        file_content: Binary content dari file PDF
        filename: Nama file
    
    Returns:
        Dictionary hasil parsing
    """
    pdf_file = BytesIO(file_content)
    return extract_invoice_data(pdf_file, filename)


def parse_multiple_pdfs(files: List[tuple]) -> Dict[str, Any]:
    """
    Parse multiple PDF files
    
    Args:
        files: List of tuples (filename, file_content)
    
    Returns:
        Dictionary berisi hasil parsing semua file
    """
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
