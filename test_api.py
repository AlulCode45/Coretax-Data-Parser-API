"""
Test script untuk Coretax Data Parser API
"""
import requests
import os

# Base URL API
BASE_URL = "http://localhost:8000"

def test_root():
    """Test root endpoint"""
    print("🧪 Testing Root Endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_health():
    """Test health check endpoint"""
    print("🧪 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_single_file(pdf_path):
    """Test parsing single PDF file"""
    print(f"🧪 Testing Single File Parse: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}\n")
        return
    
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/parse", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Filename: {result.get('filename')}")
    print(f"Status: {result.get('status')}")
    print(f"Total Items: {result.get('total_items')}")
    
    if result.get('validation'):
        validation = result['validation']
        print(f"Valid: {validation.get('is_valid')}")
        print(f"Calculated: {validation.get('calculated_total_formatted')}")
        print(f"PDF Total: {validation.get('pdf_total_formatted')}")
    print()

def test_multiple_files(pdf_paths):
    """Test parsing multiple PDF files"""
    print(f"🧪 Testing Multiple Files Parse: {len(pdf_paths)} files")
    
    files = []
    for path in pdf_paths:
        if os.path.exists(path):
            files.append(('files', open(path, 'rb')))
        else:
            print(f"⚠️ Skipping {path} - file not found")
    
    if not files:
        print("❌ No valid files to process\n")
        return
    
    response = requests.post(f"{BASE_URL}/parse-multiple", files=files)
    
    # Close all file handles
    for _, f in files:
        f.close()
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Total Files: {result.get('total_files')}")
    print(f"Success: {result.get('total_success')}")
    print(f"Failed: {result.get('total_failed')}")
    
    if result.get('results'):
        print("\nResults:")
        for idx, res in enumerate(result['results'], 1):
            print(f"  {idx}. {res.get('filename')} - {res.get('status')}")
    print()

def test_api_info():
    """Test API info endpoint"""
    print("🧪 Testing API Info...")
    response = requests.get(f"{BASE_URL}/api-info")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"API Name: {result.get('api_name')}")
    print(f"Version: {result.get('version')}")
    print(f"Endpoints: {len(result.get('endpoints', []))}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Coretax Data Parser API - Test Script")
    print("=" * 60)
    print()
    
    # Pastikan API server sudah berjalan
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print("❌ API server tidak berjalan!")
        print("Jalankan server dengan: python api.py")
        print("Atau: uvicorn api:app --reload")
        exit(1)
    
    # Test all endpoints
    test_root()
    test_health()
    test_api_info()
    
    # Test file parsing
    # Ganti dengan path file PDF Anda
    sample_pdf = "sample_pdf/invoice.pdf"
    
    # Cari file PDF di folder sample_pdf
    if os.path.exists("sample_pdf"):
        pdf_files = [
            os.path.join("sample_pdf", f) 
            for f in os.listdir("sample_pdf") 
            if f.lower().endswith('.pdf')
        ]
        
        if pdf_files:
            # Test single file
            test_single_file(pdf_files[0])
            
            # Test multiple files (max 3 untuk demo)
            if len(pdf_files) > 1:
                test_multiple_files(pdf_files[:3])
        else:
            print("⚠️ Tidak ada file PDF di folder sample_pdf/")
    else:
        print("⚠️ Folder sample_pdf/ tidak ditemukan")
    
    print("=" * 60)
    print("✅ Testing completed!")
    print("=" * 60)
