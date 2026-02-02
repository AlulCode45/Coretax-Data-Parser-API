<?php

namespace App\Services;

use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class CoretaxParserService
{
    private string $apiUrl;
    private int $timeout;

    public function __construct()
    {
        $this->apiUrl = config('services.coretax_parser.url', 'http://localhost:8000');
        $this->timeout = config('services.coretax_parser.timeout', 60);
    }

    /**
     * Parse single PDF file menggunakan API CoretaxDataParser
     *
     * @param UploadedFile $file
     * @return array
     * @throws \Exception
     */
    public function parseSinglePdf(UploadedFile $file): array
    {
        try {
            Log::info('CoretaxParserService: Parsing single PDF', [
                'file' => $file->getClientOriginalName(),
                'api_url' => $this->apiUrl,
                'timeout' => $this->timeout
            ]);

            $response = Http::timeout($this->timeout)
                ->attach('file', fopen($file->getRealPath(), 'r'), $file->getClientOriginalName())
                ->post("{$this->apiUrl}/parse");

            Log::info('CoretaxParserService: API Response', [
                'status' => $response->status(),
                'body' => $response->body()
            ]);

            if (!$response->successful()) {
                throw new \Exception("API Error (" . $response->status() . "): " . $response->body());
            }

            $data = $response->json();

            if ($data['status'] !== 'success') {
                throw new \Exception("Parse failed: " . ($data['error'] ?? 'Unknown error'));
            }

            return $data;
        } catch (\Exception $e) {
            Log::error('CoretaxParserService::parseSinglePdf failed', [
                'file' => $file->getClientOriginalName(),
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            throw $e;
        }
    }

    /**
     * Parse multiple PDF files menggunakan API CoretaxDataParser
     *
     * @param array $files Array of UploadedFile
     * @return array
     * @throws \Exception
     */
    public function parseMultiplePdfs(array $files): array
    {
        try {
            Log::info('CoretaxParserService: Parsing multiple PDFs', [
                'file_count' => count($files),
                'files' => array_map(fn($f) => $f->getClientOriginalName(), $files),
                'api_url' => $this->apiUrl,
                'timeout' => $this->timeout
            ]);

            $request = Http::timeout($this->timeout);

            foreach ($files as $file) {
                $request->attach(
                    'files',
                    fopen($file->getRealPath(), 'r'),
                    $file->getClientOriginalName()
                );
            }

            $response = $request->post("{$this->apiUrl}/parse-multiple");

            Log::info('CoretaxParserService: API Response', [
                'status' => $response->status(),
                'body_preview' => substr($response->body(), 0, 500)
            ]);

            if (!$response->successful()) {
                throw new \Exception("API Error (" . $response->status() . "): " . $response->body());
            }

            $data = $response->json();

            if ($data['status'] !== 'completed') {
                throw new \Exception("Parse failed: Multiple files processing error. Status: " . ($data['status'] ?? 'unknown'));
            }

            return $data;
        } catch (\Exception $e) {
            Log::error('CoretaxParserService::parseMultiplePdfs failed', [
                'file_count' => count($files),
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            throw $e;
        }
    }

    /**
     * Konversi hasil parsing API ke format yang digunakan sistem
     *
     * @param array $apiResult Hasil dari API CoretaxDataParser
     * @param float $defaultMargin Default margin untuk perhitungan harga jual
     * @return array
     */
    public function convertToSystemFormat(array $apiResult, float $defaultMargin = 1.0): array
    {
        $items = [];

        // Handle single file result
        if ($apiResult['status'] === 'success') {
            $items = $this->processItems($apiResult, $defaultMargin);
        }
        // Handle multiple files result
        elseif ($apiResult['status'] === 'completed' && isset($apiResult['results'])) {
            foreach ($apiResult['results'] as $result) {
                if ($result['status'] === 'success') {
                    $processedItems = $this->processItems($result, $defaultMargin);
                    $items = array_merge($items, $processedItems);
                }
            }
        }

        return $items;
    }

    /**
     * Process items dari hasil API dengan semua data lengkap (v2.0)
     *
     * ✨ NEW FEATURES:
     * - Quantity/Stock dari PDF (bukan default 1 lagi!)
     * - Unit price untuk kalkulasi margin
     * - Unit/satuan (PCS, KG, dll)
     * - Discount amount
     * - Invoice metadata lengkap (number, date, supplier)
     * - Item code dari PDF
     *
     * @param array $result
     * @param float $margin
     * @return array
     */
    private function processItems(array $result, float $margin): array
    {
        $items = [];
        $filename = $result['filename'] ?? 'unknown.pdf';
        $metadata = $result['metadata'] ?? [];

        // Extract invoice number dari metadata (lebih akurat) atau filename
        $invoiceNumber = $metadata['invoice_number'] ?? $this->extractInvoiceNumber($filename);

        Log::info('CoretaxParserService: Processing items', [
            'filename' => $filename,
            'item_count' => count($result['items'] ?? []),
            'has_metadata' => !empty($metadata),
            'invoice_number' => $invoiceNumber
        ]);

        foreach ($result['items'] as $item) {
            // 🎯 FITUR BARU 1: Gunakan unit_price dan quantity dari PDF
            $unitPrice = $item['unit_price'] ?? 0;
            $quantity = $item['quantity'] ?? 1;
            $buyPrice = $item['total'] ?? ($unitPrice * $quantity);

            // Hitung harga jual dengan margin
            $sellPrice = $buyPrice + ($buyPrice * $margin / 100);
            $profit = $sellPrice - $buyPrice;

            // 🎯 FITUR BARU 2: Gunakan item_code dari PDF jika ada
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

                    // 🎯 FITUR BARU 3: Stock menggunakan quantity dari PDF!
                    'stock' => (int) $quantity,
                    'initial_stock' => (int) $quantity,

                    // 🎯 FITUR BARU 4: Informasi tambahan dari parser baru
                    'unit_price' => $unitPrice,
                    'unit' => $item['unit'] ?? 'PCS',
                    'discount' => $item['discount'] ?? 0,

                    // 🎯 FITUR BARU 5: Invoice metadata yang lebih lengkap
                    'original_tax_invoice_file_name' => $filename,
                    'tax_invoice_number' => $invoiceNumber,
                    'invoice_date' => $metadata['invoice_date'] ?? null,
                    'supplier_name' => $metadata['supplier_name'] ?? null,
                    'supplier_npwp' => $metadata['supplier_npwp'] ?? null,

                    'is_free_ppn' => false,
                ]
            ];
        }

        Log::info('CoretaxParserService: Items processed', [
            'processed_count' => count($items),
            'sample_stock' => $items[0]['item']['stock'] ?? 'N/A'
        ]);

        return $items;
    }

    /**
     * Extract invoice number dari filename
     *
     * @param string $filename
     * @return string|null
     */
    private function extractInvoiceNumber(string $filename): ?string
    {
        // Try to extract invoice number from filename
        // Format: InputTaxInvoice-123456.pdf atau similar
        if (preg_match('/(\d+)/', $filename, $matches)) {
            return $matches[1];
        }

        return null;
    }

    /**
     * Check if API is available
     *
     * @return bool
     */
    public function isApiAvailable(): bool
    {
        try {
            $response = Http::timeout(5)->get("{$this->apiUrl}/health");
            return $response->successful() && $response->json('status') === 'healthy';
        } catch (\Exception $e) {
            Log::warning('CoretaxParser API is not available', [
                'url' => $this->apiUrl,
                'error' => $e->getMessage()
            ]);
            return false;
        }
    }
}
