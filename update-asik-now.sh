#!/bin/bash

echo "🔄 Updating ASIK CoretaxParserService..."

# Backup
echo "📦 Creating backup..."
cp /Users/user/Project/ASIK/app/Services/CoretaxParserService.php \
   /Users/user/Project/ASIK/app/Services/CoretaxParserService.php.backup-$(date +%Y%m%d-%H%M%S)

# Copy new version
echo "📝 Copying new version..."
cp /Users/user/Project/CoretaxDataParser-API/CoretaxParserService-UPDATED.php \
   /Users/user/Project/ASIK/app/Services/CoretaxParserService.php

# Clear cache
echo "🧹 Clearing cache..."
cd /Users/user/Project/ASIK
php artisan config:clear
php artisan route:clear

echo ""
echo "✅ ASIK service updated successfully!"
echo ""
echo "🎯 Fitur baru yang aktif:"
echo "  ✓ Stock = quantity dari PDF (bukan default 1)"
echo "  ✓ Unit price untuk margin"
echo "  ✓ Unit/satuan (PCS, KG, dll)"
echo "  ✓ Discount amount"
echo "  ✓ Invoice metadata lengkap"
echo ""
echo "🧪 Test sekarang:"
echo "  1. Start API: cd /Users/user/Project/CoretaxDataParser-API && uvicorn api:app --port 8000 --reload"
echo "  2. Buka ASIK dan import tax invoice"
echo "  3. Cek stock - harusnya angka dari PDF (150, 250, dll) bukan 1!"
