"""GLM-OCR Web Application Server.

FastAPI backend for OCR processing using llama.cpp server.
"""

import asyncio
import base64
import os
from pathlib import Path

import aiofiles
import httpx
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="GLM-OCR Web", version="1.0.0")

# Configuration - connect to separate llama-server container
LLAMA_SERVER_URL = os.getenv("LLAMA_SERVER_URL", "http://llama-server:8080")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/ocr-uploads"))

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{LLAMA_SERVER_URL}/health", timeout=5.0)
            return {
                "status": "healthy",
                "llama_server": "ready" if resp.status_code == 200 else "error"
            }
    except Exception as e:
        return {"status": "degraded", "llama_server": str(e)}


@app.post("/api/ocr")
async def process_ocr(file: UploadFile = File(...)):
    """Process image and return OCR result."""
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Invalid file type: {file.content_type}")
    
    content = await file.read()
    image_base64 = base64.b64encode(content).decode("utf-8")
    mime_type = file.content_type or "image/png"
    image_url = f"data:{mime_type};base64,{image_base64}"
    
    prompt = "Recognize all text in this image. Output only the text without any comments."
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{LLAMA_SERVER_URL}/v1/chat/completions",
                json={
                    "model": "glm-ocr",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }],
                    "max_tokens": 2048,
                    "temperature": 0.1
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(500, f"OCR failed: {response.text}")
            
            result = response.json()
            text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {"success": True, "text": text.strip()}
            
    except httpx.TimeoutException:
        raise HTTPException(504, "OCR request timed out")
    except Exception as e:
        raise HTTPException(500, f"OCR error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)