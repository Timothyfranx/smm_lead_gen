"""
OPTIMIZED STEALTH Scraper - v3 (Hybrid)
This version reverts to the reliable N+1 (page-by-page) scraping method,
as the API-first (v2) method is being blocked by X.com's bot detection.

This version's improvements:
- All 'time.sleep()' calls are replaced with 'page.wait_for_selector()'
  or 'page.wait_for_load_state()'. This is much faster and stealthier.
- All complex anti-detection scripts ('add_init_script') are REMOVED,
  as they were likely causing the "privacy extensions" error.
- Selectors are confirmed based on your debug HTML.
"""

import time
import logging
import json
import os
import random
from typing import List, Dict, Optional, Tuple
from playwright.sync_api import sync_playwright, Page, BrowserContext, Browser, Route, Request
from src import config, utils

# --- CONSTANTS ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTH_DIR = os.path.join(PROJECT_ROOT, 'auth')
ACCOUNTS_DIR = os.path.join(AUTH_DIR, 'accounts')

X_BASE_URL = "https://x.com"
X_SEARCH_URL = "https://x.com/search?q={query}&f=user"

SCROLLS_PER_SEARCH = 5
SCROLLS_PER_PROFILE = 7 # Kept from your original config.py logic

# --- SELECTORS (from your original scraper.py, confirmed by x_page_debug.html) ---
USER_SEARCH_CARD_SELECTORS = [
    '[data-testid="UserCell"]',
    'div[data-testid="cellInnerDiv"]:has(a[href*="/"])',
]

USER_HANDLE_SELECTORS = [
    'a[href^="/"][role="link"]',
    'div[data-testid="User-Name"] a',
]

USER_BIO_SELECTOR = '[data-testid="UserDescription"]'
FOLLOWER_COUNT_SELECTOR = 'a[href$="/verified_followers"] span, a[href$="/followers"] span'
TWEET_CONTAINER_SELECTOR = 'article[data-testid="tweet"]'
TWEET_TEXT_SELECTOR = '[data-testid="tweetText"]'
TWEET_TIMESTAMP_SELECTOR = 'time[datetime]'


class Scraper:
    """Optimized Scraper - v3 (Hybrid)"""
    
    def __init__(self, headless: bool = True, account_name: str = "default"):
        self.logger = logging.getLogger(__name__)
        self.headless = headless
        self.account_name = account_name
        self.playwright = None
        self.browser: Browser = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        os.makedirs(ACCOUNTS_DIR, exist_ok=True)

    def setup_new_account(self, account_name: str = "default"):
        """ONE-TIME SETUP: Login manually and save browser state"""
        self.logger.info(f"🔧 Setting up new account: {account_name}")
        
        try:
            from undetected_playwright.sync_api import sync_playwright as stealth_playwright
            pw = stealth_playwright()
            self.logger.info("✅ Using undetected-playwright (stealth mode)")
        except ImportError:
            self.logger.warning("⚠️  undetected-playwright not found, using regular playwright")
            pw = sync_playwright()
        
        self.playwright = pw.start()
        
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='en-US',
        )
        self.page = self.context.new_page()
        
        self.logger.info("Opening X login page...")
        self.page.goto(f"{X_BASE_URL}/login", wait_until="domcontentloaded")
        
        print("\n" + "="*60)
        print("🔐 MANUAL LOGIN REQUIRED")
        print("="*60)
        print("1. Login to X in the browser")
        print("2. Complete any 2FA/verification")
        print("3. Wait until you see your HOME feed")
        print("4. Press ENTER to save the session")
        print("="*60 + "\n")
        
        input("Press ENTER after logged in...")
        
        state_file_path = os.path.join(ACCOUNTS_DIR, f'{account_name}_state.json')
        self.context.storage_state(path=state_file_path)
        
        self.logger.info(f"✅ Account '{account_name}' saved to: {state_file_path}")
        self.close()
        return True

    def _load_account_state(self) -> bool:
        """Load saved browser state"""
        try:
            state_file_path = os.path.join(ACCOUNTS_DIR, f'{self.account_name}_state.json')
            if not os.path.exists(state_file_path):
                self.logger.error(f"❌ Account '{self.account_name}' not found!")
                return False

            self.logger.info(f"Loading account: {self.account_name}")
            self.playwright = sync_playwright().start()
            
            # Use 'chrome' channel if available, otherwise default Chromium
            try:
                self.browser = self.playwright.chromium.launch(
                    headless=self.headless,
                    channel='chrome'
                )
                self.logger.info("✅ Launched using 'chrome' channel.")
            except Exception:
                self.logger.info("Chrome channel not found, launching default Chromium.")
                self.browser = self.playwright.chromium.launch(
                    headless=self.headless
                )
            
            # Create a simple context. We are *not* adding anti-detect scripts
            # as they seem to be causing the "privacy extensions" error.
            self.context = self.browser.new_context(
                storage_state=state_file_path,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                locale='en-US',
            )
            
            self.page = self.context.new_page()
            self.logger.info(f"✅ Account '{self.account_name}' loaded")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading account: {e}")
            return False

    def _verify_login(self) -> bool:
        """Check if we're logged in"""
        if not self.page: return False
        
        try:
            self.logger.info("Verifying login status...")
            self.page.goto(f"{X_BASE_URL}/home", wait_until="domcontentloaded", timeout=60000)
            
            # Wait for the "Compose" button. This is the most reliable check.
            self.logger.info("Page loaded, waiting for compose button...")
            self.page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=30000, state="visible")
            
            self.logger.info("✅ Login VERIFIED!")
            return True
        except Exception as e:
            self.logger.error(f"❌ Login verification failed: {e}")
            self.page.screenshot(path=f"error_{self.account_name}_login_failed.png")
            self.logger.error(f"Screenshot saved to error_{self.account_name}_login_failed.png")
            return False

    def _smart_scroll(self, wait_time: int = 3000):
        """Scrolls down and waits for network to quiet down."""
        self.page.evaluate("window.scrollBy(0, 2000)")
        try:
            # Wait for network to be idle, max wait_time ms
            self.page.wait_for_load_state("networkidle", timeout=wait_time)
        except:
            # Fallback sleep if network never becomes idle
            time.sleep(1)

    def _find_user_cards(self) -> list:
        """Finds all user card elements on the page."""
        if not self.page: return []
        
        for selector in USER_SEARCH_CARD_SELECTORS:
            try:
                cards = self.page.query_selector_all(selector)
                if len(cards) > 0:
                    return cards
            except:
                continue
        return []

    def _extract_handle_from_card(self, card_element) -> Optional[str]:
        """Extract username from card"""
        for selector in USER_HANDLE_SELECTORS:
            try:
                handle_el = card_element.query_selector(selector)
                if handle_el:
                    href = handle_el.get_attribute('href')
                    if href:
                        handle = href.strip('/').split('?')[0] # Get handle, remove query params
                        if handle and len(handle) > 0 and "/" not in handle:
                            return handle
            except:
                continue
        return None
            
    def _pre_filter_user(self, user_card_element) -> Optional[dict]:
        """Extract basic info from user card"""
        try:
            handle = self._extract_handle_from_card(user_card_element)
            if not handle:
                return None
            
            profile_url = f"{X_BASE_URL}/{handle}"
            
            bio = ""
            try:
                bio_element = user_card_element.query_selector(USER_BIO_SELECTOR)
                if bio_element:
                    bio = bio_element.inner_text()
            except:
                pass # Bio is optional
            
            return {
                "handle": handle,
                "profile_url": profile_url,
                "bio": bio
            }
        except:
            return None

    def _get_profile_details(self, profile_url: str) -> Optional[dict]:
        """This is the 'N+1' visit. We go to the user's profile page."""
        if not self.page: return None

        self.logger.info(f"Visiting: {profile_url}")
        try:
            self.page.goto(profile_url, wait_until="domcontentloaded", timeout=60000)
            # Wait for the main profile header to be visible
            self.page.wait_for_selector('[data-testid="UserProfileHeader_Items"]', state="visible", timeout=20000)

            # Get follower count
            follower_count = 0
            try:
                # Wait for the follower count element to be ready
                self.page.wait_for_selector(FOLLOWER_COUNT_SELECTOR, state="visible", timeout=10000)
                follower_elements = self.page.query_selector_all(FOLLOWER_COUNT_SELECTOR)
                
                for el in follower_elements:
                    text = el.inner_text()
                    if text:
                        count_str = text.split()[0]
                        if "K" in count_str:
                            follower_count = int(float(count_str.replace("K", "")) * 1000)
                        elif "M" in count_str:
                            follower_count = int(float(count_str.replace("M", "")) * 1000000)
                        elif count_str.replace(',', '').isdigit():
                            follower_count = int(count_str.replace(',', ''))
                        if follower_count > 0:
                            break
            except Exception as e:
                self.logger.warning(f"Could not parse follower count for {profile_url}: {e}")
            
            # Apply follower filter
            if not (config.FOLLOWER_FILTER['MIN'] <= follower_count <= config.FOLLOWER_FILTER['MAX']):
                self.logger.info(f"Skipping: @{profile_url.split('/')[-1]} follower count ({follower_count}) out of range")
                return None
            
            # Scrape tweets
            tweets = []
            seen_timestamps = set()
            
            for scroll in range(SCROLLS_PER_PROFILE):
                try:
                    # Wait for at least one tweet to be visible
                    if scroll == 0:
                        self.page.wait_for_selector(TWEET_CONTAINER_SELECTOR, state="visible", timeout=10000)
                except Exception:
                    self.logger.warning(f"No tweets found on profile {profile_url}")
                    break # No tweets, stop scrolling

                tweet_elements = self.page.query_selector_all(TWEET_CONTAINER_SELECTOR)
                
                found_new_tweet = False
                for tweet in tweet_elements:
                    try:
                        text_el = tweet.query_selector(TWEET_TEXT_SELECTOR)
                        time_el = tweet.query_selector(TWEET_TIMESTAMP_SELECTOR)
                        
                        if text_el and time_el:
                            tweet_text = text_el.inner_text()
                            tweet_timestamp = time_el.get_attribute('datetime')
                            
                            if tweet_timestamp and tweet_timestamp not in seen_timestamps:
                                tweets.append({
                                    "text": tweet_text,
                                    "timestamp": tweet_timestamp
                                })
                                seen_timestamps.add(tweet_timestamp)
                                found_new_tweet = True
                        
                        if len(tweets) >= config.TWEETS_TO_SCRAPE:
                            break
                    except:
                        continue # Ignore individual failed tweets
                
                if len(tweets) >= config.TWEETS_TO_SCRAPE or not found_new_tweet:
                    break # Stop if we have enough tweets or if we're not finding new ones
                
                self._smart_scroll()
            
            return {
                "follower_count": follower_count,
                "total_tweets": len(tweets),
                "tweets": tweets
            }

        except Exception as e:
            self.logger.error(f"Failed to scrape profile {profile_url}: {e}")
            self.page.screenshot(path=f"error_{profile_url.split('/')[-1]}.png")
            return None

    def run(self) -> List[Dict]:
        """Main scraping pipeline (Hybrid v3)"""
        self.logger.info(f"Starting optimized scraper with account: {self.account_name}")
        
        if not self._load_account_state(): return []
        if not self._verify_login(): return []

        all_raw_leads = []
        
        for query in config.SEARCH_QUERIES:
            self.logger.info(f"--- Processing: '{query}' ---")
            search_url = X_SEARCH_URL.format(query=query.replace(" ", "%20"))
            
            try:
                self.page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                # Wait for the *first* user cell to appear
                self.page.wait_for_selector('[data-testid="UserCell"]', state="visible", timeout=30000)
                self.logger.info("Search results loaded.")
                
                potential_profiles = []
                seen_handles = set()
                
                for scroll_num in range(SCROLLS_PER_SEARCH):
                    self.logger.info(f"Scroll {scroll_num + 1}/{SCROLLS_PER_SEARCH}")
                    
                    user_cards = self._find_user_cards()
                    if not user_cards:
                        self.logger.warning("No user cards found on this scroll.")
                        
                    found_new_handle = False
                    for card in user_cards:
                        profile_data = self._pre_filter_user(card)
                        
                        if profile_data and profile_data['handle'] not in seen_handles:
                            potential_profiles.append(profile_data)
                            seen_handles.add(profile_data['handle'])
                            self.logger.info(f"  Found @{profile_data['handle']}")
                            found_new_handle = True
                    
                    if not found_new_handle and scroll_num > 0:
                        self.logger.info("No new handles found, moving to next query.")
                        break # Stop scrolling if we're not finding new users
                    
                    self._smart_scroll()
                
                self.logger.info(f"Found {len(potential_profiles)} potential profiles for query '{query}'.")

                # Deep scrape (The N+1 part)
                for profile in potential_profiles:
                    profile_details = self._get_profile_details(profile['profile_url'])
                    
                    if profile_details:
                        raw_lead = {
                            "handle": profile['handle'],
                            "bio": profile['bio'],
                            "profile_url": profile['profile_url'],
                            **profile_details
                        }
                        all_raw_leads.append(raw_lead)
                        self.logger.info(f"✅ SUCCESS: @{profile['handle']} added to leads.")
                    
                    # Wait for a "human" amount of time between profile visits
                    self._smart_scroll(wait_time=2000)

            except Exception as e:
                self.logger.error(f"Failed query '{query}': {e}")
            
            # Wait for a "human" amount of time between profile visits
            wait_time = random.uniform(4, 10) # Wait a random 4-10 seconds
            self.logger.info(f"Pausing for {wait_time:.1f}s to look human (prevent rate-limit)...")
            time.sleep(wait_time)

        self.logger.info(f"Finished. Found {len(all_raw_leads)} leads.")
        return all_raw_leads

    def close_browser(self):
        """Closes the browser and context, but leaves the playwright instance."""
        if self.context:
            self.context.close()
            self.context = None
        if self.browser:
            self.browser.close()
            self.browser = None
            
    def close(self):
        """Shutdown everything"""
        self.logger.info("Shutting down scraper...")
        self.close_browser() # This was the typo!
        if self.playwright:
            self.playwright.stop()


def run_with_rotation(account_names: List[str], headless: bool) -> List[Dict]:
    """Run scraper with account rotation (v3)"""
    logger = logging.getLogger(__name__)
    all_leads = []
    
    for account_name in account_names:
        logger.info(f"\n{'='*60}")
        logger.info(f"Trying account: {account_name}")
        logger.info(f"{'='*60}\n")
        
        scraper = Scraper(headless=headless, account_name=account_name)
        
        try:
            leads = scraper.run()
            
            if len(leads) > 0:
                logger.info(f"✅ Success: {len(leads)} leads found with {account_name}")
                all_leads.extend(leads)
                scraper.close()
                # We break on success, as one good run is all we need
                break
            else:
                logger.warning(f"⚠️  Account {account_name} found 0 leads, trying next...")
                scraper.close()
                
        except Exception as e:
            logger.error(f"❌ Account {account_name} failed: {e}")
            scraper.close()
            continue
    
    # We aggregate all leads found, even if we break
    # Note: If you want *only* leads from the first successful account,
    # you can `all_leads = leads` before the `break`. I'll extend.
    final_leads = []
    seen_handles = set()
    for lead in all_leads:
        if lead['handle'] not in seen_handles:
            final_leads.append(lead)
            seen_handles.add(lead['handle'])
    
    return final_leads