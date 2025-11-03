"""
Debug script to inspect X's current HTML and find the right selectors
This will help us figure out why the scraper can't find user cards
"""

import time
import os
from playwright.sync_api import sync_playwright

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_DIR = os.path.join(PROJECT_ROOT, 'auth', 'accounts')

def debug_x_selectors():
    """
    Opens X search page and lets you inspect the HTML
    """
    
    print("\n" + "="*70)
    print(" X SELECTOR DEBUG TOOL")
    print("="*70)
    
    # Use your existing account
    account_name = "account1"
    state_file = os.path.join(ACCOUNTS_DIR, f'{account_name}_state.json')
    
    if not os.path.exists(state_file):
        print(f"\n❌ Account '{account_name}' not found!")
        print("Run: python setup_accounts.py first")
        return
    
    print(f"\nUsing account: {account_name}")
    print("Opening browser in NON-headless mode so you can see what's happening...\n")
    
    playwright = sync_playwright().start()
    
    browser = playwright.chromium.launch(
        headless=False,  # So you can see what's happening
        args=['--disable-blink-features=AutomationControlled']
    )
    
    context = browser.new_context(
        storage_state=state_file,
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    )
    
    page = context.new_page()
    
    # First, verify we're logged in
    print("Step 1: Checking login status...")
    try:
        page.goto("https://twitter.com/home", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        
        current_url = page.url
        print(f"Current URL: {current_url}")
        
        if "login" in current_url.lower():
            print("\n❌ Session expired! You're being redirected to login.")
            print("Run: python setup_accounts.py to refresh your session")
            context.close()
            browser.close()
            playwright.stop()
            return
        
        print("✅ Logged in successfully!")
        
    except Exception as e:
        print(f"❌ Error loading home page: {e}")
        context.close()
        browser.close()
        playwright.stop()
        return
    
    # Now try the search
    search_url = "https://twitter.com/search?q=AI%20founder&f=user"
    
    print(f"\nStep 2: Navigating to search page...")
    print(f"URL: {search_url}")
    
    try:
        page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        print("✅ Page loaded!")
    except Exception as e:
        print(f"\n❌ Error loading search page: {e}")
        print("Taking a screenshot to see what happened...")
        page.screenshot(path="error_screenshot.png")
        print("Screenshot saved: error_screenshot.png")
        context.close()
        browser.close()
        playwright.stop()
        return
    
    print("\n" + "="*70)
    print(" TESTING SELECTORS")
    print("="*70)
    
    # Try all the selectors
    selectors_to_test = [
        '[data-testid="UserCell"]',
        'div[data-testid="cellInnerDiv"]',
        'article[data-testid="UserCell"]',
        '[data-testid="User-Name"]',
        'div[dir="ltr"]',
        'div[data-testid="UserAvatar-Container-unknown"]',
        'a[role="link"][href^="/"]',
    ]
    
    print("\nSearching for user card elements...\n")
    
    for selector in selectors_to_test:
        try:
            elements = page.query_selector_all(selector)
            count = len(elements)
            
            if count > 0:
                print(f"✅ FOUND: '{selector}' → {count} elements")
                
                # Get a sample element's HTML
                if count > 0:
                    first_elem = elements[0]
                    outer_html = first_elem.evaluate('el => el.outerHTML')
                    print(f"   Sample HTML (first 200 chars):")
                    print(f"   {outer_html[:200]}...\n")
            else:
                print(f"❌ EMPTY: '{selector}' → 0 elements")
        except Exception as e:
            print(f"❌ ERROR: '{selector}' → {e}")
    
    # Save page HTML for inspection
    html_file = os.path.join(PROJECT_ROOT, "x_page_debug.html")
    page_html = page.content()
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(page_html)
    print(f"\n📄 Full page HTML saved to: {html_file}")
    
    # Save screenshot
    screenshot_file = os.path.join(PROJECT_ROOT, "x_page_debug.png")
    page.screenshot(path=screenshot_file, full_page=True)
    print(f"📸 Screenshot saved to: {screenshot_file}")
    
    print("\n" + "="*70)
    print(" BROWSER IS OPEN - INSPECT THE PAGE")
    print("="*70)
    print("\nThe browser window is now open. You can:")
    print("  1. Right-click on a user card → Inspect")
    print("  2. Look at the HTML structure")
    print("  3. Find the correct selector")
    print("\nWhen done, press ENTER here to close everything...")
    
    input()
    
    context.close()
    browser.close()
    playwright.stop()
    
    print("\n✅ Debug session complete!")
    print("\nNext steps:")
    print("  1. Check the files: x_page_debug.html and x_page_debug.png")
    print("  2. Look for patterns in the HTML")
    print("  3. Share the output with me and I'll update the selectors")

if __name__ == "__main__":
    debug_x_selectors()