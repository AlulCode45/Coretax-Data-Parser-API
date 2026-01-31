# Coretax Data Parser

Aplikasi Python untuk mengekstrak dan memvalidasi data faktur pajak dari file PDF Coretax. Aplikasi ini secara otomatis membaca item-item dalam faktur, menghitung total, dan memvalidasi apakah total kalkulasi sesuai dengan total yang tertera di PDF.

## 🚀 Fitur

- ✅ Ekstraksi data item dari PDF faktur pajak
- ✅ Parsing harga dan kuantitas dengan format Indonesia (Rp)
- ✅ Kalkulasi otomatis total dari semua item
- ✅ Validasi total kalkulasi vs total PDF
- ✅ Support single file atau batch processing (folder)
- ✅ Output dalam format tabel yang mudah dibaca
- ✅ Error handling dan reporting

## 📋 Requirements

- Python 3.7+
- pdfplumber
- tabulate

## 🔧 Instalasi

1. Clone atau download repository ini

2. Install dependencies:

```bash
pip install pdfplumber tabulate
```

## 💻 Cara Penggunaan

### Single File

Jalankan aplikasi dan masukkan path ke file PDF:

```bash
python main.py
```

Kemudian masukkan path file PDF:

```
Masukkan path file PDF atau folder: /path/to/your/invoice.pdf
```

### Batch Processing (Folder)

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
CoretaxDataParser/
├── main.py           # File utama aplikasi
├── sample_pdf/       # Folder contoh berisi file PDF faktur
└── README.md         # Dokumentasi ini
```

## 🔍 Fungsi Utama

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
