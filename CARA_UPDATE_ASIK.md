# 🚀 Cara Update ASIK untuk Fitur Parser Baru

## ⚡ Quick Steps (5 menit)

### 1. Backup File Lama

```bash
cd /Users/user/Project/ASIK/app/Services
cp CoretaxParserService.php CoretaxParserService.php.backup-$(date +%Y%m%d)
```

### 2. Replace File

```bash
cp /Users/user/Project/CoretaxDataParser-API/CoretaxParserService-UPDATED.php /Users/user/Project/ASIK/app/Services/CoretaxParserService.php
```

### 3. Verifikasi

```bash
cd /Users/user/Project/ASIK
php artisan config:cache
php artisan route:cache
```

### 4. Test Import

1. Start API parser: `cd /Users/user/Project/CoretaxDataParser-API && uvicorn api:app --host 0.0.0.0 --port 8000 --reload`
2. Buka ASIK UI
3. Import tax invoice PDF
4. **Cek stok - harusnya sekarang sesuai quantity di PDF (bukan 1 lagi!)**

---

## 🎯 Apa yang Berubah?

### SEBELUM (v1.0):

```php
'stock' => 1,  // ❌ SELALU 1!
'unit_price' => 0,
'unit' => null,
// Metadata minim
```

### SESUDAH (v2.0):

```php
'stock' => (int) $quantity,  // ✅ Dari PDF! (150, 250, dll)
'unit_price' => $unitPrice,  // ✅ Harga satuan
'unit' => $item['unit'] ?? 'PCS',  // ✅ PCS, KG, dll
'discount' => $item['discount'] ?? 0,  // ✅ Diskon

// ✅ Metadata invoice lengkap:
'invoice_date' => $metadata['invoice_date'],
'supplier_name' => $metadata['supplier_name'],
'supplier_npwp' => $metadata['supplier_npwp'],
```

---

## 🔍 Validasi Sukses

Setelah import, cek database:

```sql
SELECT name, stock, unit_price, unit, supplier_name
FROM items
ORDER BY created_at DESC
LIMIT 5;
```

**Expected Result:**

- `stock` = angka dari PDF (bukan 1)
- `unit_price` > 0 (harga satuan)
- `unit` = PCS/KG/dll
- `supplier_name` terisi

---

## 🐛 Troubleshooting

### ❌ Stock masih 1

- Cek API parser running di port 8000
- Verify `$item['quantity']` di log Laravel
- Cek config: `php artisan config:clear`

### ❌ API timeout

- Check API health: `curl http://localhost:8000/health`
- Increase timeout di config: `services.coretax_parser.timeout`

### ❌ Field NULL

- Cek migration: `php artisan migrate:status`
- Add columns jika belum ada (opsional)

---

## 📋 Migration Database (Opsional)

Jika ingin simpan semua field baru:

```php
// database/migrations/xxxx_add_parser_v2_fields_to_items.php
Schema::table('items', function (Blueprint $table) {
    $table->decimal('unit_price', 15, 2)->nullable()->after('buy_price');
    $table->string('unit', 20)->nullable()->after('unit_price');
    $table->decimal('discount', 15, 2)->nullable()->after('unit');
    $table->date('invoice_date')->nullable()->after('tax_invoice_number');
    $table->string('supplier_name')->nullable()->after('invoice_date');
    $table->string('supplier_npwp', 50)->nullable()->after('supplier_name');
});
```

```bash
php artisan migrate
```

Jangan lupa update model:

```php
// app/Models/Item.php
protected $fillable = [
    // ... existing fields ...
    'unit_price',
    'unit',
    'discount',
    'invoice_date',
    'supplier_name',
    'supplier_npwp',
];
```

---

## 📞 Support

**File Dokumentasi:**

- 📄 `PERBAIKAN_PARSER_UNTUK_ASIK.md` - Changelog lengkap
- 📄 `PANDUAN_UPDATE_ASIK.md` - Panduan detail
- 📄 `CONTOH_RESPONSE.md` - Contoh response API

**Test Web Client:**

```bash
cd /Users/user/Project/CoretaxDataParser-API
./start-web-client.sh
```

Buka http://localhost:8000 untuk test parser.
