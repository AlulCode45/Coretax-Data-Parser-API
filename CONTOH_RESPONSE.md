# Contoh Response API - Before & After

## 📋 Contoh PDF yang Diparse

**File:** InputTaxInvoice-007704dc-6653-4c9e-b1d9-603814e7cac5.pdf

**Isi PDF:**

- Supplier: SAUDARA PRATAMA (NPWP: 0021057187122000)
- Buyer: ANUGERAH TEMAN SETIA (NPWP: 0637531807118000)
- Invoice #: 04002500373856589
- Tanggal: 06 November 2025

**Items:**

1. LENCANA MERAH - Rp 155,540.54 × 150 = Rp 23,331,081 (Discount: Rp 4,617,117)
2. CAKRA KEMBAR - Rp 201,801.80 × 250 = Rp 50,450,450

---

## ❌ SEBELUM PERBAIKAN (v1.0.0)

### Request

```bash
curl -X POST "http://localhost:9000/parse" \
  -F "file=@InputTaxInvoice-007704dc.pdf"
```

### Response

```json
{
  "status": "success",
  "filename": "InputTaxInvoice-007704dc.pdf",
  "items": [
    {
      "no": 1,
      "nama_barang": "LENCANA MERAH",
      "total_raw": "23.331.081,00",
      "total": 23331081.0
    },
    {
      "no": 2,
      "nama_barang": "CAKRA KEMBAR",
      "total_raw": "50.450.450,00",
      "total": 50450450.0
    }
  ],
  "total_items": 2,
  "validation": {
    "calculated_total": 73781531.0,
    "calculated_total_formatted": "Rp 73.781.531,00",
    "pdf_total": 73781531.0,
    "pdf_total_formatted": "Rp 73.781.531,00",
    "is_valid": true,
    "difference": 0.0,
    "difference_formatted": "Rp 0,00"
  }
}
```

### Masalah dalam Response Lama

❌ **Tidak ada `metadata`** - Invoice number, date, supplier hilang  
❌ **Tidak ada `item_code`** - Kode barang tidak ada  
❌ **Tidak ada `quantity`** - Stock tidak bisa dihitung (default jadi 1)  
❌ **Tidak ada `unit`** - Satuan tidak tercatat  
❌ **Tidak ada `unit_price`** - Harga satuan tidak ada  
❌ **Tidak ada `discount`** - Potongan harga tidak tercatat

---

## ✅ SETELAH PERBAIKAN (v2.0.0)

### Request

```bash
curl -X POST "http://localhost:9000/parse" \
  -F "file=@InputTaxInvoice-007704dc.pdf"
```

### Response

```json
{
  "status": "success",
  "filename": "InputTaxInvoice-007704dc.pdf",
  "metadata": {
    "invoice_number": "04002500373856589",
    "invoice_date": "06 November 2025",
    "supplier_name": "SAUDARA PRATAMA",
    "supplier_npwp": "0021057187122000",
    "buyer_name": "ANUGERAH TEMAN SETIA",
    "buyer_npwp": "0637531807118000"
  },
  "items": [
    {
      "no": 1,
      "item_code": "000000",
      "nama_barang": "LENCANA MERAH",
      "quantity": 150.0,
      "unit": "Lainnya",
      "unit_price": 155540.54,
      "unit_price_formatted": "Rp 155.540,54",
      "discount": 4617117.0,
      "discount_formatted": "Rp 4.617.117,00",
      "total_raw": "23.331.081,00",
      "total": 23331081.0,
      "total_formatted": "Rp 23.331.081,00"
    },
    {
      "no": 2,
      "item_code": "000000",
      "nama_barang": "CAKRA KEMBAR",
      "quantity": 250.0,
      "unit": "Lainnya",
      "unit_price": 201801.8,
      "unit_price_formatted": "Rp 201.801,80",
      "discount": 0.0,
      "discount_formatted": "Rp 0,00",
      "total_raw": "50.450.450,00",
      "total": 50450450.0,
      "total_formatted": "Rp 50.450.450,00"
    }
  ],
  "total_items": 2,
  "validation": {
    "calculated_total": 73781531.0,
    "calculated_total_formatted": "Rp 73.781.531,00",
    "pdf_total": 73781531.0,
    "pdf_total_formatted": "Rp 73.781.531,00",
    "is_valid": true,
    "difference": 0.0,
    "difference_formatted": "Rp 0,00"
  }
}
```

### Keunggulan Response Baru

✅ **Ada `metadata`** - Semua info invoice lengkap  
✅ **Ada `item_code`** - Kode barang dari PDF  
✅ **Ada `quantity`** - **PENTING! Stock = 150 dan 250, bukan 1**  
✅ **Ada `unit`** - Satuan tercatat  
✅ **Ada `unit_price`** - Harga satuan tersedia  
✅ **Ada `discount`** - Potongan harga tercatat  
✅ **Ada `_formatted` fields** - Format rupiah untuk display

---

## 📊 Perbandingan Field by Field

| Field                          | Sebelum      | Sesudah                   | Keterangan               |
| ------------------------------ | ------------ | ------------------------- | ------------------------ |
| `metadata`                     | ❌ Tidak ada | ✅ Ada                    | Invoice info lengkap     |
| `metadata.invoice_number`      | ❌           | ✅ "04002500373856589"    | Dari PDF, bukan filename |
| `metadata.invoice_date`        | ❌           | ✅ "06 November 2025"     | Tanggal faktur           |
| `metadata.supplier_name`       | ❌           | ✅ "SAUDARA PRATAMA"      | Nama supplier            |
| `metadata.supplier_npwp`       | ❌           | ✅ "0021057187122000"     | NPWP supplier            |
| `metadata.buyer_name`          | ❌           | ✅ "ANUGERAH TEMAN SETIA" | Nama pembeli             |
| `metadata.buyer_npwp`          | ❌           | ✅ "0637531807118000"     | NPWP pembeli             |
| `items[].item_code`            | ❌           | ✅ "000000"               | Kode barang              |
| `items[].quantity`             | ❌           | ✅ 150.0                  | **Quantity = Stock!**    |
| `items[].unit`                 | ❌           | ✅ "Lainnya"              | Satuan                   |
| `items[].unit_price`           | ❌           | ✅ 155540.54              | Harga per unit           |
| `items[].unit_price_formatted` | ❌           | ✅ "Rp 155.540,54"        | Format display           |
| `items[].discount`             | ❌           | ✅ 4617117.0              | Potongan harga           |
| `items[].discount_formatted`   | ❌           | ✅ "Rp 4.617.117,00"      | Format display           |
| `items[].total_formatted`      | ❌           | ✅ "Rp 23.331.081,00"     | Format display           |

---

## 🎯 Impact pada ASIK

### Item 1: LENCANA MERAH

#### Sebelum

```php
[
  'name' => 'LENCANA MERAH',
  'buy_price' => 23331081,
  'stock' => 1,  // ❌ SALAH! Harusnya 150
  'tax_invoice_number' => '007704dc',  // ❌ Dari filename
]
```

#### Sesudah

```php
[
  'name' => 'LENCANA MERAH',
  'item_code' => '000000',
  'buy_price' => 23331081,
  'unit_price' => 155540.54,  // ✅ BARU!
  'stock' => 150,  // ✅ BENAR!
  'unit' => 'Lainnya',  // ✅ BARU!
  'discount' => 4617117,  // ✅ BARU!
  'tax_invoice_number' => '04002500373856589',  // ✅ Akurat!
  'invoice_date' => '06 November 2025',  // ✅ BARU!
  'supplier_name' => 'SAUDARA PRATAMA',  // ✅ BARU!
]
```

### Item 2: CAKRA KEMBAR

#### Sebelum

```php
[
  'name' => 'CAKRA KEMBAR',
  'buy_price' => 50450450,
  'stock' => 1,  // ❌ SALAH! Harusnya 250
  'tax_invoice_number' => '007704dc',  // ❌ Dari filename
]
```

#### Sesudah

```php
[
  'name' => 'CAKRA KEMBAR',
  'item_code' => '000000',
  'buy_price' => 50450450,
  'unit_price' => 201801.80,  // ✅ BARU!
  'stock' => 250,  // ✅ BENAR!
  'unit' => 'Lainnya',  // ✅ BARU!
  'discount' => 0,  // ✅ BARU!
  'tax_invoice_number' => '04002500373856589',  // ✅ Akurat!
  'invoice_date' => '06 November 2025',  // ✅ BARU!
  'supplier_name' => 'SAUDARA PRATAMA',  // ✅ BARU!
]
```

---

## 🔄 Multiple Files Response

### Request

```bash
curl -X POST "http://localhost:9000/parse-multiple" \
  -F "files=@invoice1.pdf" \
  -F "files=@invoice2.pdf"
```

### Response

```json
{
  "status": "completed",
  "total_files": 2,
  "total_success": 2,
  "total_failed": 0,
  "results": [
    {
      "status": "success",
      "filename": "invoice1.pdf",
      "metadata": { ... },
      "items": [ ... ],
      "total_items": 2,
      "validation": { ... }
    },
    {
      "status": "success",
      "filename": "invoice2.pdf",
      "metadata": { ... },
      "items": [ ... ],
      "total_items": 3,
      "validation": { ... }
    }
  ]
}
```

---

## 🧪 Testing Scenarios

### Scenario 1: Simple Item

```
PDF: "Laptop ASUS Rp 10.000.000,00 x 5,00 PCS"
```

**Response:**

```json
{
  "nama_barang": "Laptop ASUS",
  "quantity": 5.0,
  "unit": "PCS",
  "unit_price": 10000000.0,
  "total": 50000000.0
}
```

### Scenario 2: With Discount

```
PDF: "Monitor LG Rp 2.500.000,00 x 10,00 PCS"
      "Potongan Harga = Rp 500.000,00"
```

**Response:**

```json
{
  "nama_barang": "Monitor LG",
  "quantity": 10.0,
  "unit": "PCS",
  "unit_price": 2500000.0,
  "discount": 500000.0,
  "total": 24500000.0
}
```

### Scenario 3: Different Units

```
PDF: "Beras Premium Rp 15.000,00 x 500,00 KG"
```

**Response:**

```json
{
  "nama_barang": "Beras Premium",
  "quantity": 500.0,
  "unit": "KG",
  "unit_price": 15000.0,
  "total": 7500000.0
}
```

---

## 📝 Notes

- Response tetap **backward compatible** - field lama masih ada
- Field `_formatted` untuk display, raw number untuk kalkulasi
- Metadata bisa `null` jika tidak bisa diextract dari PDF
- Item code "000000" adalah generic code, bisa di-override
- Quantity menggunakan format desimal (150.0, bukan 150)

---

**Version:** 2.0.0  
**Date:** 2 February 2026
