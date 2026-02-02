# 🔄 Panduan Update Integrasi ASIK dengan Parser API yang Diperbaiki

## 📋 Langkah-Langkah Update

### Step 1: Backup File yang Akan Diubah

```bash
cd /Users/user/Project/ASIK
cp app/Services/CoretaxParserService.php app/Services/CoretaxParserService.php.backup
```

### Step 2: Update Method `processItems()`

Edit file: `/Users/user/Project/ASIK/app/Services/CoretaxParserService.php`

**Cari method ini:**

```php
private function processItems(array $result, float $margin): array
{
    $items = [];
    $filename = $result['filename'] ?? 'unknown.pdf';

    foreach ($result['items'] as $item) {
        $buyPrice = $item['total'] ?? 0;
        $sellPrice = $buyPrice + ($buyPrice * $margin / 100);
        $profit = $sellPrice - $buyPrice;

        $items[] = [
            'item' => [
                'name' => $item['nama_barang'] ?? 'Unknown Item',
                'buy_price' => $buyPrice,
                'margin' => $margin,
                'sell_price' => $sellPrice,
                'profit' => $profit,
                'stock' => 1, // Default stock 1
                'initial_stock' => 1,
                'original_tax_invoice_file_name' => $filename,
                'tax_invoice_number' => $this->extractInvoiceNumber($filename),
                'is_free_ppn' => false,
                'item_code' => null, // Will be generated later
            ]
        ];
    }

    return $items;
}
```

**Ganti dengan method yang diperbaiki:**

```php
private function processItems(array $result, float $margin): array
{
    $items = [];
    $filename = $result['filename'] ?? 'unknown.pdf';
    $metadata = $result['metadata'] ?? [];

    // Extract invoice number dari metadata (lebih akurat) atau filename
    $invoiceNumber = $metadata['invoice_number'] ?? $this->extractInvoiceNumber($filename);

    foreach ($result['items'] as $item) {
        // 🎯 PERUBAHAN 1: Gunakan unit_price dan quantity dari PDF
        $unitPrice = $item['unit_price'] ?? 0;
        $quantity = $item['quantity'] ?? 1;
        $buyPrice = $item['total'] ?? ($unitPrice * $quantity);

        // Hitung harga jual dengan margin
        $sellPrice = $buyPrice + ($buyPrice * $margin / 100);
        $profit = $sellPrice - $buyPrice;

        // 🎯 PERUBAHAN 2: Gunakan item_code dari PDF jika ada
        $itemCode = $item['item_code'] ?? null;
        if ($itemCode === '000000' || empty($itemCode)) {
            $itemCode = null; // Biarkan system generate jika generic code
        }

        $items[] = [
            'item' => [
                'name' => $item['nama_barang'] ?? 'Unknown Item',
                'item_code' => $itemCode,
                'buy_price' => $buyPrice,
                'margin' => $margin,
                'sell_price' => $sellPrice,
                'profit' => $profit,

                // 🎯 PERUBAHAN 3: Stock menggunakan quantity dari PDF!
                'stock' => (int) $quantity,
                'initial_stock' => (int) $quantity,

                // 🎯 PERUBAHAN 4: Informasi tambahan dari parser baru
                'unit_price' => $unitPrice,
                'unit' => $item['unit'] ?? 'PCS',
                'discount' => $item['discount'] ?? 0,

                // 🎯 PERUBAHAN 5: Invoice metadata yang lebih lengkap
                'original_tax_invoice_file_name' => $filename,
                'tax_invoice_number' => $invoiceNumber,
                'invoice_date' => $metadata['invoice_date'] ?? null,
                'supplier_name' => $metadata['supplier_name'] ?? null,
                'supplier_npwp' => $metadata['supplier_npwp'] ?? null,

                'is_free_ppn' => false,
            ]
        ];
    }

    return $items;
}
```

### Step 3: (Optional) Update Database Migration untuk Field Baru

Jika ingin menyimpan informasi tambahan, tambahkan kolom ke tabel items:

```bash
cd /Users/user/Project/ASIK
php artisan make:migration add_extended_fields_to_items_table
```

Edit migration file yang baru dibuat:

```php
public function up(): void
{
    Schema::table('items', function (Blueprint $table) {
        $table->string('unit')->nullable()->after('stock');
        $table->decimal('unit_price', 15, 2)->nullable()->after('buy_price');
        $table->decimal('discount', 15, 2)->default(0)->after('unit_price');
        $table->string('invoice_date')->nullable()->after('tax_invoice_number');
        $table->string('supplier_name')->nullable()->after('invoice_date');
        $table->string('supplier_npwp')->nullable()->after('supplier_name');
    });
}

public function down(): void
{
    Schema::table('items', function (Blueprint $table) {
        $table->dropColumn([
            'unit',
            'unit_price',
            'discount',
            'invoice_date',
            'supplier_name',
            'supplier_npwp'
        ]);
    });
}
```

Jalankan migration:

```bash
php artisan migrate
```

### Step 4: Update Model (Optional)

Edit `/Users/user/Project/ASIK/app/Models/Item.php`:

```php
protected $fillable = [
    'uuid',
    'db_uuid',
    'item_code',
    'type_item',
    'name',
    'stock',
    'buy_price',
    'margin',
    'sell_price',
    'profit',
    // Field baru
    'unit',
    'unit_price',
    'discount',
    'original_tax_invoice_file_name',
    'tax_invoice_number',
    'invoice_date',
    'supplier_name',
    'supplier_npwp',
];

protected $casts = [
    'stock' => 'integer',
    'buy_price' => 'decimal:2',
    'unit_price' => 'decimal:2',
    'discount' => 'decimal:2',
    'margin' => 'decimal:2',
    'sell_price' => 'decimal:2',
    'profit' => 'decimal:2',
];
```

### Step 5: Restart Services

```bash
# Restart API Parser
cd /Users/user/Project/CoretaxDataParser-API
uvicorn api:app --host 0.0.0.0 --port 9000 --reload &

# Restart Laravel (jika pakai serve)
cd /Users/user/Project/ASIK
php artisan serve --port 8000
```

### Step 6: Test Import

1. Buka browser: http://localhost:8000/dashboard/items
2. Klik "Import Items"
3. Pilih "API Parser (Coretax)"
4. Upload 1-2 PDF untuk test
5. Submit

**Expected Result:**

- Items diimport dengan stock sesuai quantity di PDF
- Unit price tersedia
- Invoice number akurat (dari metadata PDF, bukan filename)

## 🔍 Verifikasi Update Berhasil

### Test 1: Cek Stock Tidak Lagi Default 1

**Sebelum:**

- Semua item import dengan stock = 1

**Sesudah:**

- Item dengan quantity 150 di PDF → stock = 150
- Item dengan quantity 250 di PDF → stock = 250

### Test 2: Cek Invoice Number Lebih Akurat

**Sebelum:**

- Invoice number: "007704dc" (dari filename)

**Sesudah:**

- Invoice number: "04002500373856589" (dari PDF)

### Test 3: Cek Data Tambahan Tersimpan

Query database:

```sql
SELECT name, stock, unit_price, unit, discount, invoice_date, supplier_name
FROM items
WHERE tax_invoice_number = '04002500373856589'
LIMIT 1;
```

Expected result:

```
name: "LENCANA MERAH"
stock: 150
unit_price: 155540.54
unit: "Lainnya"
discount: 4617117.00
invoice_date: "06 November 2025"
supplier_name: "SAUDARA PRATAMA"
```

## 📊 Perbandingan Before/After

### Before Update

**Import 2 items dari PDF:**

```
Item 1: LENCANA MERAH
- Stock: 1 ❌ (seharusnya 150)
- Buy Price: 23,331,081 ✅
- Invoice: "007704dc" ❌ (dari filename)

Item 2: CAKRA KEMBAR
- Stock: 1 ❌ (seharusnya 250)
- Buy Price: 50,450,450 ✅
- Invoice: "007704dc" ❌ (dari filename)
```

### After Update

**Import 2 items dari PDF:**

```
Item 1: LENCANA MERAH
- Stock: 150 ✅ (dari quantity di PDF)
- Unit Price: 155,540.54 ✅
- Unit: Lainnya ✅
- Buy Price: 23,331,081 ✅
- Discount: 4,617,117 ✅
- Invoice: "04002500373856589" ✅ (dari metadata PDF)
- Date: "06 November 2025" ✅
- Supplier: "SAUDARA PRATAMA" ✅

Item 2: CAKRA KEMBAR
- Stock: 250 ✅ (dari quantity di PDF)
- Unit Price: 201,801.80 ✅
- Unit: Lainnya ✅
- Buy Price: 50,450,450 ✅
- Discount: 0 ✅
- Invoice: "04002500373856589" ✅
- Date: "06 November 2025" ✅
- Supplier: "SAUDARA PRATAMA" ✅
```

## 🎯 Manfaat Update

### 1. Stock Management Akurat

- Stock otomatis sesuai quantity di faktur
- Tidak perlu manual update stock setelah import
- Inventory tracking lebih presisi

### 2. Harga Detail Tersedia

- Unit price untuk kalkulasi margin
- Discount tercatat untuk analisis
- Buy price total tetap tersimpan

### 3. Invoice Tracking Lengkap

- Nomor invoice akurat dari PDF
- Tanggal invoice untuk laporan
- Info supplier untuk referensi

### 4. Data Lebih Kaya

- Satuan barang (unit) tersedia
- Item code dari PDF (jika ada)
- Metadata lengkap untuk audit

## 🐛 Troubleshooting

### Issue: Stock masih 1 setelah import

**Solusi:**

1. Cek API response: `curl http://localhost:9000/parse -F "file=@path/to/test.pdf"`
2. Pastikan response punya field `quantity`
3. Cek log Laravel untuk error
4. Pastikan method `processItems()` sudah diupdate

### Issue: Unit price = 0

**Penyebab:** PDF format berbeda atau parser gagal extract unit price

**Solusi:**

- Fallback ke total price tetap ada
- Cek manual PDF apakah ada format "Rp X x Y Unit"

### Issue: Invoice number masih dari filename

**Penyebab:** Metadata extraction gagal

**Solusi:**

1. Cek API response punya field `metadata.invoice_number`
2. Fallback ke filename tetap ada jika metadata kosong

## 📝 Rollback (Jika Diperlukan)

Jika ada masalah, restore backup:

```bash
cd /Users/user/Project/ASIK
cp app/Services/CoretaxParserService.php.backup app/Services/CoretaxParserService.php
php artisan config:clear
php artisan cache:clear
```

## ✅ Post-Update Checklist

- [ ] Method `processItems()` sudah diupdate
- [ ] API Parser sudah restart dengan versi baru
- [ ] Test import 1 PDF berhasil
- [ ] Stock tidak lagi default 1
- [ ] Invoice number akurat (bukan dari filename)
- [ ] Migration dijalankan (jika update database)
- [ ] Model fillable sudah update (jika update database)
- [ ] Test import multiple PDF berhasil
- [ ] Data tersimpan lengkap di database
- [ ] UI menampilkan data dengan benar

## 📞 Support

Jika ada masalah:

1. Cek file backup di: `app/Services/CoretaxParserService.php.backup`
2. Cek log: `tail -f storage/logs/laravel.log`
3. Test API: `curl http://localhost:9000/health`
4. Lihat contoh response di: `/Users/user/Project/CoretaxDataParser-API/PERBAIKAN_PARSER_UNTUK_ASIK.md`

---

**Version:** 2.0.0  
**Last Updated:** 2 February 2026  
**Author:** GitHub Copilot
