#!/usr/bin/env python3
"""
Script untuk update items.blade.php dengan field baru dari parser v2.0
"""

import re
import sys

def update_items_blade():
    blade_file = '/Users/user/Project/ASIK/resources/views/dashboard/items.blade.php'
    
    print("📖 Reading items.blade.php...")
    with open(blade_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Tambah field di form input (setelah stock field)
    print("\n1️⃣ Menambahkan field input form...")
    stock_field_pattern = r'(</small>\s*</div>\s*<div class="form-group mt-2">\s*<label for="price">Harga Beli)'
    
    new_fields = '''</small>
                        </div>
                        <div class="form-group mt-2">
                            <label for="unit">Satuan</label>
                            <input type="text" class="form-control" id="unit" name="unit"
                                value="{{ old('unit', 'PCS') }}" placeholder="PCS, KG, LITER, dll">
                            <small class="text-muted">Satuan barang (PCS, KG, LITER, dll)</small>
                        </div>
                        <div class="form-group mt-2">
                            <label for="unit_price">Harga Satuan</label>
                            <div class="input-group mb-2">
                                <span class="input-group-text">Rp.</span>
                                <input type="text" class="form-control" id="unit_price" name="unit_price"
                                    placeholder="Harga per satuan" value="{{ old('unit_price') }}">
                            </div>
                            <small class="text-muted">Harga per satuan (otomatis terisi dari parser)</small>
                        </div>
                        <div class="form-group mt-2">
                            <label for="discount">Diskon</label>
                            <div class="input-group mb-2">
                                <span class="input-group-text">Rp.</span>
                                <input type="text" class="form-control" id="discount" name="discount"
                                    placeholder="Diskon" value="{{ old('discount', 0) }}">
                            </div>
                            <small class="text-muted">Total diskon dari invoice</small>
                        </div>
                        <div class="form-group mt-2">
                            <label for="invoice_date">Tanggal Invoice</label>
                            <input type="date" class="form-control" id="invoice_date" name="invoice_date"
                                value="{{ old('invoice_date') }}">
                            <small class="text-muted">Tanggal dari tax invoice</small>
                        </div>
                        <div class="form-group mt-2">
                            <label for="price">Harga Beli'''
    
    if 'id="unit"' not in content:
        content = re.sub(stock_field_pattern, new_fields, content)
        print("   ✅ Form input fields ditambahkan")
    else:
        print("   ⚠️  Form input fields sudah ada")
    
    # 2. Tambah table header columns
    print("\n2️⃣ Menambahkan kolom header table...")
    if '<th>Satuan</th>' not in content:
        # Cari header NPWP Supplier dan tambahkan setelahnya
        header_pattern = r'(<th>NPWP Supplier</th>)'
        new_headers = r'\1\n                                        <th>Satuan</th>\n                                        <th>Harga Satuan</th>\n                                        <th>Diskon</th>\n                                        <th>Tgl Invoice</th>'
        content = re.sub(header_pattern, new_headers, content)
        print("   ✅ Table headers ditambahkan")
    else:
        print("   ⚠️  Table headers sudah ada")
    
    # 3. Tambah DataTables columns
    print("\n3️⃣ Menambahkan DataTables columns...")
    if "data: 'unit'" not in content:
        # Cari supplier_npwp column dan tambahkan setelahnya
        datatable_pattern = r"({\s*data: 'supplier_npwp',\s*name: 'supplier_npwp'\s*},)"
        
        new_columns = r"""\1
                    {
                        data: 'unit',
                        name: 'unit',
                        defaultContent: 'PCS'
                    },
                    {
                        data: 'unit_price',
                        name: 'unit_price',
                        render: function(data) {
                            if (!data) return '-';
                            return 'Rp. ' + Number(data).toLocaleString('id-ID', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            });
                        }
                    },
                    {
                        data: 'discount',
                        name: 'discount',
                        render: function(data) {
                            if (!data || data == 0) return '-';
                            return 'Rp. ' + Number(data).toLocaleString('id-ID', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            });
                        }
                    },
                    {
                        data: 'invoice_date',
                        name: 'invoice_date',
                        render: function(data) {
                            if (!data) return '-';
                            return new Date(data).toLocaleDateString('id-ID');
                        }
                    },"""
        
        content = re.sub(datatable_pattern, new_columns, content, flags=re.DOTALL)
        print("   ✅ DataTables columns ditambahkan")
    else:
        print("   ⚠️  DataTables columns sudah ada")
    
    # 4. Tambah edit modal fields
    print("\n4️⃣ Menambahkan edit modal fields...")
    if 'id="edit-unit"' not in content:
        # Cari edit-stock field dan tambahkan setelahnya
        edit_pattern = r'(<input type="number"[^>]*id="edit-stock"[^>]*>[\s\S]*?</div>)'
        
        edit_fields = r'''\1
                        <div class="form-group mt-2">
                            <label for="edit-unit">Satuan</label>
                            <input type="text" class="form-control" id="edit-unit" name="unit">
                        </div>
                        <div class="form-group mt-2">
                            <label for="edit-unit-price">Harga Satuan</label>
                            <input type="text" class="form-control" id="edit-unit-price" name="unit_price">
                        </div>
                        <div class="form-group mt-2">
                            <label for="edit-discount">Diskon</label>
                            <input type="text" class="form-control" id="edit-discount" name="discount">
                        </div>
                        <div class="form-group mt-2">
                            <label for="edit-invoice-date">Tanggal Invoice</label>
                            <input type="date" class="form-control" id="edit-invoice-date" name="invoice_date">
                        </div>'''
        
        content = re.sub(edit_pattern, edit_fields, content)
        print("   ✅ Edit modal fields ditambahkan")
    else:
        print("   ⚠️  Edit modal fields sudah ada")
    
    # 5. Tambah data attributes di edit button
    print("\n5️⃣ Menambahkan data attributes...")
    if 'data-unit=' not in content:
        # Cari pattern edit button dan tambahkan attributes
        button_pattern = r'(data-stock="\$\{row\.stock\}")'
        new_attrs = r'''\1
                        data-unit="${row.unit || 'PCS'}"
                        data-unit-price="${row.unit_price || ''}"
                        data-discount="${row.discount || 0}"
                        data-invoice-date="${row.invoice_date || ''}"'''
        
        content = re.sub(button_pattern, new_attrs, content)
        print("   ✅ Data attributes ditambahkan")
    else:
        print("   ⚠️  Data attributes sudah ada")
    
    # 6. Tambah modal population code
    print("\n6️⃣ Menambahkan modal population code...")
    if "data('unit')" not in content:
        # Cari pattern $('#edit-stock').val dan tambahkan setelahnya
        modal_pattern = r"(\$\('#edit-stock'\)\.val\(stock\);)"
        
        modal_code = r"""\1
                const unit = button.data('unit');
                const unitPrice = button.data('unit-price');
                const discount = button.data('discount');
                const invoiceDate = button.data('invoice-date');
                
                $('#edit-unit').val(unit);
                $('#edit-unit-price').val(unitPrice);
                $('#edit-discount').val(discount);
                $('#edit-invoice-date').val(invoiceDate);"""
        
        content = re.sub(modal_pattern, modal_code, content)
        print("   ✅ Modal population code ditambahkan")
    else:
        print("   ⚠️  Modal population code sudah ada")
    
    # Cek apakah ada perubahan
    if content == original_content:
        print("\n⚠️  Tidak ada perubahan yang dilakukan (mungkin sudah ter-update)")
        return False
    
    # Backup dan save
    print("\n💾 Menyimpan perubahan...")
    backup_file = blade_file + '.backup-v1'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original_content)
    print(f"   ✅ Backup: {backup_file}")
    
    with open(blade_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"   ✅ Updated: {blade_file}")
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("🔧 UPDATE ITEMS.BLADE.PHP - Parser v2.0")
    print("=" * 60)
    
    try:
        updated = update_items_blade()
        
        print("\n" + "=" * 60)
        if updated:
            print("✅ ITEMS.BLADE.PHP BERHASIL DIUPDATE!")
        else:
            print("ℹ️  FILE SUDAH UP-TO-DATE")
        print("=" * 60)
        
        print("\n🎯 Field baru yang ditambahkan:")
        print("   • Satuan (unit) - PCS, KG, LITER, dll")
        print("   • Harga Satuan (unit_price)")
        print("   • Diskon (discount)")
        print("   • Tanggal Invoice (invoice_date)")
        
        print("\n📋 Yang perlu dilakukan selanjutnya:")
        print("   1. Refresh halaman items di browser")
        print("   2. Test import tax invoice")
        print("   3. Cek apakah field baru muncul di tabel")
        print("   4. Verify stock menggunakan quantity dari PDF")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
