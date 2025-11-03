"""
This is a one-time-use script to create a robust authentication file.
It will launch a browser, you log in to X manually, and then press Enter.
It saves your *entire* session (cookies, local storage, etc.) to the
auth/session_cookie.json file, which bypasses all login checks.
"""
import time
from playwright.sync_api import sync_playwright
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
AUTH_FILE = os.path.join(PROJECT_ROOT, 'auth', 'session_cookie.json')

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("="*50)
        print("ACTION REQUIRED:")
        print("A browser window has opened. Please log in to X (Twitter) manually.")
        print("After you are successfully logged in and see your timeline,")
        print("come back here and press the [Enter] key to continue.")
        print("="*50)
        
        page.goto("https://twitter.com/login")
        
        # Wait for the user to log in
        input() # This pauses the script until you press Enter
        
        # Save the entire session state
        context.storage_state(path=AUTH_FILE)
        
        print(f"Successfully saved authentication state to {AUTH_FILE}")
        browser.close()

if __name__ == "__main__":
    # First, let's clear the old, incorrectly formatted file
    if os.path.exists(AUTH_FILE):
        os.remove(AUTH_FILE)
        print(f"Removed old {AUTH_FILE}.")
        
    main()