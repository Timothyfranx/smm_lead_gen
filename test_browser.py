"""
Quick test to verify browser opens and loads X properly
UPDATED VERSION with better wait times
"""

import time
from src.scraper import Scraper

def test_browser():
    print("\n" + "="*70)
    print(" TESTING BROWSER VISIBILITY")
    print("="*70)
    
    print("\n1. Creating scraper with headless=False...")
    scraper = Scraper(headless=False, account_name="account1")
    
    print("2. Loading account...")
    if not scraper._load_account_state("account1"):
        print("❌ Failed to load account!")
        return
    
    print("3. ✅ Browser should be VISIBLE now!")
    print("4. Navigating to X home page (this takes 10-15 seconds)...")
    
    try:
        scraper.page.goto("https://twitter.com/home", wait_until="load", timeout=90000)
        time.sleep(10)  # Wait for page to fully render
        
        print("5. ✅ Page loaded!")
        print("\n" + "="*70)
        print(" CHECK THE BROWSER WINDOW")
        print("="*70)
        print("The browser should be visible and showing X home page.")
        print("Do you see your timeline? Does it look normal? (y/n)")
        
        response = input("> ")
        
        if response.lower() == 'y':
            print("\n✅ Great! Now testing search page...")
            
            search_url = "https://twitter.com/search?q=AI%20founder&f=user"
            print(f"Navigating to: {search_url}")
            print("(This also takes 10-15 seconds)...")
            
            scraper.page.goto(search_url, wait_until="load", timeout=90000)
            time.sleep(15)  # Give search page time to load
            
            print("\n" + "="*70)
            print(" CHECK THE SEARCH PAGE")
            print("="*70)
            print("Do you see user search results?")
            print("Is the page layout normal? (y/n)")
            
            response2 = input("> ")
            
            if response2.lower() == 'y':
                print("\n✅ Everything looks good!")
                print("The scraper should work. Try running main.py again.")
            else:
                print("\n❌ Page is broken/misaligned")
                print("Taking screenshot for analysis...")
                scraper.page.screenshot(path="test_search_page.png", full_page=True)
                print("Screenshot saved: test_search_page.png")
                print("Send me this screenshot so I can see what X is serving.")
        else:
            print("\n❌ Home page looks broken")
            print("Taking screenshot...")
            scraper.page.screenshot(path="test_home_page.png", full_page=True)
            print("Screenshot saved: test_home_page.png")
            
            # Check what error is showing
            page_content = scraper.page.content()
            if "Something went wrong" in page_content:
                print("\n⚠️  Detected 'Something went wrong' error")
            if "AutomationControlled" in page_content:
                print("\n⚠️  Detected 'AutomationControlled' warning")
            if "privacy related extensions" in page_content:
                print("\n⚠️  Detected 'privacy extensions' warning")
    
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print("\nTaking screenshot of what was loaded...")
        try:
            scraper.page.screenshot(path="test_error.png", full_page=True)
            print("Screenshot saved: test_error.png")
        except:
            print("Could not save screenshot")
    
    print("\nPress ENTER to close browser...")
    input()
    
    scraper.close()
    print("✅ Test complete!")

if __name__ == "__main__":
    test_browser()