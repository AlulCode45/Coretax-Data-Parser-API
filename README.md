# Coretax Data Parser API

REST API untuk mengekstrak dan memvalidasi data faktur pajak dari file PDF Coretax. Aplikasi ini secara otomatis membaca item-item dalam faktur, menghitung total, dan memvalidasi apakah total kalkulasi sesuai dengan total yang tertera di PDF.

## 🚀 Fitur

- ✅ REST API dengan FastAPI
- ✅ Upload single atau multiple PDF files
- ✅ Ekstraksi data item dari PDF faktur pajak
- ✅ Parsing harga dan kuantitas dengan format Indonesia (Rp)
- ✅ Kalkulasi otomatis total dari semua item
- ✅ Validasi total kalkulasi vs total PDF
- ✅ Response dalam format JSON
- ✅ Error handling dan reporting
- ✅ Dokumentasi API otomatis (Swagger/OpenAPI)
- ✅ Support CLI mode untuk testing lokal

## 📋 Requirements

- Python 3.7+
- FastAPI
- uvicorn
- pdfplumber
- python-multipart
- tabulate (untuk CLI mode)

## 🔧 Instalasi

1. Clone atau download repository ini

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## 💻 Cara Penggunaan

### Mode 1: API Server (Production Mode)

#### Menjalankan API Server

```bash
python api.py
```

Atau menggunakan uvicorn langsung:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

API akan berjalan di `http://localhost:8000`

#### Akses Dokumentasi API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Endpoint API

1. **GET /** - Root endpoint

   ```bash
   curl http://localhost:8000/
   ```

2. **POST /parse** - Parse single PDF file

   ```bash
   curl -X POST "http://localhost:8000/parse" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@path/to/invoice.pdf"
   ```

3. **POST /parse-multiple** - Parse multiple PDF files

   ```bash
   curl -X POST "http://localhost:8000/parse-multiple" \
     -H "Content-Type: multipart/form-data" \
     -F "files=@path/to/invoice1.pdf" \
     -F "files=@path/to/invoice2.pdf" \
     -F "files=@path/to/invoice3.pdf"
   ```

4. **GET /health** - Health check

   ```bash
   curl http://localhost:8000/health
   ```

5. **GET /api-info** - Informasi detail API
   ```bash
   curl http://localhost:8000/api-info
   ```

#### Contoh Response JSON (Single File)

```json
{
  "status": "success",
  "filename": "invoice.pdf",
  "items": [
    {
      "no": 1,
      "nama_barang": "Item A",
      "total_raw": "1.500.000,00",
      "total": 1500000.0
    },
    {
      "no": 2,
      "nama_barang": "Item B",
      "total_raw": "2.300.000,00",
      "total": 2300000.0
    }
  ],
  "total_items": 2,
  "validation": {
    "calculated_total": 3800000.0,
    "calculated_total_formatted": "Rp 3.800.000,00",
    "pdf_total": 3800000.0,
    "pdf_total_formatted": "Rp 3.800.000,00",
    "is_valid": true,
    "difference": 0.0,
    "difference_formatted": "Rp 0,00"
  }
}
```

#### Contoh Response JSON (Multiple Files)

```json
{
  "status": "completed",
  "total_files": 3,
  "total_success": 2,
  "total_failed": 1,
  "results": [
    {
      "status": "success",
      "filename": "invoice1.pdf",
      "items": [...],
      "validation": {...}
    },
    {
      "status": "success",
      "filename": "invoice2.pdf",
      "items": [...],
      "validation": {...}
    },
    {
      "status": "error",
      "filename": "invoice3.pdf",
      "error": "Error message",
      "items": [],
      "validation": null
    }
  ]
}
```

### Mode 2: CLI (Command Line Interface)

#### Single File

Jalankan aplikasi CLI dan masukkan path ke file PDF:

```bash
python main.py
```

Kemudian masukkan path file PDF:

```
Masukkan path file PDF atau folder: /path/to/your/invoice.pdf
```

#### Batch Processing (Folder)

Untuk memproses banyak file sekaligus, masukkan path folder:

```bash
python main.py
```

```
Masukkan path file PDF atau folder: /path/to/your/sample_pdf/
```

## 📊 Output

Aplikasi akan menampilkan:

1. **Tabel Detail Item**
   - Nomor urut
   - Nama barang
   - Total harga per baris

2. **Ringkasan Total**
   - Total kalkulasi dari semua item
   - Total yang tertera di PDF
   - Status validasi (✅ COCOK atau ❌ TIDAK COCOK)

### Contoh Output

```
📄 MEMPROSES FILE: InputTaxInvoice-123456.pdf

+-----+------------------+---------------------+
| NO  | NAMA BARANG      | TOTAL BARIS (Rp)    |
+=====+==================+=====================+
| 1   | Item A           | 1,500,000.00        |
+-----+------------------+---------------------+
| 2   | Item B           | 2,300,000.00        |
+-----+------------------+---------------------+

TOTAL KALKULASI    Rp 3,800,000.00
TOTAL PDF          Rp 3,800,000.00
✅ STATUS: COCOK (VALID)
```

## 🏗️ Struktur Aplikasi

```
CoretaxDataParser-API/
├── api.py            # FastAPI application (REST API)
├── parser.py         # Core parser module (ekstraksi PDF)
├── main.py           # CLI application (command line)
├── requirements.txt  # Python dependencies
├── sample_pdf/       # Folder contoh berisi file PDF faktur
├── .gitignore        # Git ignore file
└── README.md         # Dokumentasi ini
```

## 🔍 Module Utama

### api.py

REST API server menggunakan FastAPI dengan endpoints:

- `/` - Root endpoint
- `/parse` - Parse single PDF
- `/parse-multiple` - Parse multiple PDFs
- `/health` - Health check
- `/api-info` - API information

### parser.py

Core parsing module dengan fungsi:

- `parse_pdf_file()` - Parse single PDF file
- `parse_multiple_pdfs()` - Parse multiple PDF files
- `extract_invoice_data()` - Ekstrak data dari PDF
- `clean_number()` - Helper untuk parsing angka
- `format_idr()` - Helper untuk format IDR

### main.py

CLI application untuk testing lokal dengan output tabel

## 🧪 Testing API

### Menggunakan curl

```bash
# Single file
curl -X POST "http://localhost:8000/parse" \
  -F "file=@sample_pdf/invoice.pdf"

# Multiple files
curl -X POST "http://localhost:8000/parse-multiple" \
  -F "files=@sample_pdf/invoice1.pdf" \
  -F "files=@sample_pdf/invoice2.pdf"
```

### Menggunakan Python requests

```python
import requests

# Single file
url = "http://localhost:8000/parse"
files = {'file': open('invoice.pdf', 'rb')}
response = requests.post(url, files=files)
print(response.json())

# Multiple files
url = "http://localhost:8000/parse-multiple"
files = [
    ('files', open('invoice1.pdf', 'rb')),
    ('files', open('invoice2.pdf', 'rb')),
    ('files', open('invoice3.pdf', 'rb'))
]
response = requests.post(url, files=files)
print(response.json())
```

### Menggunakan JavaScript (fetch)

```javascript
// Single file
const formData = new FormData();
formData.append("file", fileInput.files[0]);

fetch("http://localhost:8000/parse", {
  method: "POST",
  body: formData,
})
  .then((response) => response.json())
  .then((data) => console.log(data));

// Multiple files
const formData = new FormData();
for (let file of fileInput.files) {
  formData.append("files", file);
}

fetch("http://localhost:8000/parse-multiple", {
  method: "POST",
  body: formData,
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

## 🚀 Deployment

### Development

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Optional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📝 API Response Structure

### Success Response

```json
{
  "status": "success",
  "filename": "string",
  "items": [
    {
      "no": "number",
      "nama_barang": "string",
      "total_raw": "string",
      "total": "number"
    }
  ],
  "total_items": "number",
  "validation": {
    "calculated_total": "number",
    "calculated_total_formatted": "string",
    "pdf_total": "number",
    "pdf_total_formatted": "string",
    "is_valid": "boolean",
    "difference": "number",
    "difference_formatted": "string"
  }
}
```

### Error Response

```json
{
  "status": "error",
  "filename": "string",
  "error": "string",
  "items": [],
  "total_items": 0,
  "validation": null
}
```

## 🔐 Security Notes

- API tidak memiliki authentication (tambahkan jika diperlukan)
- Validasi file type dilakukan di endpoint
- Maximum file size perlu dikonfigurasi sesuai kebutuhan
- CORS perlu dikonfigurasi untuk production

## 📄 License

MIT License

## 👨‍💻 Author

Coretax Data Parser API v1.0.0

### `extract_invoice_with_validation(pdf_path)`

Ekstrak data invoice dari PDF dan validasi totalnya

- Parse tabel item dengan regex
- Ekstrak total dari summary PDF
- Bandingkan dan validasi

### `clean_number(num_str)`

Konversi string angka format Indonesia ke float

- Menghilangkan pemisah ribuan (.)
- Mengubah koma desimal (,) ke titik (.)

### `format_idr(number)`

Format angka ke format mata uang Rupiah

- Pemisah ribuan: titik (.)
- Pemisah desimal: koma (,)

### `process_path(path)`

Process single file atau batch folder

- Deteksi tipe input (file/folder)
- Iterasi semua PDF dalam folder

## ⚠️ Catatan

- Aplikasi dirancang khusus untuk format PDF Coretax
- Pastikan file PDF tidak terenkripsi atau memiliki proteksi
- Untuk file PDF yang error, aplikasi akan menampilkan pesan error tanpa menghentikan proses

## 🐛 Troubleshooting

**Error: "ModuleNotFoundError"**

- Install dependencies dengan `pip install pdfplumber tabulate`

**Error saat membaca PDF**

- Pastikan file PDF tidak corrupt
- Check apakah PDF memiliki password protection
- Pastikan format PDF sesuai dengan format Coretax

**Total tidak cocok**

- Check apakah ada item yang tidak ter-extract
- Periksa format angka di PDF
- Mungkin ada item tambahan yang tidak terbaca oleh regex

## 📝 License

Aplikasi ini dibuat untuk keperluan internal processing data faktur pajak.

## 👨‍💻 Author

Dibuat untuk mempermudah validasi dan ekstraksi data faktur pajak dari Coretax.

## 🔄 Update Log

- **v1.0.0** - Initial release dengan fitur ekstraksi dan validasi dasar
