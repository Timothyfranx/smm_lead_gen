"""
This is the "Strategist" (analyzer.py) module.
Its job is to:
1. Take the "raw data" list from the Scraper.
2. Load it into a pandas DataFrame.
3. Apply all the complex business logic from config.py:
    - Classify accounts ('Person' or 'Project').
    - Analyze activity gaps ('Paused', 'Dormant').
    - Categorize follower tiers ('Tier 1', 'Tier 2').
    - Find and list all matched keywords from bios and tweets.
4. Output a clean, sorted, final DataFrame ready to be saved as a CSV.
"""

import logging
import pandas as pd
import regex  # Using 'regex' for more advanced features like word boundaries
from datetime import datetime, timezone
from typing import List, Dict

# Import our "brain"
from src import config


class Analyzer:
    """
    The Analyzer class encapsulates all data transformation and business logic.
    """
    
    def __init__(self, raw_data_list: List[Dict]):
        self.logger = logging.getLogger(__name__)
        if not raw_data_list:
            self.logger.warning("Analyzer initialized with empty raw data list.")
            self.df = pd.DataFrame()
        else:
            self.df = pd.DataFrame(raw_data_list)
        
        # --- Pre-compile all regex patterns for massive speed improvement ---
        self.patterns = {
            # Persona 1: Founder
            'founder_bio': self._compile_pattern_list(config.FOUNDER_BIO_KEYWORDS),
            'founder_tweet': self._compile_pattern_list(config.FOUNDER_TWEET_KEYWORDS),
            
            # Persona 2: Project
            'project_bio': self._compile_pattern_list(config.PROJECT_BIO_KEYWORDS),
            'project_tweet': self._compile_pattern_list(config.PROJECT_TWEET_KEYWORDS),
            
            # General
            'general_bio': self._compile_pattern_list(config.GENERAL_BIO_KEYWORDS),
            'high_intent_tweet': self._compile_pattern_list(config.HIGH_INTENT_TWEET_KEYWORDS)
        }

    def _compile_pattern_list(self, keywords: list) -> regex.Pattern:
        """Helper to create a single, case-insensitive regex pattern from a list."""
        # \b ensures we match whole words (e.g., "ai" not "train")
        pattern_str = r'\b(' + '|'.join(regex.escape(k) for k in keywords) + r')\b'
        return regex.compile(pattern_str, flags=regex.IGNORECASE | regex.UNICODE)

    def _classify_account_type(self, bio: str) -> str:
        """Classifies account as 'Person' or 'Project' based on bio."""
        if not isinstance(bio, str):
            return 'Unknown'
        
        # Check for 'Person' keywords first, as they are more specific
        if self.patterns['founder_bio'].search(bio):
            return 'Person'
        
        # Then check for 'Project' keywords
        if self.patterns['project_bio'].search(bio):
            return 'Project'
        
        return 'Unknown'

    def _analyze_activity(self, tweets_list: list) -> pd.Series:
        """Parses tweet list to find activity status and days since last post."""
        if not tweets_list or not isinstance(tweets_list, list):
            return pd.Series({'activity_status': 'No Tweets Found', 'days_since_last_post': -1})
        
        try:
            # The scraper sorts tweets by most recent, so [0] is the latest
            last_tweet_timestamp = tweets_list[0]['timestamp']
            
            # Parse ISO 8601 format: "2025-10-28T10:00:00.000Z"
            last_tweet_time = datetime.fromisoformat(last_tweet_timestamp.replace('Z', '+00:00'))
            
            now = datetime.now(timezone.utc)
            days_gap = (now - last_tweet_time).days
            
            # Find the correct status from our config
            for status, (min_days, max_days) in config.ACTIVITY_GAPS.items():
                if min_days <= days_gap <= max_days:
                    return pd.Series({'activity_status': status, 'days_since_last_post': days_gap})
            
            # Default to Dormant if it's over the max (e.g., > 90)
            return pd.Series({'activity_status': 'Dormant', 'days_since_last_post': days_gap})

        except Exception as e:
            self.logger.warning(f"Error parsing tweet timestamp: {e}. Data: {tweets_list[0]}")
            return pd.Series({'activity_status': 'Error', 'days_since_last_post': -1})

    def _categorize_followers(self, followers: int) -> str:
        """Assigns a "Follower Tier" based on the count."""
        if not isinstance(followers, (int, float)):
            return 'N/A'
        
        for tier, (min_f, max_f) in config.FOLLOWER_TIERS.items():
            if min_f <= followers <= max_f:
                return tier
        
        # If they are outside our defined tiers but within the filter
        if followers < config.FOLLOWER_TIERS['Tier 1'][0]:
            return 'Tier 0 (Sub-500)'
        return 'N/A'

    def _find_matched_keywords(self, text: str, patterns_to_check: List[regex.Pattern]) -> list:
        """Finds all unique keywords from a list of patterns in a text block."""
        if not isinstance(text, str):
            return []
        
        matches = set()
        for pattern in patterns_to_check:
            found_keywords = pattern.findall(text)
            # Add the lowercase version of each found keyword to the set
            matches.update([k.lower() for k in found_keywords])
            
        return list(matches)

    def run_analysis(self) -> pd.DataFrame:
        """
        Runs the full analysis pipeline on the DataFrame.
        """
        if self.df.empty:
            self.logger.warning("Analyzer DataFrame is empty. Aborting analysis.")
            return pd.DataFrame()
            
        self.logger.info(f"Analyzing {len(self.df)} raw profiles...")

        # 1. Classify Account Type
        self.df['account_type'] = self.df['bio'].apply(self._classify_account_type)

        # 2. Analyze Activity
        activity_data = self.df['tweets'].apply(self._analyze_activity)
        self.df = pd.concat([self.df, activity_data], axis=1)

        # 3. Categorize Followers
        self.df['follower_tier'] = self.df['follower_count'].apply(self._categorize_followers)

        # 4. Find Matched Bio Keywords
        self.df['matched_bio_keywords'] = self.df['bio'].apply(
            lambda x: self._find_matched_keywords(
                x, [self.patterns['founder_bio'], self.patterns['project_bio'], self.patterns['general_bio']]
            )
        )

        # 5. Find Matched Tweet Keywords
        # First, combine all tweet texts into one giant string for analysis
        self.df['all_tweets_text'] = self.df['tweets'].apply(
            lambda t_list: " ".join([t['text'] for t in t_list if isinstance(t, dict) and 'text' in t])
        )
        self.df['matched_tweet_keywords'] = self.df['all_tweets_text'].apply(
            lambda x: self._find_matched_keywords(
                x, [self.patterns['founder_tweet'], self.patterns['project_tweet'], self.patterns['high_intent_tweet']]
            )
        )
        
        # TODO: Engagement Analysis
        # The current scraper.py does *not* scrape like/retweet counts, as they
        # are harder to get and make the scrape less stable.
        # To enable this, scraper.py would need to be upgraded to find those
        # selectors, and this class would need a new _analyze_engagement() method.
        # self.df['engagement_ratio'] = 0.0 # Placeholder

        # 6. Final Cleanup and Column Selection
        self.logger.info("Analysis complete. Cleaning up DataFrame...")
        
        final_columns = [
            'handle',
            'account_type',
            'follower_count',
            'follower_tier',
            'activity_status',
            'days_since_last_post',
            'total_tweets',
            'matched_bio_keywords',
            'matched_tweet_keywords',
            'bio',
            'profile_url'
        ]
        
        # Ensure all columns exist before trying to select them
        final_df = self.df[[col for col in final_columns if col in self.df.columns]].copy()
        
        # Sort to show the best leads first:
        # We want "Paused" or "Dormant" accounts with high follower counts.
        final_df = final_df.sort_values(
            by=['activity_status', 'follower_count'],
            ascending=[False, False]
        )

        return final_df