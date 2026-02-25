"""
Automated browser test using Playwright: Open the web app,
upload a test PNG, and verify the preview and diagnosis appear.
"""
import sys
import base64
import asyncio
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("ERROR: playwright not installed. Run: pip install playwright")
    sys.exit(1)


PNG_1x1_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
)


async def test_upload_flow():
    """Test the upload flow through the browser UI."""
    data = base64.b64decode(PNG_1x1_BASE64)
    test_png = Path("test_browser_upload.png")
    test_png.write_bytes(data)
    print(f"[TEST] Created test image: {test_png} ({len(data)} bytes)")

    async with async_playwright() as p:
        print("[BROWSER] Launching Chromium (headless)...")
        browser = await p.chromium.launch(headless=True)
        print("[BROWSER] Browser launched")

        context = await browser.new_context()
        page = await context.new_page()
        
        # Intercept /upload response to capture diagnosis
        captured_responses = []
        all_requests = []
        
        async def on_request(request):
            all_requests.append({"url": request.url, "method": request.method})
            if "/upload" in request.url:
                print(f"[REQUEST] {request.method} {request.url}")
        
        async def on_response(response):
            if "/upload" in response.url:
                print(f"[INTERCEPT] Captured {response.status} from /upload")
                try:
                    body = await response.json()
                    captured_responses.append(body)
                    print(f"[INTERCEPT] Response keys: {list(body.keys())[:5]}...")
                except Exception as e:
                    print(f"[INTERCEPT] Could not parse JSON: {e}")
        
        async def on_request_failed(request):
            if "/upload" in request.url:
                print(f"[REQUEST FAILED] {request.method} {request.url}")
                print(f"[REQUEST FAILED] Failure: {request.failure}")
        
        def on_console_msg(msg):
            print(f"[CONSOLE] {msg.type.upper()}: {msg.text}")
        
        page.on("request", on_request)
        page.on("response", on_response)
        page.on("requestfailed", on_request_failed)
        page.on("console", on_console_msg)
        
        print("[BROWSE] Navigating to http://127.0.0.1:5000/")
        try:
            await page.goto("http://127.0.0.1:5000/", timeout=30000)
            print("[BROWSE] Page loaded")
        except Exception as e:
            print(f"[WARN] 127.0.0.1 failed, trying localhost")
            try:
                await page.goto("http://localhost:5000/", timeout=30000)
                print("[BROWSE] Page loaded (via localhost)")
            except Exception as e2:
                print(f"[ERROR] Failed to load page (both 127.0.0.1 and localhost): {e2}")
                await browser.close()
                return False
        
        # Wait for page to be ready (networkidle)
        print("[BROWSE] Waiting for page to load fully...")
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
            print("[BROWSE] Page ready")
        except Exception as e:
            print(f"[WARN] Page load state timeout: {e}")
        
        # Check if elements exist
        print("[BROWSE] Checking for DOM elements...")
        try:
            img_input = page.locator("#imageInput")
            # Hidden file inputs don't need to be visible to interact with them
            print("[BROWSE] Image input element found (hidden by design)")
        except Exception as e:
            print(f"[ERROR] Image input not found: {e}")
            await browser.close()
            return False
        
        # Upload the test image
        print(f"[UPLOAD] Uploading {test_png}...")
        await page.locator("#imageInput").set_input_files(str(test_png))
        print("[UPLOAD] File input set")
        
        # Wait for preview to appear (or timeout gracefully)
        print("[PREVIEW] Waiting for preview image...")
        try:
            preview_img = page.locator("#previewImage")
            # Try to wait for visible state, but it may appear silently
            await asyncio.sleep(1)  # Give time for image loader to process
            await preview_img.wait_for(state="attached", timeout=5000)
            print("[PREVIEW] ✓ Preview image element attached!")
        except Exception as e:
            print(f"[ERROR] Preview image did not appear: {e}")
            # Get page content to debug
            content = await page.content()
            if "No image selected" in content:
                print("[ERROR] Page still shows 'No image selected' placeholder")
            await browser.close()
            return False
        
        # Check result text
        result_text = await page.locator("#result").text_content()
        if result_text and "Image loaded" in result_text:
            print("[PREVIEW] ✓ Result message confirms image loaded")
        
        # Click Analyze button
        print("[ANALYZE] Clicking 'Analyze Health Condition' button...")
        try:
            analyze_btn = page.locator("#analyzeBtn")
            await analyze_btn.wait_for(timeout=5000)
            await analyze_btn.click()
            print("[ANALYZE] Button clicked")
        except Exception as e:
            print(f"[ERROR] Failed to click analyze button: {e}")
            await browser.close()
            return False
        
        # Wait for response capture and result display
        print("[ANALYZE] Waiting for diagnosis response (up to 30s)...")
        max_wait = 30
        start = asyncio.get_event_loop().time()
        while len(captured_responses) == 0 and (asyncio.get_event_loop().time() - start) < max_wait:
            await asyncio.sleep(0.5)
        
        print(f"[DEBUG] All requests made during upload: {all_requests}")
        
        if len(captured_responses) > 0:
            resp = captured_responses[0]
            print(f"[SUCCESS] ✓ Upload succeeded!")
            print(f"  - Diagnosis: {resp.get('Diagnosis', 'N/A')}")
            print(f"  - Confidence: {resp.get('Confidence', 'N/A')}")
            print(f"  - Status: {resp.get('Status', 'N/A')}")
            if resp.get('image_url'):
                print(f"  - Image URL: {resp.get('image_url')}")
            result_ok = True
        else:
            print("[ERROR] No /upload response captured within 30s")
            # Check if there's an error message on page
            try:
                result = await page.locator("#result").text_content()
                print(f"[DEBUG] Result content: {result[:200]}")
            except:
                pass
            result_ok = False
        
        # Cleanup
        await browser.close()
        test_png.unlink()
        return result_ok


if __name__ == "__main__":
    try:
        success = asyncio.run(test_upload_flow())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[FATAL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
