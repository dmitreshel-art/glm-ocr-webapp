"""GLM-OCR Web Application Server.

FastAPI backend for OCR processing using llama.cpp server.
Supports images and multi-page PDFs.
"""

import asyncio
import base64
import io
import os
from datetime import datetime
from pathlib import Path
from typing import List

import aiofiles
import httpx
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

app = FastAPI(title="GLM-OCR Web", version="1.0.0")

# Configuration
LLAMA_SERVER_URL = os.getenv("LLAMA_SERVER_URL", "http://llama-server:8080")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/ocr-uploads"))
RESULTS_DIR = Path(os.getenv("RESULTS_DIR", "/app/results"))

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Max image dimensions for GLM-OCR
MAX_IMAGE_WIDTH = 1280
MAX_IMAGE_HEIGHT = 1280


def resize_image(image_data: bytes, max_width: int = MAX_IMAGE_WIDTH, max_height: int = MAX_IMAGE_HEIGHT) -> tuple[bytes, str]:
    """Resize image to fit within max dimensions while preserving aspect ratio."""
    img = Image.open(io.BytesIO(image_data))
    
    img_format = img.format or "PNG"
    mime_type = f"image/{img_format.lower()}"
    if img_format == "JPG":
        mime_type = "image/jpeg"
    
    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        img_format = "JPEG"
        mime_type = "image/jpeg"
    
    output = io.BytesIO()
    img.save(output, format=img_format, quality=85)
    return output.getvalue(), mime_type


def pdf_to_images(pdf_data: bytes) -> List[tuple[bytes, str]]:
    """Convert PDF pages to images. Returns list of (image_data, mime_type)."""
    try:
        from pdf2image import convert_from_bytes
    except ImportError:
        raise HTTPException(500, "PDF support not installed. Run: pip install pdf2image")
    
    try:
        images = convert_from_bytes(pdf_data, dpi=200)
        result = []
        for img in images:
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=85)
            result.append((output.getvalue(), "image/jpeg"))
        return result
    except Exception as e:
        raise HTTPException(400, f"Failed to convert PDF: {str(e)}")


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
    return {"status": "ok", "llama_server": "ok"}


@app.get("/api/health")
async def llama_health():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{LLAMA_SERVER_URL}/health")
            if resp.status_code == 200:
                return {"status": "ok"}
            return {"status": "error", "code": resp.status_code}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def ocr_image(image_data: bytes, mime_type: str) -> str:
    """Process single image and return OCR text."""
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    image_url = f"data:{mime_type};base64,{image_base64}"
    
    prompt = "Recognize all text in this image. Output only the text without any comments."
    
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
            raise HTTPException(500, f"OCR failed: {response.text[:200]}")
        
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")


@app.post("/api/ocr")
async def process_ocr(file: UploadFile = File(...)):
    """Process image or PDF and return OCR result."""
    allowed_image_types = ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"]
    allowed_pdf_types = ["application/pdf"]
    allowed_types = allowed_image_types + allowed_pdf_types
    
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Invalid file type: {file.content_type}. Allowed: images, PDF")
    
    try:
        content = await file.read()
        
        # Handle PDF
        if file.content_type == "application/pdf":
            print(f"[OCR] Processing PDF: {len(content)} bytes")
            pages = pdf_to_images(content)
            print(f"[OCR] PDF converted to {len(pages)} pages")
            
            results = []
            for i, (page_data, mime_type) in enumerate(pages):
                print(f"[OCR] Processing page {i + 1}/{len(pages)}")
                resized_data, _ = resize_image(page_data)
                text = await ocr_image(resized_data, mime_type)
                results.append({"page": i + 1, "text": text.strip()})
            
            # Combine all pages
            combined_text = "\n\n--- Page Break ---\n\n".join(r["text"] for r in results)
            
            # Save result
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = "".join(c if c.isalnum() or c in "._- " else "_" for c in (file.filename or "document"))
            result_file = RESULTS_DIR / f"{timestamp}_{safe_filename}.txt"
            
            async with aiofiles.open(result_file, "w", encoding="utf-8") as f:
                await f.write(f"# OCR Result: {file.filename}\n")
                await f.write(f"# Pages: {len(pages)}\n")
                await f.write(f"# Date: {datetime.now().isoformat()}\n\n")
                await f.write(combined_text)
            
            return {
                "success": True,
                "text": combined_text,
                "pages": results,
                "file_id": timestamp,
                "total_pages": len(pages)
            }
        
        # Handle image
        print(f"[OCR] Received image: {len(content)} bytes, type: {file.content_type}")
        resized_data, mime_type = resize_image(content)
        print(f"[OCR] Resized image: {len(resized_data)} bytes")
        
        text = await ocr_image(resized_data, mime_type)
        print(f"[OCR] Got text: {len(text)} chars")
        
        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = "".join(c if c.isalnum() or c in "._- " else "_" for c in (file.filename or "image"))
        result_file = RESULTS_DIR / f"{timestamp}_{safe_filename}.txt"
        
        async with aiofiles.open(result_file, "w", encoding="utf-8") as f:
            await f.write(f"# OCR Result\n")
            await f.write(f"# Source: {file.filename}\n")
            await f.write(f"# Date: {datetime.now().isoformat()}\n\n")
            await f.write(text.strip())
        
        return {"success": True, "text": text.strip(), "file_id": timestamp}
        
    except httpx.TimeoutException:
        raise HTTPException(504, "OCR request timed out")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[OCR] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"OCR error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


@app.post("/api/ocr")
async def process_ocr(file: UploadFile = File(...)):
    """Process image and return OCR result."""
    import traceback
    
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Invalid file type: {file.content_type}")
    
    try:
        content = await file.read()
        print(f"[OCR] Received image: {len(content)} bytes, type: {file.content_type}")
        
        # Resize image to fit context window
        try:
            resized_content, mime_type = resize_image(content)
            print(f"[OCR] Resized image: {len(resized_content)} bytes, type: {mime_type}")
        except Exception as e:
            print(f"[OCR] Resize failed: {e}")
            raise HTTPException(400, f"Failed to process image: {str(e)}")
        
        image_base64 = base64.b64encode(resized_content).decode("utf-8")
        image_url = f"data:{mime_type};base64,{image_base64}"
        
        prompt = "Recognize all text in this image. Output only the text without any comments."
        
        print(f"[OCR] Sending to llama-server...")
        
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
            
            print(f"[OCR] Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[OCR] Error response: {response.text[:500]}")
                raise HTTPException(500, f"OCR failed: {response.text[:200]}")
            
            result = response.json()
            text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"[OCR] Got text: {len(text)} chars")
            
            # Save result to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = "".join(c if c.isalnum() or c in "._- " else "_" for c in (file.filename or "image"))
            result_file = RESULTS_DIR / f"{timestamp}_{safe_filename}.txt"
            
            try:
                async with aiofiles.open(result_file, "w", encoding="utf-8") as f:
                    await f.write(f"# OCR Result\n")
                    await f.write(f"# Source: {file.filename}\n")
                    await f.write(f"# Date: {datetime.now().isoformat()}\n\n")
                    await f.write(text.strip())
                print(f"[OCR] Saved to: {result_file}")
            except Exception as e:
                print(f"[OCR] Failed to save result: {e}")
            
            return {"success": True, "text": text.strip(), "file_id": timestamp}
            
    except httpx.TimeoutException:
        print(f"[OCR] Timeout")
        raise HTTPException(504, "OCR request timed out")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[OCR] Error: {e}")
        traceback.print_exc()
        raise HTTPException(500, f"OCR error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)