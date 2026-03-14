# Start HIP llama-server on Windows (CPU-only, no GPU)
# Use when GPU is not available or for testing

$llamaDir = "C:\Users\1\.llamaCPP"
$modelPath = "F:\MyProjects\GLM-OCR\hf-cache"

Write-Host "Starting llama-server (CPU-only)..." -ForegroundColor Yellow

Set-Location $llamaDir

# CPU-only: no -ngl flag means all layers on CPU
& .\llama-server.exe `
    -m "$modelPath\ggml-org_GLM-OCR-GGUF_GLM-OCR-Q8_0.gguf" `
    --mmproj "$modelPath\ggml-org_GLM-OCR-GGUF_mmproj-GLM-OCR-Q8_0.gguf" `
    --ctx-size 16384 `
    --port 8765 `
    --host 0.0.0.0

# Note: Remove -ngl 99 for CPU-only mode
# Add -ngl 99 for GPU acceleration (HIP)