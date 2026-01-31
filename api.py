"""
Coretax Data Parser API
FastAPI application untuk parsing invoice PDF Coretax
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import parser as pdf_parser

# Inisialisasi FastAPI
app = FastAPI(
    title="Coretax Data Parser API",
    description="API untuk mengekstrak dan memvalidasi data faktur pajak dari PDF Coretax",
    version="1.0.0"
)

# CORS middleware untuk membolehkan akses dari web client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dalam production, ganti dengan domain spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Root endpoint - informasi API
    """
    return {
        "message": "Coretax Data Parser API",
        "version": "1.0.0",
        "endpoints": {
            "POST /parse": "Parse single PDF file",
            "POST /parse-multiple": "Parse multiple PDF files",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Coretax Data Parser API"
    }


@app.post("/parse")
async def parse_single_pdf(file: UploadFile = File(...)):
    """
    Parse single PDF file
    
    Args:
        file: PDF file yang akan diparse
    
    Returns:
        JSON response dengan data invoice yang sudah diekstrak
    """
    # Validasi tipe file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="File harus berformat PDF"
        )
    
    try:
        # Baca konten file
        content = await file.read()
        
        # Parse PDF
        result = pdf_parser.parse_pdf_file(content, file.filename)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@app.post("/parse-multiple")
async def parse_multiple_pdfs(files: List[UploadFile] = File(...)):
    """
    Parse multiple PDF files sekaligus
    
    Args:
        files: List of PDF files yang akan diparse
    
    Returns:
        JSON response dengan hasil parsing semua file
    """
    # Validasi minimal 1 file
    if not files:
        raise HTTPException(
            status_code=400,
            detail="Minimal harus upload 1 file"
        )
    
    # Validasi semua file adalah PDF
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' bukan PDF. Semua file harus berformat PDF"
            )
    
    try:
        # Baca semua file
        files_data = []
        for file in files:
            content = await file.read()
            files_data.append((file.filename, content))
        
        # Parse semua PDF
        result = pdf_parser.parse_multiple_pdfs(files_data)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing files: {str(e)}"
        )


@app.get("/api-info")
async def api_info():
    """
    Informasi detail tentang API endpoints
    """
    return {
        "api_name": "Coretax Data Parser API",
        "version": "1.0.0",
        "endpoints": [
            {
                "method": "GET",
                "path": "/",
                "description": "Root endpoint dengan informasi dasar API"
            },
            {
                "method": "GET",
                "path": "/health",
                "description": "Health check endpoint"
            },
            {
                "method": "POST",
                "path": "/parse",
                "description": "Parse single PDF file",
                "parameters": {
                    "file": "PDF file (form-data)"
                },
                "response": {
                    "status": "success/error",
                    "filename": "nama file",
                    "items": "list item barang",
                    "total_items": "jumlah item",
                    "validation": {
                        "calculated_total": "total kalkulasi",
                        "pdf_total": "total dari PDF",
                        "is_valid": "true/false",
                        "difference": "selisih"
                    }
                }
            },
            {
                "method": "POST",
                "path": "/parse-multiple",
                "description": "Parse multiple PDF files sekaligus",
                "parameters": {
                    "files": "Multiple PDF files (form-data)"
                },
                "response": {
                    "status": "completed",
                    "total_files": "jumlah file",
                    "total_success": "jumlah sukses",
                    "total_failed": "jumlah gagal",
                    "results": "array hasil parsing tiap file"
                }
            },
            {
                "method": "GET",
                "path": "/api-info",
                "description": "Endpoint ini - informasi detail API"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
