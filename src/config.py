"""
OPTIMIZED SMM LEAD DETECTION CONFIG
Focus: "Trying but failing" accounts in the 150-5K follower sweet spot
Strategy: Fast, lean, high-conversion searches
"""

# ============================================================================
# CORE FILTERS & SETTINGS
# ============================================================================

FOLLOWER_FILTER = {
    'MIN': 150,
    'MAX': 5000  # Changed from 10K - better conversion rate
}

# Reduced from 50 to 20 - faster scraping, still enough to detect patterns
TWEETS_TO_SCRAPE = 20

# ============================================================================
# SMART SEARCH QUERIES - Using X Advanced Operators
# ============================================================================

# HIGH-INTENT: Self-aware accounts (know they need help)
HIGH_INTENT_SEARCHES = [
    # Direct struggle admissions
    '("need to post more" OR "should tweet more" OR "need to be more consistent") (founder OR startup OR ceo) lang:en -job -hiring',
    '("bad at twitter" OR "terrible at social media" OR "struggling with posting") (founder OR builder) lang:en -job',
    '("no engagement" OR "posting into void" OR "algorithm hates me") (founder OR startup) lang:en -bot',
    '("can\'t keep up" OR "too busy to post" OR "no time for twitter") founder lang:en -job -hiring',
    '("getting back to" OR "trying to be more active" OR "haven\'t posted") (founder OR ceo) lang:en',
]

# MEDIUM-INTENT: Active builders in target niches
MEDIUM_INTENT_SEARCHES = [
    # AI founders (unverified = more likely to need help)
    '((founder OR ceo OR builder) (ai OR llm OR "machine learning") lang:en) -filter:verified -job -hiring -bot',
    '((founder OR ceo) ("ai startup" OR "ai tool" OR "ai app") lang:en) -filter:verified -job',
    '("building" (ai OR "artificial intelligence" OR llm) founder lang:en) -job -hiring',
    
    # Web3 builders (notoriously bad at marketing)
    '((founder OR builder OR ceo) (web3 OR crypto OR blockchain) lang:en) -filter:verified -nft -job -hiring',
    '((founder OR ceo) (defi OR onchain OR "web3 project") lang:en) -filter:verified -job',
    
    # "Building in public" crowd (trying but often struggling)
    '("building in public" (founder OR indie OR solo) lang:en) -"looking for" -job -hiring',
    '(("indie hacker" OR solopreneur OR "solo founder") lang:en) -filter:verified -job',
]

# FUNDED-BUT-STRUGGLING: Has budget but visibility sucks
FUNDED_SEARCHES = [
    # Recent funding (has money for SMM)
    '((raised OR "just raised" OR funded) (seed OR "pre-seed") (founder OR startup) lang:en) since:2024-06-01 -job -hiring',
    '(("announced our" OR "closed our") (round OR funding OR seed) lang:en) since:2024-06-01 -job',
    
    # Accelerator grads (funded but often need marketing help)
    '((yc OR "y combinator" OR techstars) (founder OR startup) lang:en) -job -hiring',
    '(accelerator (founder OR startup OR ceo) lang:en) -"looking for" -job',
]

# Combine all tiers
SEARCH_QUERIES = (
    HIGH_INTENT_SEARCHES +      # Best leads, run first
    MEDIUM_INTENT_SEARCHES +    # Good volume
    FUNDED_SEARCHES             # High-value leads
)

# ============================================================================
# POSTING PATTERN DETECTION
# ============================================================================

# What constitutes each posting pattern
POSTING_PATTERNS = {
    'erratic_active': {
        'description': 'Posts 1-3x/week but inconsistently',
        'avg_gap_days': (2, 7),        # Average 2-7 days between posts
        'gap_variance': 4,              # High variance (inconsistent)
        'max_days_since_last': 7,       # Must have posted in last week
        'score_value': 40               # Highest score - perfect lead
    },
    'sparse_consistent': {
        'description': 'Posts ~1x/week regularly',
        'avg_gap_days': (7, 14),       # Average 7-14 days
        'gap_variance': 3,              # Low variance (predictable)
        'max_days_since_last': 14,      # Posted in last 2 weeks
        'score_value': 30               # Good lead
    },
    'comeback_kid': {
        'description': 'Was gone, just returned',
        'avg_gap_days': (14, 90),      # Long gaps in history
        'gap_variance': 10,             # Very high variance
        'max_days_since_last': 7,       # But posted recently!
        'score_value': 25               # Decent timing
    },
    'daily_poster': {
        'description': 'Posts daily (already has system)',
        'avg_gap_days': (0, 2),        # Posts almost daily
        'gap_variance': 1,              # Very consistent
        'max_days_since_last': 3,
        'score_value': 0                # Skip - don't need help
    },
    'dormant': {
        'description': 'Too inactive (30+ days)',
        'avg_gap_days': (30, 9999),
        'gap_variance': 999,
        'max_days_since_last': 9999,
        'score_value': 0                # Skip - too dead
    }
}

# ============================================================================
# STRUGGLE SIGNAL KEYWORDS
# ============================================================================

# TIER 1: Direct admissions (GOLD - 30 points)
TIER1_STRUGGLE_KEYWORDS = [
    "need to post more",
    "should tweet more",
    "need to be more consistent",
    "bad at social media",
    "terrible at twitter",
    "struggling to stay active",
    "can't keep up with posting",
    "should engage more",
]

# TIER 2: Indirect frustration (GOOD - 20 points)
TIER2_STRUGGLE_KEYWORDS = [
    "no engagement",
    "no one sees my tweets",
    "posting into the void",
    "algorithm hates me",
    "reach is down",
    "twitter is hard",
    "no traction",
    "haven't posted in a while",
    "trying to be more active",
    "getting back to posting",
    "back to building in public",
]

# Combine for easy searching
ALL_STRUGGLE_KEYWORDS = TIER1_STRUGGLE_KEYWORDS + TIER2_STRUGGLE_KEYWORDS

# ============================================================================
# PERSONA-SPECIFIC KEYWORDS (For Classification)
# ============================================================================

# FOUNDERS (Personal brand accounts)
FOUNDER_BIO_KEYWORDS = [
    "founder", "cofounder", "ceo", "cto", "maker", "builder",
    "indie hacker", "solo founder", "creator", "entrepreneur",
    "solopreneur", "founding engineer"
]

# PROJECTS (Brand/company accounts)
PROJECT_BIO_KEYWORDS = [
    "ai startup", "web3 project", "official", "team", "labs",
    "platform", "protocol", "network", "studio", "dao",
    "we're building", "our mission", "join us"
]

# Keep your original comprehensive lists too
FOUNDER_TWEET_KEYWORDS = [
    "been quiet lately", "taking a break", "back to building",
    "haven't posted in a while", "getting back", "missed building",
    "burnout", "regrouping", "pause", "step back"
]

PROJECT_TWEET_KEYWORDS = [
    "we're live", "our beta", "mainnet launch", "just launched",
    "join our discord", "join our telegram", "open beta",
    "partnership", "integrated with", "grants program"
]

GENERAL_BIO_KEYWORDS = [
    "ai", "web3", "crypto", "blockchain", "defi", "startup",
    "building", "llm", "ml", "onchain"
]

HIGH_INTENT_TWEET_KEYWORDS = [
    "just raised", "funded", "seed round", "hiring",
    "launching soon", "building in public", "mvp"
]

# ============================================================================
# LEAD SCORING WEIGHTS
# ============================================================================

# For FOUNDERS (Personal accounts)
FOUNDER_SCORING = {
    'posting_pattern': {
        'erratic_active': 40,
        'sparse_consistent': 30,
        'comeback_kid': 25,
        'daily_poster': 0,
        'dormant': 0
    },
    'struggle_signals': {
        'tier1_per_keyword': 15,    # 15 points per Tier 1 keyword (max 2)
        'tier2_per_keyword': 10,    # 10 points per Tier 2 keyword (max 2)
        'max_points': 30
    },
    'follower_tier': {
        (500, 2000): 20,    # Sweet spot
        (2001, 5000): 15,   # Good
        (150, 499): 10      # Small but okay
    },
    'bonus': {
        'has_founder_keywords': 10,
        'is_funded': 10,
        'posted_last_3_days': 5
    }
}

# For PROJECTS (Brand accounts)
PROJECT_SCORING = {
    'posting_pattern': {
        'erratic_active': 40,
        'sparse_consistent': 30,
        'comeback_kid': 25,
        'daily_poster': 0,
        'dormant': 0
    },
    'struggle_signals': {
        'tier1_per_keyword': 15,
        'tier2_per_keyword': 10,
        'max_points': 30
    },
    'follower_tier': {
        (1000, 3000): 20,   # Sweet spot for projects
        (3001, 5000): 15,
        (150, 999): 10
    },
    'bonus': {
        'recently_launched': 10,    # "mvp", "beta", "just launched"
        'is_funded': 10,
        'posted_last_3_days': 5
    }
}

# Score thresholds
SCORE_GRADES = {
    'A': (70, 100),   # HOT LEAD
    'B': (50, 69),    # Qualified
    'C': (30, 49),    # Maybe
    'F': (0, 29)      # Skip
}

MIN_QUALIFYING_SCORE = 50  # Only export B-grade and above

# ============================================================================
# PERFORMANCE LIMITS (For your ancient PC)
# ============================================================================

SCRAPING_LIMITS = {
    'max_profiles_per_query': 12,       # Don't over-scrape one query
    'max_total_profiles': 40,           # Total to deep-scrape per run
    'early_exit_threshold': 25,         # Stop if we have 25 B+ leads
}

# ============================================================================
# ACTIVITY GAPS (Keep your original)
# ============================================================================

ACTIVITY_GAPS = {
    'Active': (0, 7),
    'Semi-Active': (8, 30),
    'Paused': (31, 90),
    'Dormant': (91, 9999)
}

# ============================================================================
# FOLLOWER TIERS (Updated for 150-5K range)
# ============================================================================

FOLLOWER_TIERS = {
    'Tier 0': (150, 499),     # Small
    'Tier 1': (500, 2000),    # Sweet spot
    'Tier 2': (2001, 5000),   # Good
}

# ============================================================================
# OUTPUT CUSTOMIZATION
# ============================================================================

OUTPUT_COLUMNS = [
    'handle',
    'account_type',              # Person or Project
    'smm_need_score',            # 0-100 score
    'score_grade',               # A, B, C, F
    'score_reasons',             # Why they scored this way
    'posting_pattern',           # erratic_active, sparse_consistent, etc.
    'follower_count',
    'follower_tier',
    'days_since_last_post',
    'struggle_keywords_found',   # List of keywords found
    'struggle_tweets',           # Actual tweets showing struggle
    'bio',
    'profile_url'
]

SORT_PRIORITY = ['smm_need_score', 'follower_count']