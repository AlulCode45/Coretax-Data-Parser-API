# Quick Start Guide - Coretax Data Parser API

## 🚀 Panduan Cepat Memulai

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Jalankan API Server

```bash
python api.py
```

Atau menggunakan uvicorn:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di: **http://localhost:8000**

### 3. Akses Dokumentasi API

- **Swagger UI (Interactive Docs)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Info**: http://localhost:8000/api-info

### 4. Testing API

#### Opsi A: Web Client (Browser)

1. Buka file `web_client.html` di browser Anda
2. Pastikan API server sudah berjalan
3. Upload file PDF dan lihat hasilnya secara real-time

#### Opsi B: Python Test Script

```bash
python test_api.py
```

Script ini akan otomatis test semua endpoint dan memproses file PDF di folder `sample_pdf/`

#### Opsi C: cURL

**Single File:**

```bash
curl -X POST "http://localhost:8000/parse" \
  -F "file=@sample_pdf/invoice.pdf"
```

**Multiple Files:**

```bash
curl -X POST "http://localhost:8000/parse-multiple" \
  -F "files=@sample_pdf/invoice1.pdf" \
  -F "files=@sample_pdf/invoice2.pdf"
```

#### Opsi D: Postman / Thunder Client

Import endpoint berikut:

```
POST http://localhost:8000/parse
Body: form-data
Key: file
Value: [pilih file PDF]

POST http://localhost:8000/parse-multiple
Body: form-data
Key: files (multiple files)
Value: [pilih beberapa file PDF]
```

### 5. CLI Mode (Original)

Untuk testing lokal dengan output tabel di terminal:

```bash
python main.py
```

Masukkan path file atau folder yang berisi PDF.

## 📊 Response Format

### Success Response

```json
{
  "status": "success",
  "filename": "invoice.pdf",
  "items": [
    {
      "no": 1,
      "nama_barang": "Item Name",
      "total_raw": "1.500.000,00",
      "total": 1500000.0
    }
  ],
  "total_items": 1,
  "validation": {
    "calculated_total": 1500000.0,
    "calculated_total_formatted": "Rp 1.500.000,00",
    "pdf_total": 1500000.0,
    "pdf_total_formatted": "Rp 1.500.000,00",
    "is_valid": true,
    "difference": 0.0,
    "difference_formatted": "Rp 0,00"
  }
}
```

## 🔧 Troubleshooting

### API tidak bisa diakses

- Pastikan port 8000 tidak digunakan aplikasi lain
- Cek firewall settings
- Pastikan semua dependencies sudah terinstall

### Web Client tidak bisa connect ke API

- Pastikan API server sudah berjalan
- Cek CORS settings di `api.py`
- Buka browser console untuk melihat error messages

### Error parsing PDF

- Pastikan file adalah PDF yang valid
- Cek apakah format PDF sesuai dengan format Coretax
- Lihat error message di response JSON

## 📁 File Structure

```
CoretaxDataParser-API/
├── api.py              # FastAPI server (REST API)
├── parser.py           # Core parsing logic
├── main.py             # CLI application
├── test_api.py         # API testing script
├── web_client.html     # Web-based client
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore file
├── README.md          # Full documentation
├── QUICKSTART.md      # This file
└── sample_pdf/        # Sample PDF files
```

## 🎯 Next Steps

1. ✅ Upload PDF files melalui web client atau API
2. ✅ Integrate dengan aplikasi Anda
3. ✅ Customize parsing logic sesuai kebutuhan
4. ✅ Deploy ke production server
5. ✅ Add authentication jika diperlukan

## 💡 Tips

- Gunakan web client untuk testing cepat
- Gunakan Swagger UI untuk eksplorasi API
- Gunakan CLI mode untuk batch processing
- Check API logs untuk debugging

## 📞 Support

Untuk informasi lebih lanjut, baca dokumentasi lengkap di `README.md`
