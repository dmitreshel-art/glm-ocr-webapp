# Start HIP llama-server on Windows (GPU acceleration)
# Radeon 890M / gfx1150

$llamaDir = "C:\Users\1\.llamaCPP"
$modelPath = "F:\MyProjects\GLM-OCR\hf-cache"

Write-Host "Starting HIP llama-server (GPU)..." -ForegroundColor Green

Set-Location $llamaDir

& .\llama-server.exe `
    -m "$modelPath\ggml-org_GLM-OCR-GGUF_GLM-OCR-Q8_0.gguf" `
    --mmproj "$modelPath\ggml-org_GLM-OCR-GGUF_mmproj-GLM-OCR-Q8_0.gguf" `
    -ngl 99 `
    --ctx-size 16384 `
    --port 8765 `
    --host 0.0.0.0