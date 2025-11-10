"""
This is a one-time-use script to create a robust authentication file.
It will launch a browser, you log in to X manually, and then press Enter.
It saves your *entire* session (cookies, local storage, etc.) to the
auth/session_cookie.json file, which bypasses all login checks.

THIS IS THE UPDATED VERSION to bypass bot detection.
"""
import time
from playwright.sync_api import sync_playwright
import os
import shutil  # Import for deleting directories

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
AUTH_FILE = os.path.join(PROJECT_ROOT, 'auth', 'session_cookie.json')
# We will create a temporary, persistent profile for this login
USER_DATA_DIR = os.path.join(PROJECT_ROOT, 'temp_chrome_profile')

def main():
    # --- Clean up old session and profile ---
    if os.path.exists(AUTH_FILE):
        os.remove(AUTH_FILE)
        print(f"Removed old {AUTH_FILE}.")
    if os.path.exists(USER_DATA_DIR):
        print(f"Removing old temporary profile at {USER_DATA_DIR}...")
        try:
            shutil.rmtree(USER_DATA_DIR)
            print("Successfully removed old profile.")
        except Exception as e:
            print(f"Warning: Could not remove old profile. It might be in use. Error: {e}")
            print("Please close any open Chrome windows and try again.")
            return
    # --- ---

    with sync_playwright() as p:
        print("Launching 'human-like' browser (persistent context)...")
        # Launch a PERSISTENT context. This is much harder to detect.
        # It uses a dedicated user data directory to store cookies, etc.,
        # just like a real browser profile.
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False,
            # --- Arguments to make it look more human ---
            args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized',
            ],
            # Use a common user agent to blend in
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()
        
        print("="*50)
        print("ACTION REQUIRED:")
        print("A 'human-like' browser window has opened. Please log in to X (Twitter) manually.")
        print("Go through the full login (username, password, any 2FA).")
        print("After you are successfully logged in and see your timeline,")
        print("come back here and press the [Enter] key to continue.")
        print("="*50)
        
        try:
            page.goto("https://twitter.com/login", timeout=60000)
        except Exception as e:
            print(f"Error navigating to login page: {e}")
            print("Please check your internet connection.")
            context.close()
            return
            
        # Wait for the user to log in
        input() # This pauses the script until you press Enter
        
        try:
            # Save the entire session state
            context.storage_state(path=AUTH_FILE)
            print(f"Successfully saved authentication state to {AUTH_FILE}")
        except Exception as e:
            print(f"Error saving authentication state: {e}")
        finally:
            context.close()
            print("Browser context closed.")

    # Clean up the temporary profile directory after we're done
    if os.path.exists(USER_DATA_DIR):
        try:
            shutil.rmtree(USER_DATA_DIR)
            print(f"Successfully cleaned up temporary profile: {USER_DATA_DIR}")
        except Exception as e:
            print(f"Warning: Could not clean up {USER_DATA_DIR}. You may need to delete it manually. Error: {e}")

if __name__ == "__main__":
    main()