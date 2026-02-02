# 🌐 Web Client - Cara Penggunaan

## 📋 Overview

Web client telah diupdate untuk menampilkan semua data baru dari parser v2.0, termasuk:

- ✅ Invoice metadata (invoice number, date, supplier)
- ✅ Quantity/Stock untuk setiap item
- ✅ Unit price dan unit (satuan)
- ✅ Item code dan discount

## 🚀 Cara Menggunakan

### 1. Start API Server

Pastikan API server sudah berjalan:

```bash
cd /Users/user/Project/CoretaxDataParser-API
uvicorn api:app --host 0.0.0.0 --port 9000 --reload
```

**Note:** Port default di web_client.html adalah **9000** (sesuai ASIK). Jika API Anda berjalan di port lain, edit baris ini di web_client.html:

```javascript
const API_URL = "http://localhost:9000"; // Ubah sesuai port Anda
```

### 2. Buka Web Client

Ada 2 cara:

**Cara 1: Buka langsung di browser**

```bash
open web_client.html
# Atau double-click file web_client.html
```

**Cara 2: Via HTTP server (recommended untuk avoid CORS)**

```bash
# Python 3
python3 -m http.server 8080

# Kemudian buka browser:
# http://localhost:8080/web_client.html
```

### 3. Upload PDF

1. **Pilih file:**
   - Klik tombol "Pilih File"
   - Atau drag & drop PDF ke area upload

2. **Multiple files:**
   - Anda bisa memilih beberapa PDF sekaligus
   - Klik "Upload & Parse" untuk memproses

3. **Lihat hasil:**
   - Hasil akan muncul di bawah tombol
   - Scroll ke bawah untuk melihat detail

## 📊 Tampilan Data Baru

### Invoice Metadata (Baru! 🆕)

Sekarang ditampilkan dalam card terpisah:

- Invoice Number
- Invoice Date
- Supplier Name
- Supplier NPWP
- Buyer Name
- Buyer NPWP

### Items Table (Enhanced! ✨)

Kolom baru yang ditambahkan:

- **Item Code** - Kode barang dari PDF
- **Qty** 🆕 - Quantity/Stock (PENTING!)
- **Unit** 🆕 - Satuan (PCS, KG, dll)
- **Unit Price** 🆕 - Harga per unit
- **Discount** 🆕 - Potongan harga

### Validation Summary (Tetap Ada)

- Calculated Total
- PDF Total
- Difference
- Validation Status

## 🎨 Fitur UI

### 1. API Status Indicator

Di bagian atas ada indikator status API:

- ✅ **Hijau (Online)** - API siap digunakan
- ❌ **Merah (Offline)** - API tidak tersedia

Status di-check otomatis setiap 10 detik.

### 2. Drag & Drop Support

Anda bisa drag & drop PDF langsung ke area upload - tidak perlu klik "Pilih File".

### 3. File Management

- Lihat daftar file yang dipilih
- Hapus file individual sebelum upload
- Lihat ukuran file

### 4. Loading Indicator

Spinner muncul saat processing PDF.

### 5. Responsive Design

UI menyesuaikan dengan ukuran layar (mobile-friendly).

## 🔍 Contoh Tampilan

### Before v2.0

```
Items Table:
┌────┬──────────────┬────────────┐
│ No │ Nama Barang  │ Total      │
├────┼──────────────┼────────────┤
│ 1  │ LENCANA      │ 23,331,081 │
└────┴──────────────┴────────────┘
```

### After v2.0 ✨

```
Invoice Metadata:
┌────────────────────┬──────────────────────┐
│ Invoice Number     │ 04002500373856589    │
│ Date               │ 06 November 2025     │
│ Supplier           │ SAUDARA PRATAMA      │
└────────────────────┴──────────────────────┘

Items Table:
┌────┬───────┬──────────────┬─────┬─────┬────────────┬──────────┬────────────┐
│ No │ Code  │ Nama Barang  │ Qty │ Unit│ Unit Price │ Discount │ Total      │
├────┼───────┼──────────────┼─────┼─────┼────────────┼──────────┼────────────┤
│ 1  │000000 │ LENCANA      │ 150 │Lain │ 155,540.54 │4,617,117 │ 23,331,081 │
└────┴───────┴──────────────┴─────┴─────┴────────────┴──────────┴────────────┘
```

## 🔧 Troubleshooting

### Issue: API Status Offline

**Solusi:**

1. Pastikan API server berjalan: `curl http://localhost:9000/health`
2. Cek port di web_client.html match dengan API server
3. Restart API server jika perlu

### Issue: CORS Error di Console

**Solusi:**
Buka web_client.html via HTTP server:

```bash
python3 -m http.server 8080
```

Kemudian akses via: http://localhost:8080/web_client.html

### Issue: Data Tidak Muncul

**Penyebab:** Parser API belum diupdate atau masih versi lama

**Solusi:**

1. Pastikan file `parser.py` sudah diupdate dengan versi terbaru
2. Restart API server
3. Test dengan sample PDF

### Issue: Metadata Kosong

Jika metadata tidak muncul, kemungkinan:

- Format PDF berbeda
- Parser gagal extract metadata
- Data memang tidak ada di PDF

Parser akan tetap berfungsi meski metadata kosong (graceful fallback).

## 📝 Customization

### Ubah Port API

Edit di web_client.html:

```javascript
const API_URL = "http://localhost:8000"; // Ubah ke port Anda
```

### Ubah Warna Tema

Edit CSS di bagian `<style>`:

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
/* Ganti dengan warna favorit Anda */
```

### Hide/Show Kolom

Untuk hide kolom tertentu, edit bagian tabel:

```javascript
// Contoh: Hide item_code
// Hapus atau comment baris ini:
html += `<th>Item Code</th>`;
```

## 🎯 Testing

### Test dengan Sample PDF

```bash
# 1. Start API
cd /Users/user/Project/CoretaxDataParser-API
uvicorn api:app --host 0.0.0.0 --port 9000 --reload

# 2. Buka web client
open web_client.html

# 3. Upload sample PDF dari folder sample_pdf/
```

### Expected Result

1. ✅ API Status: Online (hijau)
2. ✅ Metadata card muncul dengan data invoice
3. ✅ Items table menampilkan quantity, unit price, dll
4. ✅ Validation summary menunjukkan "VALID"

## 📖 Related Documentation

- [PERBAIKAN_PARSER_UNTUK_ASIK.md](PERBAIKAN_PARSER_UNTUK_ASIK.md) - Full changelog
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference
- [CONTOH_RESPONSE.md](CONTOH_RESPONSE.md) - Response examples
- [PANDUAN_UPDATE_ASIK.md](PANDUAN_UPDATE_ASIK.md) - ASIK integration guide

## 🎓 Tips

1. **Use Chrome/Firefox** - Better developer tools
2. **Open DevTools (F12)** - Monitor API calls dan errors
3. **Test incrementally** - Upload 1 PDF dulu, baru multiple files
4. **Check Network tab** - Lihat request/response dari API
5. **Use sample PDFs** - Test dengan PDF di folder sample_pdf/

---

**Version:** 2.0.0  
**Last Updated:** 2 February 2026  
**Status:** ✅ Ready to use
