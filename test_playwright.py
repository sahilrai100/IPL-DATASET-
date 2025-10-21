from playwright.sync_api import sync_playwright

print("Testing Playwright...")

with sync_playwright() as p:
    # Launch browser
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Go to a simple page
    page.goto('https://raisahil100.pythonanywhere.com/')
    
    # Get title
    title = page.title()
    print(f"✅ Page title: {title}")
    
    # Get some text

     # Try to get h1, but don't fail if it doesn't exist
    try:
                heading = page.locator('h1').first.inner_text(timeout=5000)
    except:
                heading = "No heading found"
            
    browser.close()
    

print("🎉 PLAYWRIGHT TEST PASSED!")