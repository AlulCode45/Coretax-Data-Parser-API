#!/bin/bash

# Test Script untuk Web Client
# Script ini akan start API server dan buka web client

echo "=================================================="
echo "🚀 Starting Coretax Parser API & Web Client"
echo "=================================================="
echo ""

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python3 first."
    exit 1
fi

# Check if uvicorn is installed
if ! python3 -c "import uvicorn" &> /dev/null; then
    echo "❌ uvicorn not found. Installing..."
    pip3 install uvicorn fastapi python-multipart pdfplumber --quiet
fi

echo "✅ Dependencies OK"
echo ""

# Start API server in background
echo "🔧 Starting API server on port 9000..."
uvicorn api:app --host 0.0.0.0 --port 9000 --reload &
API_PID=$!

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
sleep 3

# Check if API is running
if curl -s http://localhost:9000/health > /dev/null; then
    echo "✅ API Server is running (PID: $API_PID)"
else
    echo "❌ API Server failed to start"
    kill $API_PID 2>/dev/null
    exit 1
fi

echo ""
echo "=================================================="
echo "✨ Ready to use!"
echo "=================================================="
echo ""
echo "📍 API Server: http://localhost:9000"
echo "📍 API Docs: http://localhost:9000/docs"
echo "📍 Web Client: Opening in browser..."
echo ""
echo "💡 To stop the server, press Ctrl+C or run:"
echo "   kill $API_PID"
echo ""

# Open web client in default browser
if command -v open &> /dev/null; then
    # macOS
    open web_client.html
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open web_client.html
elif command -v start &> /dev/null; then
    # Windows
    start web_client.html
else
    echo "⚠️  Please open web_client.html manually in your browser"
fi

# Keep script running
echo "Press Ctrl+C to stop the server..."
wait $API_PID
