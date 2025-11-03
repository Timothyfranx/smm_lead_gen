"""
This is the central configuration file for the SMM Lead Generation Bot.
All keywords, filters, and settings are stored here for easy access and
modification without touching the core scraper or analyzer code.
"""

# ----------------------------------------------------------------------------
# CORE FILTERS & SETTINGS
# ----------------------------------------------------------------------------

# The main follower filter to pre-qualify accounts.
# We will only scrape profiles within this range.
FOLLOWER_FILTER = {
    'MIN': 150,
    'MAX': 10000
}

# The number of recent tweets to scrape from each profile's timeline
# for analysis.
TWEETS_TO_SCRAPE = 50

# ----------------------------------------------------------------------------
# SCRAPER CONFIGURATION
# ----------------------------------------------------------------------------

# Broad, general search queries for the "Scout" (scraper.py) to use.
# The "Strategist" (analyzer.py) will do the smart filtering later.
SEARCH_QUERIES = [
    "AI founder",
    "web3 builder",
    "AI startup",
    "web3 project",
    "building in public",
    "AI app",
    "onchain",
    "crypto founder",
    "LLM"
]

# ----------------------------------------------------------------------------
# ANALYSIS RULES (TIERS & GAPS)
# ----------------------------------------------------------------------------

# Defines the "Activity Gap" to classify how active a user is.
# (Min_Days, Max_Days)
ACTIVITY_GAPS = {
    'Active': (0, 7),
    'Semi-Active': (8, 30),
    'Paused': (31, 90),
    'Dormant': (91, 9999)  # 91+ days
}

# Defines the "Follower Tiers" for client segmentation.
# (Min_Followers, Max_Followers)
FOLLOWER_TIERS = {
    'Tier 1': (500, 2000),
    'Tier 2': (2001, 10000),
    'Tier 3': (10001, 50000)
    # Note: Our FOLLOWER_FILTER @ 10k max means we'll mostly see T1 & T2.
}

# ----------------------------------------------------------------------------
# PERSONA 1: "FOUNDER" KEYWORDS
# ----------------------------------------------------------------------------

# Keywords to identify an individual (Founder, Builder, CEO).
# Used to classify an account as `account_type = 'Person'`.
FOUNDER_BIO_KEYWORDS = [
    # Founder / Builder Terms
    "founder", "cofounder", "ceo", "cto", "maker", "builder", "hacker",
    "indie hacker", "solo founder", "bootstrapped", "creator", "entrepreneur",
    "operator", "startup founder", "founding engineer", "early builder",
    "creator economy", "side project", "startup studio", "solopreneur"
]

# Tweet keywords indicating a "Paused Founder" (burnout, inactivity).
# These are strong signals for your SMM pitch.
FOUNDER_TWEET_KEYWORDS = [
    # Low Structure / Burnout Indicators
    "been quiet lately", "taking a break", "back to building",
    "haven’t posted in a while", "getting back", "missed building",
    "restart", "rebooting project", "new start", "paused work",
    "burnout", "regrouping", "pause", "step back"
]

# ----------------------------------------------------------------------------
# PERSONA 2: "PROJECT" KEYWORDS
# ----------------------------------------------------------------------------

# Keywords to identify an organization (Project, Brand, Team).
# Used to classify an account as `account_type = 'Project'`.
PROJECT_BIO_KEYWORDS = [
    # AI / Tech Projects
    "ai startup", "ai project", "ai app", "ai tool", "ai platform", "llm platform",
    "autonomous agents", "genai app", "ai saas", "ai research lab", "ai infra",
    "ai model", "ai api", "ai sdk", "ai framework", "llm fine-tuning",
    "ai chatbot", "ai studio", "ai team", "ai product launch",

    # Web3 / Crypto Projects
    "web3 project", "crypto project", "onchain protocol", "defi platform",
    "nft marketplace", "nft project", "dao community", "token project",
    "smart contract", "blockchain project", "layer2 project", "zk-rollup",
    "zk proof", "wallet", "dex", "bridge", "airdrops", "ido", "ido launch",
    "launchpad", "staking platform", "governance protocol", "validator node",
    "chain infra",

    # General Brand / Product Language
    "official", "team", "project", "platform", "startup", "product",
    "community", "ecosystem", "labs", "studio", "network", "protocol",
    "foundation", "dao", "hq", "collective", "devs", "core team"
]

# Tweet keywords indicating an "Inefficient Project" (e.g., product/community focus).
PROJECT_TWEET_KEYWORDS = [
    # Launch / Milestone
    "we’re live", "our beta is out", "mainnet launch", "testnet live",
    "public alpha", "mvp ready", "just launched", "product demo",
    "feature update", "v2 release", "changelog", "new integration",
    "announcement", "dev update", "v1", "v2",

    # Community / Growth
    "join our discord", "join our telegram", "open beta", "open waitlist",
    "be part of", "early access", "feedback wanted", "building our community",
    "help us test", "thanks for 1k followers", "update thread", "link in bio",

    # Funding / Partners
    "partnership", "integrated with", "collaborating with",
    "ecosystem partner", "grants program", "joined accelerator"
]

# ----------------------------------------------------------------------------
# GENERAL HIGH-INTENT KEYWORDS (For all personas)
# ----------------------------------------------------------------------------

# General contextual keywords for all accounts.
# These help identify topics of interest (AI, Web3, etc.)
GENERAL_BIO_KEYWORDS = [
    # AI / Tech
    "ai", "artificial intelligence", "machine learning", "ml", "deep learning",
    "data scientist", "nlp", "genai", "llm", "langchain", "rag", "ai developer",
    "ai engineer",

    # Web3 / Crypto
    "web3", "onchain", "crypto", "defi", "blockchain", "nft", "dao", "token",
    "metaverse", "dapp", "solidity", "layer2", "zk", "eth", "solana",
    "polygon", "base",

    # Business / Growth
    "seed", "raising", "funded", "backed by", "investor", "angel", "vc",
    "series a", "demo day", "stealth mode", "growth", "traction", "accelerator",

    # Communication
    "telegram", "discord", "substack", "newsletter", "waitlist"
]

# High-signal tweet keywords relevant to *all* personas (e.g., funding, hiring).
HIGH_INTENT_TWEET_KEYWORDS = [
    # Funding / Business
    "just raised", "closed our round", "funded", "seed round", "pre-seed",
    "announced our raise", "demo day", "pitching", "backed by",
    "angel round", "runway", "vc funded",

    # Hiring / Team
    "hiring", "looking for", "join our team", "need a", "collaborate",
    "work with us", "cofounder wanted", "searching for a", "open position",

    # Launch / Product
    "launching soon", "mvp live", "try the demo", "building in public",
    "feedback welcome", "working on", "new project", "prototype"
]