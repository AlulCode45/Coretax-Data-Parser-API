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
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            full_text = ""
            
            # Ekstrak teks dan tabel dari semua halaman
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
                
                table = page.extract_table()
                if not table:
                    continue
                
                # Proses setiap baris dalam tabel
                for row in table:
                    row_content = " ".join([str(c) for c in row[:-1] if c])
                    total_col = row[-1].strip() if row[-1] else "0"
                    
                    # Pattern untuk mendeteksi item barang
                    pattern = r"(.*?)Rp\s+([\d\.,]+)\s+[x×]\s+([\d\.,]+)\s+(\w+)"
                    matches = re.finditer(pattern, row_content, re.DOTALL)
                    
                    for match in matches:
                        raw_name = match.group(1).strip()
                        
                        # Bersihkan nama item
                        clean_name = re.sub(r'\d{6}', '', raw_name)
                        clean_name = re.sub(
                            r'Potongan Harga.*|PPnBM.*|^\d+\s+',
                            '',
                            clean_name,
                            flags=re.DOTALL
                        )
                        clean_name = " ".join(clean_name.split()).strip()
                        
                        items_list.append({
                            "no": len(items_list) + 1,
                            "nama_barang": clean_name or "Detail Item",
                            "total_raw": total_col,
                            "total": clean_number(total_col)
                        })
            
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
