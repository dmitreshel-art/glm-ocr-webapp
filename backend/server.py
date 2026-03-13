"""GLM-OCR Web Application Server.

FastAPI backend for OCR processing using llama.cpp server and GLM-OCR model.

llama.cpp server supports OpenAI-compatible multimodal API.
Use /v1/chat/completions with image_url content type.
"""

import asyncio
import base64
import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional

import aiofiles
import httpx
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="GLM-OCR Web", version="1.0.0")

# Configuration
MODEL_PATH = Path(os.getenv("MODEL_PATH", "/models/glm-ocr-q8_0.gguf"))
MMPROJ_PATH = Path(os.getenv("MMPROJ_PATH", "/models/mmproj.gguf"))
LLAMA_SERVER_PORT = int(os.getenv("LLAMA_SERVER_PORT", "8765"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/ocr-uploads"))
RESULT_DIR = Path(os.getenv("RESULT_DIR", "/tmp/ocr-results"))

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

# Global state
llama_process: Optional[asyncio.subprocess.Process] = None
server_ready = False


async def start_llama_server():
    """Start llama.cpp server in background with local model."""
    global llama_process, server_ready
    
    if llama_process is not None:
        return
    
    print(f"Starting llama-server with model: {MODEL_PATH}")
    
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model not found: {MODEL_PATH}")
    
    if not MMPROJ_PATH.exists():
        raise RuntimeError(f"mmproj not found: {MMPROJ_PATH}")
    
    llama_process = await asyncio.create_subprocess_exec(
        "llama-server",
        "-m", str(MODEL_PATH),
        "--mmproj", str(MMPROJ_PATH),
        "--port", str(LLAMA_SERVER_PORT),
        "--host", "127.0.0.1",
        "--ctx-size", "4096",
        "--n-gpu-layers", "0",  # CPU only
        "--threads", str(os.cpu_count() or 4),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Wait for server to be ready
    async with httpx.AsyncClient() as client:
        for _ in range(30):  # 30 seconds timeout
            try:
                resp = await client.get(f"http://127.0.0.1:{LLAMA_SERVER_PORT}/health")
                if resp.status_code == 200:
                    server_ready = True
                    print("llama-server is ready")
                    return
            except:
                pass
            await asyncio.sleep(1)
    
    raise RuntimeError("Failed to start llama-server")


@app.on_event("startup")
async def startup():
    """Initialize server."""
    try:
        await start_llama_server()
    except Exception as e:
        print(f"Warning: Could not start llama-server: {e}")
        # Continue anyway - might use external server


@app.on_event("shutdown")
async def shutdown():
    """Cleanup."""
    global llama_process
    if llama_process:
        llama_process.terminate()
        await llama_process.wait()


# Mount static files
app.mount("/static", StaticFiles(directory=Path(__file__).parent.parent / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve main page."""
    static_dir = Path(__file__).parent.parent / "static"
    index_file = static_dir / "index.html"
    async with aiofiles.open(index_file, "r") as f:
        return await f.read()


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server_ready": server_ready,
        "model": str(MODEL_PATH.name)
    }


@app.post("/api/ocr")
async def process_ocr(file: UploadFile = File(...)):
    """Process image and return OCR result using OpenAI-compatible API."""
    global server_ready
    
    if not server_ready:
        try:
            await start_llama_server()
        except Exception as e:
            raise HTTPException(503, f"OCR server not ready: {e}")
    
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Invalid file type: {file.content_type}")
    
    # Save uploaded file
    file_id = str(uuid.uuid4())
    file_ext = Path(file.filename or "image.png").suffix or ".png"
    upload_path = UPLOAD_DIR / f"{file_id}{file_ext}"
    
    async with aiofiles.open(upload_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    # Convert image to base64
    image_base64 = base64.b64encode(content).decode("utf-8")
    
    # Determine MIME type
    mime_type = file.content_type or "image/png"
    image_url = f"data:{mime_type};base64,{image_base64}"
    
    # Use OpenAI-compatible chat completions API
    # llamacpp server supports multimodal in /v1/chat/completions
    prompt = "Recognize all text in this image. Output only the recognized text without any comments or explanations."
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"http://127.0.0.1:{LLAMA_SERVER_PORT}/v1/chat/completions",
                json={
                    "model": "glm-ocr",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": image_url}}
                            ]
                        }
                    ],
                    "max_tokens": 2048,
                    "temperature": 0.1
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(500, f"OCR failed: {response.text}")
            
            result = response.json()
            
            # Extract text from OpenAI response format
            if "choices" in result and len(result["choices"]) > 0:
                text = result["choices"][0].get("message", {}).get("content", "")
            else:
                text = result.get("content", "")
            
            return JSONResponse({
                "success": True,
                "text": text.strip(),
                "file_id": file_id
            })
            
    except httpx.TimeoutException:
        raise HTTPException(504, "OCR request timed out")
    except Exception as e:
        raise HTTPException(500, f"OCR error: {str(e)}")
    finally:
        # Cleanup uploaded file
        if upload_path.exists():
            upload_path.unlink()


@app.post("/api/ocr/batch")
async def process_batch(files: list[UploadFile] = File(...)):
    """Process multiple images."""
    results = []
    for file in files:
        try:
            result = await process_ocr(file)
            results.append(result)
        except HTTPException as e:
            results.append({"success": False, "error": str(e.detail)})
    return {"results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)