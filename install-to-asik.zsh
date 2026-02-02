#!/usr/bin/env zsh

set -e

echo "🔄 Updating ASIK CoretaxParserService..."
echo ""

ASIK_DIR="/Users/user/Project/ASIK"
PARSER_DIR="/Users/user/Project/CoretaxDataParser-API"
SERVICE_FILE="app/Services/CoretaxParserService.php"

# Check files exist
if [ ! -f "$ASIK_DIR/$SERVICE_FILE" ]; then
    echo "❌ Error: ASIK service file not found"
    exit 1
fi

if [ ! -f "$PARSER_DIR/CoretaxParserService-UPDATED.php" ]; then
    echo "❌ Error: Updated service file not found"
    exit 1
fi

# Backup
echo "📦 Creating backup..."
BACKUP_FILE="$ASIK_DIR/$SERVICE_FILE.backup-$(date +%Y%m%d-%H%M%S)"
cp "$ASIK_DIR/$SERVICE_FILE" "$BACKUP_FILE"
echo "   Backup: $BACKUP_FILE"

# Copy new version
echo ""
echo "📝 Copying new version..."
cp "$PARSER_DIR/CoretaxParserService-UPDATED.php" "$ASIK_DIR/$SERVICE_FILE"
echo "   ✓ File copied"

# Verify
echo ""
echo "✅ Verifying..."
if grep -q "Stock menggunakan quantity" "$ASIK_DIR/$SERVICE_FILE"; then
    echo "   ✓ New code detected"
else
    echo "   ⚠️  Warning: New code markers not found"
fi

# Clear cache
echo ""
echo "🧹 Clearing Laravel cache..."
cd "$ASIK_DIR"
php artisan config:clear > /dev/null 2>&1 && echo "   ✓ Config cleared"
php artisan route:clear > /dev/null 2>&1 && echo "   ✓ Routes cleared"

echo ""
echo "=" | head -c 60 && echo
echo "✅ ASIK SERVICE UPDATED SUCCESSFULLY!"
echo "=" | head -c 60 && echo
echo ""
echo "🎯 Fitur baru yang aktif:"
echo "   ✓ Stock = quantity dari PDF (bukan default 1)"
echo "   ✓ Unit price untuk margin"
echo "   ✓ Unit/satuan (PCS, KG, dll)"
echo "   ✓ Discount amount"
echo "   ✓ Invoice metadata lengkap"
echo ""
echo "🧪 Test sekarang:"
echo "   1. cd $PARSER_DIR"
echo "   2. uvicorn api:app --port 8000 --reload"
echo "   3. Buka ASIK dan import tax invoice"
echo "   4. Cek stock - harusnya angka dari PDF!"
echo ""
