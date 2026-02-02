# 🚀 Quick Reference - Parser API Improvements

## 📋 What Changed

### Old Parser Response

```json
{
  "items": [
    {
      "no": 1,
      "nama_barang": "LENCANA MERAH",
      "total": 23331081.0
    }
  ]
}
```

### New Parser Response

```json
{
  "metadata": {
    "invoice_number": "04002500373856589",
    "invoice_date": "06 November 2025",
    "supplier_name": "SAUDARA PRATAMA",
    "supplier_npwp": "0021057187122000"
  },
  "items": [
    {
      "no": 1,
      "item_code": "000000",
      "nama_barang": "LENCANA MERAH",
      "quantity": 150.0,
      "unit": "Lainnya",
      "unit_price": 155540.54,
      "discount": 4617117.0,
      "total": 23331081.0
    }
  ]
}
```

## 🎯 Key New Fields

| Field        | Type   | Description                | Example          |
| ------------ | ------ | -------------------------- | ---------------- |
| `metadata`   | Object | Invoice metadata           | See below        |
| `item_code`  | String | Item SKU from PDF          | "000000"         |
| `quantity`   | Float  | **Stock/Qty** (IMPORTANT!) | 150.0            |
| `unit`       | String | Unit of measurement        | "PCS", "Lainnya" |
| `unit_price` | Float  | Price per unit             | 155540.54        |
| `discount`   | Float  | Discount amount            | 4617117.0        |

### Metadata Fields

| Field            | Type   | Example                |
| ---------------- | ------ | ---------------------- |
| `invoice_number` | String | "04002500373856589"    |
| `invoice_date`   | String | "06 November 2025"     |
| `supplier_name`  | String | "SAUDARA PRATAMA"      |
| `supplier_npwp`  | String | "0021057187122000"     |
| `buyer_name`     | String | "ANUGERAH TEMAN SETIA" |
| `buyer_npwp`     | String | "0637531807118000"     |

## 🔧 Update ASIK Service

**File:** `/Users/user/Project/ASIK/app/Services/CoretaxParserService.php`

**Key Changes in `processItems()`:**

```php
// 1. Extract metadata
$metadata = $result['metadata'] ?? [];
$invoiceNumber = $metadata['invoice_number'] ?? $this->extractInvoiceNumber($filename);

// 2. Use unit_price and quantity
$unitPrice = $item['unit_price'] ?? 0;
$quantity = $item['quantity'] ?? 1;

// 3. Set stock from quantity (NOT default 1!)
'stock' => (int) $quantity,
'initial_stock' => (int) $quantity,

// 4. Add new fields
'unit_price' => $unitPrice,
'unit' => $item['unit'] ?? 'PCS',
'discount' => $item['discount'] ?? 0,
'invoice_date' => $metadata['invoice_date'] ?? null,
'supplier_name' => $metadata['supplier_name'] ?? null,
```

## ✅ Testing

### Test Parser API

```bash
cd /Users/user/Project/CoretaxDataParser-API
python3 test_improved_parser.py
```

### Test API Endpoint

```bash
curl -X POST "http://localhost:9000/parse" \
  -F "file=@sample_pdf/InputTaxInvoice-xxx.pdf"
```

### Expected Output

```json
{
  "status": "success",
  "metadata": { ... },
  "items": [
    {
      "quantity": 150.0,
      "unit_price": 155540.54,
      "unit": "Lainnya"
    }
  ]
}
```

## 🐛 Common Issues

### Stock still = 1

❌ Old code: `'stock' => 1`  
✅ Fix: `'stock' => (int) $quantity`

### Invoice number from filename

❌ Old: `$this->extractInvoiceNumber($filename)`  
✅ Fix: `$metadata['invoice_number'] ?? $this->extractInvoiceNumber($filename)`

### Missing unit_price

✅ Has fallback: `$item['unit_price'] ?? 0`

## 📂 Files Modified

### Parser API

- ✅ `/Users/user/Project/CoretaxDataParser-API/parser.py`
- ✅ `/Users/user/Project/CoretaxDataParser-API/test_improved_parser.py`
- ✅ `/Users/user/Project/CoretaxDataParser-API/PERBAIKAN_PARSER_UNTUK_ASIK.md`
- ✅ `/Users/user/Project/CoretaxDataParser-API/PANDUAN_UPDATE_ASIK.md`

### ASIK (Needs Update)

- ⚠️ `/Users/user/Project/ASIK/app/Services/CoretaxParserService.php` (processItems method)
- 📖 Reference: `/Users/user/Project/CoretaxDataParser-API/IMPROVED_SERVICE_METHOD.php`

## 🚀 Deployment Steps

1. **Backup:**

   ```bash
   cp app/Services/CoretaxParserService.php app/Services/CoretaxParserService.php.backup
   ```

2. **Update `processItems()` method** with new code

3. **Restart API:**

   ```bash
   cd /Users/user/Project/CoretaxDataParser-API
   uvicorn api:app --host 0.0.0.0 --port 9000 --reload
   ```

4. **Test import** via ASIK UI

5. **Verify stock** is not 1 anymore

## 📞 Quick Help

| Problem            | Solution                                              |
| ------------------ | ----------------------------------------------------- |
| API not responding | Check: `curl http://localhost:9000/health`            |
| Stock = 1          | Update `processItems()` method                        |
| No metadata        | Parser API needs restart                              |
| Import fails       | Check Laravel log: `tail -f storage/logs/laravel.log` |

## 📊 Impact

### Before

- ❌ Stock always = 1
- ❌ No unit price
- ❌ Invoice # from filename
- ❌ No supplier info

### After

- ✅ Stock = actual quantity
- ✅ Unit price available
- ✅ Invoice # from PDF
- ✅ Full supplier metadata

---

**Version:** 2.0.0 | **Date:** 2 Feb 2026
