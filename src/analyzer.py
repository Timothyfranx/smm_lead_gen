"""
SMART ANALYZER - v2.0
New features:
1. Posting pattern detection (erratic, sparse, daily, dormant)
2. Dual scoring system (Founders vs Projects scored differently)
3. Struggle keyword detection with tiering
4. Lead grading (A/B/C/F)
5. Detailed scoring reasons
"""

import logging
import pandas as pd
import regex
import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Tuple

from src import config


class Analyzer:
    """Smart Analyzer with posting pattern detection and dual scoring"""
    
    def __init__(self, raw_data_list: List[Dict]):
        self.logger = logging.getLogger(__name__)
        if not raw_data_list:
            self.logger.warning("Analyzer initialized with empty raw data list.")
            self.df = pd.DataFrame()
        else:
            self.df = pd.DataFrame(raw_data_list)
        
        # Pre-compile regex patterns
        self.patterns = {
            'founder_bio': self._compile_pattern_list(config.FOUNDER_BIO_KEYWORDS),
            'project_bio': self._compile_pattern_list(config.PROJECT_BIO_KEYWORDS),
            'tier1_struggle': self._compile_pattern_list(config.TIER1_STRUGGLE_KEYWORDS),
            'tier2_struggle': self._compile_pattern_list(config.TIER2_STRUGGLE_KEYWORDS),
            'general_bio': self._compile_pattern_list(config.GENERAL_BIO_KEYWORDS),
        }

    def _compile_pattern_list(self, keywords: list) -> regex.Pattern:
        """Create case-insensitive regex pattern from keyword list"""
        pattern_str = r'\b(' + '|'.join(regex.escape(k) for k in keywords) + r')\b'
        return regex.compile(pattern_str, flags=regex.IGNORECASE | regex.UNICODE)

    def _classify_account_type(self, bio: str) -> str:
        """Classify as 'Founder' (person) or 'Project' (brand)"""
        if not isinstance(bio, str):
            return 'Unknown'
        
        bio_lower = bio.lower()
        
        # Check for founder indicators
        if self.patterns['founder_bio'].search(bio):
            return 'Founder'
        
        # Check for project indicators
        if self.patterns['project_bio'].search(bio):
            return 'Project'
        
        # Heuristic: First-person language = Founder
        if any(word in bio_lower for word in ['i am', 'i\'m', 'my startup', 'i build']):
            return 'Founder'
        
        # Heuristic: Plural language = Project
        if any(word in bio_lower for word in ['we are', 'we\'re', 'our team', 'we build']):
            return 'Project'
        
        return 'Unknown'

    def _calculate_posting_gaps(self, tweets_list: list) -> Tuple[float, float, int]:
        """
        Calculate posting pattern metrics
        Returns: (avg_gap_days, gap_variance, days_since_last_post)
        """
        if not tweets_list or len(tweets_list) < 2:
            return (9999, 0, 9999)
        
        try:
            # Parse timestamps
            timestamps = []
            for tweet in tweets_list:
                if 'timestamp' in tweet:
                    ts = datetime.fromisoformat(tweet['timestamp'].replace('Z', '+00:00'))
                    timestamps.append(ts)
            
            if len(timestamps) < 2:
                return (9999, 0, 9999)
            
            # Sort by date (newest first)
            timestamps.sort(reverse=True)
            
            # Calculate gaps between consecutive posts
            gaps = []
            for i in range(len(timestamps) - 1):
                gap = (timestamps[i] - timestamps[i + 1]).days
                gaps.append(gap)
            
            # Calculate metrics
            avg_gap = np.mean(gaps) if gaps else 9999
            variance = np.var(gaps) if len(gaps) > 1 else 0
            
            # Days since last post
            now = datetime.now(timezone.utc)
            days_since = (now - timestamps[0]).days
            
            return (avg_gap, variance, days_since)
            
        except Exception as e:
            self.logger.warning(f"Error calculating posting gaps: {e}")
            return (9999, 0, 9999)

    def _detect_posting_pattern(self, avg_gap: float, variance: float, days_since: int) -> str:
        """
        Detect posting pattern based on metrics
        Returns: 'erratic_active', 'sparse_consistent', 'comeback_kid', 'daily_poster', or 'dormant'
        """
        # Check dormant first
        if days_since > 30:
            return 'dormant'
        
        # Check daily poster
        if avg_gap <= 2 and variance <= 1:
            return 'daily_poster'
        
        # Check erratic active (high variance + recent post)
        if variance >= 4 and 2 <= avg_gap <= 7 and days_since <= 7:
            return 'erratic_active'
        
        # Check sparse consistent (low variance + weekly posting)
        if variance <= 3 and 7 <= avg_gap <= 14 and days_since <= 14:
            return 'sparse_consistent'
        
        # Check comeback kid (was gone but just posted)
        if days_since <= 7 and avg_gap > 14 and variance > 10:
            return 'comeback_kid'
        
        # Default to dormant if nothing matches
        return 'dormant'

    def _find_struggle_keywords(self, tweets_list: list) -> Dict:
        """
        Find struggle keywords in recent tweets
        Returns: {
            'tier1_keywords': [...],
            'tier2_keywords': [...],
            'struggle_tweets': [...]
        }
        """
        if not tweets_list:
            return {'tier1_keywords': [], 'tier2_keywords': [], 'struggle_tweets': []}
        
        tier1_found = set()
        tier2_found = set()
        struggle_tweets = []
        
        # Check each tweet
        for tweet in tweets_list[:10]:  # Only check first 10 (most recent)
            if 'text' not in tweet:
                continue
                
            text = tweet['text']
            text_lower = text.lower()
            
            # Check Tier 1 keywords
            tier1_matches = self.patterns['tier1_struggle'].findall(text)
            if tier1_matches:
                tier1_found.update([m.lower() for m in tier1_matches])
                struggle_tweets.append({
                    'text': text[:100] + '...' if len(text) > 100 else text,
                    'tier': 1
                })
            
            # Check Tier 2 keywords
            tier2_matches = self.patterns['tier2_struggle'].findall(text)
            if tier2_matches:
                tier2_found.update([m.lower() for m in tier2_matches])
                if not tier1_matches:  # Don't double-count tweets
                    struggle_tweets.append({
                        'text': text[:100] + '...' if len(text) > 100 else text,
                        'tier': 2
                    })
        
        return {
            'tier1_keywords': list(tier1_found),
            'tier2_keywords': list(tier2_found),
            'struggle_tweets': struggle_tweets[:3]  # Keep top 3
        }

    def _calculate_smm_score(self, row: pd.Series) -> Dict:
        """
        Calculate SMM need score (0-100) with detailed reasons
        Different logic for Founders vs Projects
        """
        score = 0
        reasons = []
        
        account_type = row['account_type']
        scoring_config = config.FOUNDER_SCORING if account_type == 'Founder' else config.PROJECT_SCORING
        
        # 1. POSTING PATTERN (40 points max)
        pattern = row.get('posting_pattern', 'dormant')
        pattern_score = scoring_config['posting_pattern'].get(pattern, 0)
        score += pattern_score
        
        if pattern_score > 0:
            pattern_desc = config.POSTING_PATTERNS[pattern]['description']
            reasons.append(f"Posting: {pattern_desc} (+{pattern_score}pts)")
        
        # 2. STRUGGLE SIGNALS (30 points max)
        tier1_count = len(row.get('tier1_struggle_keywords', []))
        tier2_count = len(row.get('tier2_struggle_keywords', []))
        
        struggle_score = 0
        if tier1_count > 0:
            struggle_score += min(tier1_count * scoring_config['struggle_signals']['tier1_per_keyword'], 30)
            reasons.append(f"Found {tier1_count} high-priority struggle signal(s)")
        
        if tier2_count > 0 and struggle_score < 30:
            additional = min(tier2_count * scoring_config['struggle_signals']['tier2_per_keyword'], 
                           30 - struggle_score)
            struggle_score += additional
            reasons.append(f"Found {tier2_count} struggle signal(s)")
        
        score += min(struggle_score, scoring_config['struggle_signals']['max_points'])
        
        # 3. FOLLOWER TIER (20 points max)
        follower_count = row.get('follower_count', 0)
        tier_score = 0
        for (min_f, max_f), points in scoring_config['follower_tier'].items():
            if min_f <= follower_count <= max_f:
                tier_score = points
                reasons.append(f"{follower_count:,} followers - good range (+{points}pts)")
                break
        score += tier_score
        
        # 4. BONUSES (up to 25 points)
        bio = str(row.get('bio', '')).lower()
        
        # Founder-specific bonuses
        if account_type == 'Founder':
            if any(kw in bio for kw in ['founder', 'ceo', 'builder']):
                score += scoring_config['bonus']['has_founder_keywords']
                reasons.append("Has founder/builder identity (+10pts)")
        
        # Get tweets text for all checks
        tweets_text = ' '.join([t.get('text', '') for t in row.get('tweets', [])])
        
        # Project-specific bonuses
        if account_type == 'Project':
            if any(word in tweets_text.lower() for word in ['launched', 'mvp', 'beta', 'live']):
                score += scoring_config['bonus']['recently_launched']
                reasons.append("Recently launched (+10pts)")
        
        # Common bonuses
        if any(word in bio.lower() or word in tweets_text.lower() for word in ['raised', 'funded', 'seed', 'vc']):
            score += scoring_config['bonus']['is_funded']
            reasons.append("Funded/raising (+10pts)")
        
        if row.get('days_since_last_post', 999) <= 3:
            score += scoring_config['bonus']['posted_last_3_days']
            reasons.append("Posted in last 3 days (+5pts)")
        
        # Assign grade
        for grade, (min_s, max_s) in config.SCORE_GRADES.items():
            if min_s <= score <= max_s:
                score_grade = grade
                break
        else:
            score_grade = 'F'
        
        return {
            'smm_need_score': min(score, 100),
            'score_grade': score_grade,
            'score_reasons': ' | '.join(reasons) if reasons else 'No qualifying signals'
        }

    def run_analysis(self) -> pd.DataFrame:
        """Run the complete analysis pipeline"""
        if self.df.empty:
            self.logger.warning("Analyzer DataFrame is empty. Aborting.")
            return pd.DataFrame()
        
        self.logger.info(f"Analyzing {len(self.df)} raw profiles...")
        
        # 1. Classify account type
        self.logger.info("Step 1: Classifying accounts (Founder vs Project)...")
        self.df['account_type'] = self.df['bio'].apply(self._classify_account_type)
        
        # 2. Analyze posting patterns
        self.logger.info("Step 2: Analyzing posting patterns...")
        posting_data = self.df['tweets'].apply(
            lambda t: self._calculate_posting_gaps(t) if isinstance(t, list) else (9999, 0, 9999)
        )
        
        self.df['avg_gap_days'] = posting_data.apply(lambda x: x[0])
        self.df['gap_variance'] = posting_data.apply(lambda x: x[1])
        self.df['days_since_last_post'] = posting_data.apply(lambda x: x[2])
        
        self.df['posting_pattern'] = self.df.apply(
            lambda row: self._detect_posting_pattern(
                row['avg_gap_days'], 
                row['gap_variance'], 
                row['days_since_last_post']
            ), axis=1
        )
        
        # 3. Find struggle keywords
        self.logger.info("Step 3: Detecting struggle signals...")
        struggle_data = self.df['tweets'].apply(self._find_struggle_keywords)
        
        self.df['tier1_struggle_keywords'] = struggle_data.apply(lambda x: x['tier1_keywords'])
        self.df['tier2_struggle_keywords'] = struggle_data.apply(lambda x: x['tier2_keywords'])
        self.df['struggle_tweets'] = struggle_data.apply(lambda x: x['struggle_tweets'])
        
        # Combine for display
        self.df['struggle_keywords_found'] = self.df.apply(
            lambda row: row['tier1_struggle_keywords'] + row['tier2_struggle_keywords'], axis=1
        )
        
        # 4. Categorize followers
        self.logger.info("Step 4: Categorizing follower tiers...")
        self.df['follower_tier'] = self.df['follower_count'].apply(
            lambda f: next(
                (tier for tier, (min_f, max_f) in config.FOLLOWER_TIERS.items() if min_f <= f <= max_f),
                'N/A'
            )
        )
        
        # 5. Calculate SMM need score
        self.logger.info("Step 5: Calculating SMM need scores...")
        scoring_results = self.df.apply(self._calculate_smm_score, axis=1)
        
        self.df['smm_need_score'] = scoring_results.apply(lambda x: x['smm_need_score'])
        self.df['score_grade'] = scoring_results.apply(lambda x: x['score_grade'])
        self.df['score_reasons'] = scoring_results.apply(lambda x: x['score_reasons'])
        
        # 6. Filter out low-quality leads
        self.logger.info(f"Step 6: Filtering leads (minimum score: {config.MIN_QUALIFYING_SCORE})...")
        qualified_df = self.df[self.df['smm_need_score'] >= config.MIN_QUALIFYING_SCORE].copy()
        
        if qualified_df.empty:
            self.logger.warning("No leads met the minimum score threshold!")
            return pd.DataFrame()
        
        # 7. Select and sort output columns
        self.logger.info("Step 7: Preparing final output...")
        
        final_columns = [col for col in config.OUTPUT_COLUMNS if col in qualified_df.columns]
        final_df = qualified_df[final_columns].copy()
        
        # Sort by score (best leads first)
        final_df = final_df.sort_values(
            by=config.SORT_PRIORITY,
            ascending=False
        )
        
        # Log summary
        self.logger.info(f"\n{'='*60}")
        self.logger.info("ANALYSIS SUMMARY")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Total profiles analyzed: {len(self.df)}")
        self.logger.info(f"Qualified leads found: {len(final_df)}")
        
        grade_counts = final_df['score_grade'].value_counts()
        for grade in ['A', 'B', 'C']:
            count = grade_counts.get(grade, 0)
            self.logger.info(f"  {grade}-grade leads: {count}")
        
        self.logger.info(f"{'='*60}\n")
        
        return final_df