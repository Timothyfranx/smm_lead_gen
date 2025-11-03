"""
ULTRA STEALTH Scraper - Uses undetected-playwright to bypass X detection
Replace your current scraper.py with this version
"""

import time
import logging
import json
import os
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page, BrowserContext, Browser
from src import config, utils

# --- CONSTANTS ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTH_DIR = os.path.join(PROJECT_ROOT, 'auth')
ACCOUNTS_DIR = os.path.join(AUTH_DIR, 'accounts')

X_BASE_URL = "https://twitter.com"
X_SEARCH_URL = "https://twitter.com/search?q={query}&f=user"

SCROLLS_PER_SEARCH = 5
SCROLLS_PER_PROFILE = 7

# --- SELECTORS ---
USER_SEARCH_CARD_SELECTORS = [
    '[data-testid="UserCell"]',
    'div[data-testid="cellInnerDiv"]:has(a[href*="/"])',
    'article[data-testid="UserCell"]',
]

USER_HANDLE_SELECTORS = [
    'a[href^="/"][role="link"]',
    'div[data-testid="User-Name"] a',
    'a[href*="/"]:not([href*="search"]):not([href*="explore"])',
]

USER_BIO_SELECTOR = '[data-testid="UserDescription"]'
FOLLOWER_COUNT_SELECTOR = 'a[href$="/verified_followers"] span, a[href$="/followers"] span'
TWEET_COUNT_SELECTOR = 'div[data-testid="UserProfileHeader_Items"] span'
TWEET_CONTAINER_SELECTOR = 'article[data-testid="tweet"]'
TWEET_TEXT_SELECTOR = '[data-testid="tweetText"]'
TWEET_TIMESTAMP_SELECTOR = 'time[datetime]'


class Scraper:
    """ULTRA Stealth Scraper - Maximum anti-detection"""
    
    def __init__(self, headless: bool = True, account_name: str = "default"):
        self.logger = logging.getLogger(__name__)
        self.headless = headless
        self.account_name = account_name
        self.playwright = None
        self.browser: Browser = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.debug_mode = False
        
        os.makedirs(ACCOUNTS_DIR, exist_ok=True)

    def setup_new_account(self, account_name: str = "default"):
        """ONE-TIME SETUP: Login manually and save browser state"""
        self.logger.info(f"🔧 Setting up new account: {account_name}")
        
        try:
            from undetected_playwright.sync_api import sync_playwright as stealth_playwright
            use_stealth = True
            self.logger.info("✅ Using undetected-playwright (stealth mode)")
        except ImportError:
            self.logger.warning("⚠️  undetected-playwright not found, using regular playwright")
            use_stealth = False
        
        pw = stealth_playwright() if use_stealth else sync_playwright()
        self.playwright = pw.start()
        
        self.browser = self.playwright.chromium.launch(
            headless=False,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='en-US',
        )
        
        self.page = self.context.new_page()
        
        self.logger.info("Opening X login page...")
        self.page.goto("https://twitter.com/login", wait_until="domcontentloaded")
        
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
        
        self.context.close()
        self.browser.close()
        self.playwright.stop()
        
        return True

    def _load_account_state(self, account_name: str = "default") -> bool:
        """Load saved browser state with maximum stealth"""
        try:
            state_file_path = os.path.join(ACCOUNTS_DIR, f'{account_name}_state.json')
            
            if not os.path.exists(state_file_path):
                self.logger.error(f"❌ Account '{account_name}' not found!")
                return False

            self.logger.info(f"Loading account: {account_name}")
            
            # Initialize regular Playwright (undetected-playwright 0.3.0 is outdated)
            self.playwright = sync_playwright().start()
            
            # Use REAL Chrome instead of Chromium
            self.logger.info("🔥 Using real Chrome browser (better for stealth)")
            
            try:
                # Try to use installed Chrome
                self.browser = self.playwright.chromium.launch(
                    headless=self.headless,
                    channel='chrome',  # Use real Chrome
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                    ]
                )
                self.logger.info("✅ Using Chrome browser")
            except Exception as e:
                self.logger.warning(f"Chrome not found ({e}), using Chromium")
                self.browser = self.playwright.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-blink-features=AutomationControlled',
                    ]
                )
            
            self.context = self.browser.new_context(
                storage_state=state_file_path,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                ignore_https_errors=True,
            )
            
            self.page = self.context.new_page()
            
            # Add comprehensive anti-detection
            self.page.add_init_script("""
                // Remove webdriver
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                
                // Fix plugins
                Object.defineProperty(navigator, 'plugins', { 
                    get: () => {
                        return [
                            { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                            { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                            { name: 'Native Client', filename: 'internal-nacl-plugin' }
                        ];
                    }
                });
                
                // Fix languages
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                
                // Add chrome object
                window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {} };
                
                // Fix permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Fix hardware
                Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
                Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
                
                // Fix vendor
                Object.defineProperty(navigator, 'vendor', { get: () => 'Google Inc.' });
                Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
                
                // Fix connection
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 50,
                        downlink: 10,
                        saveData: false
                    })
                });
            """)
            
            self.logger.info(f"✅ Account '{account_name}' loaded")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading account: {e}")
            return False

    def _check_for_errors(self) -> bool:
        """Check if X is showing VISIBLE error messages (not just in HTML source)"""
        try:
            # Only check for VISIBLE error messages that users can see
            visible_errors = [
                'text="Something went wrong"',
                'text="privacy related extensions may cause issues"',
            ]
            
            for error_selector in visible_errors:
                try:
                    error_elem = self.page.locator(error_selector)
                    if error_elem.is_visible(timeout=2000):
                        self.logger.error(f"❌ Visible error detected: {error_selector}")
                        return False
                except:
                    # Error not found - that's good!
                    pass
            
            # Check if we're on an actual error page (not just word in source)
            current_url = self.page.url
            if "error" in current_url or "suspended" in current_url:
                self.logger.error(f"❌ Error URL detected: {current_url}")
                return False
            
            # If we can see the compose button or profile link, we're definitely logged in
            try:
                compose_btn = self.page.locator('[data-testid="SideNav_NewTweet_Button"]')
                if compose_btn.is_visible(timeout=3000):
                    self.logger.info("✅ No errors - compose button visible")
                    return True
            except:
                pass
            
            try:
                profile_link = self.page.locator('a[data-testid="AppTabBar_Profile_Link"]')
                if profile_link.is_visible(timeout=3000):
                    self.logger.info("✅ No errors - profile link visible")
                    return True
            except:
                pass
            
            # If no errors found and we can see navigation elements, we're good
            self.logger.info("✅ No visible errors detected")
            return True
            
        except Exception as e:
            self.logger.warning(f"Error check failed (assuming OK): {e}")
            return True

    def _verify_login(self) -> bool:
        """Check if we're logged in"""
        if not self.page:
            return False
        
        try:
            self.logger.info("Verifying login...")
            self.page.goto("https://twitter.com/home", wait_until="load", timeout=90000)  # Increased timeout
            time.sleep(10)  # Give it more time to fully load
            
            if not self._check_for_errors():
                screenshot_path = os.path.join(PROJECT_ROOT, f"error_{self.account_name}.png")
                self.page.screenshot(path=screenshot_path, full_page=True)
                self.logger.error(f"Screenshot: {screenshot_path}")
                return False
            
            current_url = self.page.url
            self.logger.info(f"Current URL: {current_url}")
            
            if "login" in current_url.lower():
                self.logger.error("❌ Redirected to login!")
                return False
            
            # Look for compose button
            try:
                compose = self.page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=10000)
                if compose:
                    self.logger.info("✅ LOGIN VERIFIED!")
                    return True
            except:
                pass
            
            # Alternative check
            try:
                profile = self.page.wait_for_selector('a[data-testid="AppTabBar_Profile_Link"]', timeout=10000)
                if profile:
                    self.logger.info("✅ LOGIN VERIFIED!")
                    return True
            except:
                pass
            
            self.logger.warning("⚠️  Login status unclear, continuing...")
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying login: {e}")
            return False

    def _wait_for_search_results(self, query: str) -> bool:
        """Wait for search results to load"""
        try:
            self.logger.info("Waiting for search results...")
            
            # Check for errors
            if not self._check_for_errors():
                return False
            
            # Try multiple selectors
            selectors = [
                '[data-testid="UserCell"]',
                'div[data-testid="cellInnerDiv"]',
                'article',
            ]
            
            for selector in selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=15000, state='visible')
                    self.logger.info(f"✅ Found results with: {selector}")
                    return True
                except:
                    continue
            
            self.logger.warning("⚠️  No results found")
            screenshot_path = os.path.join(PROJECT_ROOT, f"no_results_{query.replace(' ', '_')}.png")
            self.page.screenshot(path=screenshot_path, full_page=True)
            self.logger.warning(f"Screenshot: {screenshot_path}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error waiting for results: {e}")
            return False

    def _find_user_cards(self) -> list:
        """Find user cards"""
        if not self.page:
            return []
        
        for selector in USER_SEARCH_CARD_SELECTORS:
            try:
                cards = self.page.query_selector_all(selector)
                if len(cards) > 0:
                    self.logger.info(f"✅ Found {len(cards)} cards")
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
                        handle = href.strip('/').split('/')[-1]
                        if handle and len(handle) > 0 and not handle.startswith('?'):
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
                pass
            
            return {
                "handle": handle,
                "profile_url": profile_url,
                "bio": bio
            }
        except:
            return None

    def _get_profile_details(self, profile_url: str) -> Optional[dict]:
        """Visit profile and scrape details"""
        if not self.page:
            return None

        self.logger.info(f"Visiting: {profile_url}")
        try:
            self.page.goto(profile_url, wait_until="load", timeout=60000)
            time.sleep(4)

            # Get follower count
            follower_count = 0
            try:
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
            except:
                pass
            
            # Apply filter
            if not (config.FOLLOWER_FILTER['MIN'] <= follower_count <= config.FOLLOWER_FILTER['MAX']):
                self.logger.info(f"Skipping: follower count ({follower_count}) out of range")
                return None
            
            # Scrape tweets (simplified for speed)
            tweets = []
            seen_timestamps = set()
            
            for scroll in range(SCROLLS_PER_PROFILE):
                tweet_elements = self.page.query_selector_all(TWEET_CONTAINER_SELECTOR)
                
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
                        
                        if len(tweets) >= config.TWEETS_TO_SCRAPE:
                            break
                    except:
                        continue
                
                if len(tweets) >= config.TWEETS_TO_SCRAPE:
                    break
                
                self.page.evaluate("window.scrollBy(0, 2000)")
                time.sleep(3)
            
            return {
                "follower_count": follower_count,
                "total_tweets": len(tweets),
                "tweets": tweets
            }

        except Exception as e:
            self.logger.error(f"Failed to scrape profile: {e}")
            return None

    def run(self, account_name: str = "default") -> List[Dict]:
        """Main scraping pipeline"""
        self.logger.info(f"Starting scraper with account: {account_name}")
        self.account_name = account_name
        
        if not self._load_account_state(account_name):
            self.logger.critical("Failed to load account!")
            return []

        if not self._verify_login():
            self.logger.critical("❌ LOGIN FAILED!")
            return []

        all_raw_leads = []
        
        for query in config.SEARCH_QUERIES:
            self.logger.info(f"--- Processing: '{query}' ---")
            search_url = X_SEARCH_URL.format(query=query.replace(" ", "%20"))
            
            try:
                self.logger.info(f"Navigating to: {search_url}")
                self.page.goto(search_url, wait_until="load", timeout=60000)
                time.sleep(8)
                
                if not self._wait_for_search_results(query):
                    self.logger.warning(f"No results for '{query}', skipping...")
                    continue
                
                potential_profiles = []
                seen_handles = set()
                
                for scroll_num in range(SCROLLS_PER_SEARCH):
                    self.logger.info(f"Scroll {scroll_num + 1}/{SCROLLS_PER_SEARCH}")
                    
                    user_cards = self._find_user_cards()
                    self.logger.info(f"Found {len(user_cards)} elements")
                    
                    for card in user_cards:
                        profile_data = self._pre_filter_user(card)
                        
                        if profile_data and profile_data['handle'] not in seen_handles:
                            potential_profiles.append(profile_data)
                            seen_handles.add(profile_data['handle'])
                            self.logger.info(f"  ✅ @{profile_data['handle']}")
                    
                    self.page.evaluate("window.scrollBy(0, 2000)")
                    time.sleep(5)
                
                self.logger.info(f"Found {len(potential_profiles)} profiles")

                # Deep scrape
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
                        self.logger.info(f"SUCCESS: @{profile['handle']}")
                    
                    time.sleep(3)

            except Exception as e:
                self.logger.error(f"Failed query '{query}': {e}")
            
            time.sleep(5)

        self.logger.info(f"Finished. Found {len(all_raw_leads)} leads.")
        return all_raw_leads

    def close(self):
        """Shutdown"""
        self.logger.info("Shutting down...")
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


def run_with_rotation(account_names: List[str]) -> List[Dict]:
    """Run scraper with account rotation"""
    logger = logging.getLogger(__name__)
    all_leads = []
    
    for account_name in account_names:
        logger.info(f"\n{'='*60}")
        logger.info(f"Trying account: {account_name}")
        logger.info(f"{'='*60}\n")
        
        scraper = Scraper(headless=False, account_name=account_name)
        
        try:
            leads = scraper.run(account_name)
            
            if len(leads) > 0:
                logger.info(f"✅ Success: {len(leads)} leads")
                all_leads.extend(leads)
                scraper.close()
                break
            else:
                logger.warning(f"⚠️  0 leads, trying next account...")
                scraper.close()
                
        except Exception as e:
            logger.error(f"❌ Account failed: {e}")
            scraper.close()
            continue
    
    return all_leads