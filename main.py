"""
This is the main entry point for the SMM Lead Generation Bot.

This script orchestrates the entire process:
1. Sets up logging.
2. Initializes the Scraper (src/scraper.py) with authentication.
3. Runs the Scraper to get the raw data (supports account rotation).
4. Shuts down the Scraper to free resources.
5. Initializes the Analyzer (src/analyzer.py) with the raw data.
6. Runs the Analyzer to get the final, filtered DataFrame.
7. Saves the final leads to a CSV file (using src/utils.py).

NEW FEATURES:
- Multi-account support (add accounts via setup_accounts.py)
- Automatic account rotation if one fails
- Session persistence using storage_state
"""

import logging
from src import scraper, analyzer, utils


# ============================================
# CONFIGURATION - Edit these for your setup
# ============================================

# OPTION 1: Single account (simple but less resilient)
USE_SINGLE_ACCOUNT = False
SINGLE_ACCOUNT_NAME = "account1"

# OPTION 2: Account rotation (recommended for production)
USE_ACCOUNT_ROTATION = True
ACCOUNT_ROTATION_LIST = [
    "account1",
]

# Scraper settings
HEADLESS_MODE = False  # Set to False for debugging


def run_with_single_account(logger, account_name: str, headless: bool = True):
    """
    Run scraper with a single account (simpler but no failover)
    
    Args:
        logger: Logger instance
        account_name: Name of the account to use
        headless: Run browser in headless mode
        
    Returns:
        list: Raw leads data
    """
    bot_scraper = None
    raw_leads = []
    
    try:
        # Initialize the Scraper with account
        logger.info(f"Initializing scraper with account: '{account_name}'")
        bot_scraper = scraper.Scraper(headless=False, account_name=account_name)
        
        # Run the Scraper
        logger.info("Starting the 'Scout' (scraper.py)...")
        raw_leads = bot_scraper.run(account_name=account_name)
        logger.info(f"Scout finished. Found {len(raw_leads)} raw profiles.")
        
    except Exception as e:
        logger.critical(f"An error occurred during the scraping phase: {e}", exc_info=True)
        raw_leads = []
    
    finally:
        # Shut down the Scraper (CRITICAL to prevent zombie processes)
        if bot_scraper:
            bot_scraper.close()
            logger.info("Scraper has been shut down.")
    
    return raw_leads


def run_with_account_rotation(logger, account_list: list, headless: bool = True):
    """
    Run scraper with multiple accounts - automatically switches if one fails
    
    Args:
        logger: Logger instance
        account_list: List of account names to try
        headless: Run browser in headless mode
        
    Returns:
        list: Raw leads data
    """
    logger.info(f"Using account rotation with {len(account_list)} accounts: {account_list}")
    
    try:
        # Use the built-in rotation function
        raw_leads = scraper.run_with_rotation(account_list)
        logger.info(f"Scout finished. Found {len(raw_leads)} raw profiles.")
        return raw_leads
        
    except Exception as e:
        logger.critical(f"An error occurred during scraping with rotation: {e}", exc_info=True)
        return []


def main():
    """Main function to run the bot."""
    
    # 1. Setup Logging
    logger = utils.setup_logging()
    logger.info("="*70)
    logger.info("🚀 SMM Lead Gen Bot starting...")
    logger.info("="*70)
    
    # 2 & 3. Run the Scraper (with chosen strategy)
    raw_leads = []
    
    if USE_ACCOUNT_ROTATION:
        logger.info(f"📋 Mode: Account Rotation ({len(ACCOUNT_ROTATION_LIST)} accounts)")
        raw_leads = run_with_account_rotation(logger, ACCOUNT_ROTATION_LIST, HEADLESS_MODE)
    
    elif USE_SINGLE_ACCOUNT:
        logger.info(f"📋 Mode: Single Account ('{SINGLE_ACCOUNT_NAME}')")
        raw_leads = run_with_single_account(logger, SINGLE_ACCOUNT_NAME, HEADLESS_MODE)
    
    else:
        logger.error("❌ No scraping mode enabled! Set USE_SINGLE_ACCOUNT or USE_ACCOUNT_ROTATION to True")
        return
    
    # 4. Check if we have data to analyze
    if not raw_leads:
        logger.warning("⚠️  Scraper returned no raw leads. No analysis to perform.")
        logger.info("\nPossible reasons:")
        logger.info("  1. All accounts are suspended/expired")
        logger.info("  2. No accounts have been setup (run: python setup_accounts.py)")
        logger.info("  3. Search queries returned no results")
        logger.info("  4. X changed their HTML structure (selectors need updating)")
        logger.info("\n✅ SMM Lead Gen Bot run complete (with warnings).")
        return
    
    # 5. Analyze the raw leads
    try:
        # Initialize the Analyzer
        logger.info("\n" + "="*70)
        logger.info("Starting the 'Strategist' (analyzer.py)...")
        logger.info("="*70)
        bot_analyzer = analyzer.Analyzer(raw_leads)
        
        # Run the Analyzer
        final_leads_df = bot_analyzer.run_analysis()
        
        if not final_leads_df.empty:
            logger.info(f"\n✅ Analysis complete. Found {len(final_leads_df)} qualified leads.")
            
            # 6. Save the results
            logger.info("\nSaving results...")
            output_file = utils.save_leads_to_csv(final_leads_df)
            
            # Print summary
            logger.info("\n" + "="*70)
            logger.info(" SCRAPING COMPLETE - SUMMARY")
            logger.info("="*70)
            logger.info(f"  Raw profiles found:    {len(raw_leads)}")
            logger.info(f"  Qualified leads:       {len(final_leads_df)}")
            logger.info(f"  Conversion rate:       {len(final_leads_df)/len(raw_leads)*100:.1f}%")
            logger.info(f"  Output file:           {output_file}")
            logger.info("="*70)
            
        else:
            logger.warning("⚠️  Analysis finished, but no leads matched the final criteria.")
            logger.info("\nTips to improve results:")
            logger.info("  1. Adjust filters in config.py (follower count, keywords, etc.)")
            logger.info("  2. Try different search queries")
            logger.info("  3. Review analyzer.py scoring criteria")
            
    except Exception as e:
        logger.error(f"❌ An error occurred during the analysis phase: {e}", exc_info=True)
    
    logger.info("\n✅ SMM Lead Gen Bot run complete.")


# This makes the file runnable (e.g., `python main.py`)
if __name__ == "__main__":
    main()