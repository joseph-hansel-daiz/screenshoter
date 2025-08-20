import hashlib
import os
import zlib
import io
import asyncio
import redis

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
from playwright.async_api import async_playwright

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

CACHE_TTL_SECONDS = 604800  # 1 Week

def generate_screenshot_cache_key(url: str, width: int, height: int, delay: int) -> str:
    hash_input = f"{url}|{width}|{height}|{delay}"
    return f"screenshot:{hashlib.sha256(hash_input.encode()).hexdigest()}"

@app.get("/screenshot")
async def screenshot(
    url: str = Query(..., description="URL of the website"),
    width: int = Query(1280, description="Width of the screen (default: 1280)"),
    height: int = Query(720, description="Height of the screen (default: 720)"),
    delay: int = Query(1, description="Delay before taking screenshot (default: 1)")
):
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    cache_key = generate_screenshot_cache_key(url, width, height, delay)

    # Check Redis cache
    cached_image = r.get(cache_key)
    if cached_image:
        # Decompress image before returning
        decompressed = zlib.decompress(cached_image)
        return StreamingResponse(io.BytesIO(decompressed), media_type="image/png")

    # Generate screenshot if not cached
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": width, "height": height}
            )
            page = await context.new_page()
            await page.goto(url, wait_until="load")
            await asyncio.sleep(delay)

            screenshot_bytes = await page.screenshot(full_page=False, type="png")
            await browser.close()

            # Compress and store in Redis
            compressed = zlib.compress(screenshot_bytes)
            r.setex(cache_key, CACHE_TTL_SECONDS, compressed)

            return StreamingResponse(io.BytesIO(screenshot_bytes), media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to capture screenshot: {str(e)}")
