"""
This is the utility file ("toolbox") for the SMM Lead Generation Bot.
It contains helper functions for tasks like logging, data saving,
and other common operations.
"""

import logging
import pandas as pd
import os
from datetime import datetime

# Define the root directory of the project
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, 'data', 'outputs')

# Ensure the output directory exists
os.makedirs(OUTPUTS_DIR, exist_ok=True)


def setup_logging():
    """Configures the root logger for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # Silence the noisy "playwright" logs, we only care about our own
    logging.getLogger("playwright").setLevel(logging.WARNING)
    return logging.getLogger(__name__)


def save_leads_to_csv(leads_df: pd.DataFrame, filename: str = "latest_leads.csv"):
    """
    Saves the final DataFrame of leads to a CSV file in the data/outputs/ folder.

    Args:
        leads_df (pd.DataFrame): The pandas DataFrame containing the filtered leads.
        filename (str): The name of the file to save. We default to 'latest_leads.csv'
                        for the Telegram bot, but a timestamped one could also be used.
    """
    logger = logging.getLogger(__name__)
    
    if leads_df.empty:
        logger.warning("No leads found to save. DataFrame is empty.")
        return None

    # We use the 'latest_leads.csv' as the primary file for the bot
    latest_filepath = os.path.join(OUTPUTS_DIR, filename)
    
    # Also save a timestamped backup for historical records
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"leads_{timestamp}.csv"
    backup_filepath = os.path.join(OUTPUTS_DIR, backup_filename)

    try:
        # Save the main "latest" file
        leads_df.to_csv(latest_filepath, index=False, encoding='utf-8')
        logger.info(f"Successfully saved {len(leads_df)} leads to {latest_filepath}")

        # Save the historical backup
        leads_df.to_csv(backup_filepath, index=False, encoding='utf-8')
        logger.info(f"Historical backup saved to {backup_filepath}")
        
        return latest_filepath

    except Exception as e:
        logger.error(f"Failed to save leads to CSV: {e}")
        return None

# Example of how this might be used (don't run this file directly)
if __name__ == "__main__":
    # This block is for testing the functions
    logger = setup_logging()
    logger.info("Testing util functions...")
    
    # Create a dummy DataFrame
    test_data = {
        'handle': ['@testuser1', '@testuser2'],
        'followers': [1000, 2000],
        'activity_status': ['Paused', 'Active']
    }
    df = pd.DataFrame(test_data)
    
    # Test saving
    save_leads_to_csv(df)