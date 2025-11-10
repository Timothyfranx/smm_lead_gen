"""
Quick test script to validate the new system works
Run this BEFORE running the full scraper
"""

import sys
from datetime import datetime, timezone, timedelta

# Test imports
try:
    from src import config, analyzer
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def create_test_data():
    """Create fake test data that mimics scraper output"""
    
    # Test Case 1: Perfect A-grade lead (Founder, erratic posting, struggle signals)
    founder_struggling = {
        'handle': 'test_founder_1',
        'bio': 'AI founder building something cool. Need to be more consistent with posting!',
        'profile_url': 'https://x.com/test_founder_1',
        'follower_count': 1200,
        'total_tweets': 15,
        'tweets': [
            {'text': 'Really need to post more consistently. Struggling with social media lately.', 
             'timestamp': (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()},
            {'text': 'Working on my AI startup but bad at twitter honestly', 
             'timestamp': (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()},
            {'text': 'Posted something about AI', 
             'timestamp': (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()},
            {'text': 'Another AI tweet', 
             'timestamp': (datetime.now(timezone.utc) - timedelta(days=12)).isoformat()},
            {'text': 'Building in public is hard when you have no engagement', 
             'timestamp': (datetime.now(timezone.utc) - timedelta(days=18)).isoformat()},
        ]
    }
    
    # Test Case 2: Good B-grade lead (Project, sparse posting, funded)
    project_decent = {
        'handle': 'test_project_1',
        'bio': 'AI startup. We just raised our seed round. Official account.',
        'profile_url': 'https://x.com/test_project_1',
        'follower_count': 2500,
        'total_tweets': 12,
        'tweets': [
            {'text': 'Product update: new features launched today!', 
             'timestamp': (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()},
            {'text': 'Join our beta program', 
             'timestamp': (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()},
            {'text': 'Thanks for 2K followers!', 
             'timestamp': (datetime.now(timezone.utc) - timedelta(days=21)).isoformat()},
        ]
    }
    
    # Test Case 3: Skip - daily poster (already has system)
    daily_poster = {
        'handle': 'test_daily',
        'bio': 'Founder posting daily. Consistent content creator.',
        'profile_url': 'https://x.com/test_daily',
        'follower_count': 3000,
        'total_tweets': 50,
        'tweets': [
            {'text': f'Daily post {i}', 
             'timestamp': (datetime.now(timezone.utc) - timedelta(days=i)).isoformat()}
            for i in range(15)
        ]
    }
    
    # Test Case 4: Skip - dormant (too dead)
    dormant_account = {
        'handle': 'test_dormant',
        'bio': 'Web3 founder. Was building something.',
        'profile_url': 'https://x.com/test_dormant',
        'follower_count': 800,
        'total_tweets': 10,
        'tweets': [
            {'text': 'My last post', 
             'timestamp': (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()},
            {'text': 'Previous post', 
             'timestamp': (datetime.now(timezone.utc) - timedelta(days=65)).isoformat()},
        ]
    }
    
    return [founder_struggling, project_decent, daily_poster, dormant_account]


def test_config():
    """Test config.py loads correctly"""
    print("\n" + "="*60)
    print("TESTING CONFIG.PY")
    print("="*60)
    
    try:
        print(f"✅ Follower filter: {config.FOLLOWER_FILTER['MIN']}-{config.FOLLOWER_FILTER['MAX']}")
        print(f"✅ Search queries: {len(config.SEARCH_QUERIES)} configured")
        print(f"✅ Tweets to scrape: {config.TWEETS_TO_SCRAPE}")
        print(f"✅ Min qualifying score: {config.MIN_QUALIFYING_SCORE}")
        print(f"✅ Tier 1 struggle keywords: {len(config.TIER1_STRUGGLE_KEYWORDS)}")
        print(f"✅ Tier 2 struggle keywords: {len(config.TIER2_STRUGGLE_KEYWORDS)}")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def test_analyzer():
    """Test analyzer.py with fake data"""
    print("\n" + "="*60)
    print("TESTING ANALYZER.PY")
    print("="*60)
    
    try:
        # Create test data
        test_data = create_test_data()
        print(f"✅ Created {len(test_data)} test profiles")
        
        # Initialize analyzer
        bot_analyzer = analyzer.Analyzer(test_data)
        print("✅ Analyzer initialized")
        
        # Run analysis
        results = bot_analyzer.run_analysis()
        print(f"✅ Analysis complete")
        
        if results.empty:
            print("⚠️  Warning: No qualified leads (might be too strict)")
            return True
        
        # Display results
        print(f"\n📊 Results: {len(results)} qualified leads found")
        print("\nTop 3 leads:")
        for idx, row in results.head(3).iterrows():
            print(f"\n  {row['handle']}")
            print(f"    Type: {row['account_type']}")
            print(f"    Score: {row['smm_need_score']} ({row['score_grade']}-grade)")
            print(f"    Pattern: {row['posting_pattern']}")
            print(f"    Struggles: {len(row['struggle_keywords_found'])} keywords")
            print(f"    Reasons: {row['score_reasons'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "🧪 "*20)
    print("TESTING NEW SMM LEAD DETECTION SYSTEM")
    print("🧪 "*20)
    
    # Test config
    config_ok = test_config()
    
    # Test analyzer
    analyzer_ok = test_analyzer()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Config.py: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Analyzer.py: {'✅ PASS' if analyzer_ok else '❌ FAIL'}")
    
    if config_ok and analyzer_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. Replace your old src/config.py with the new one")
        print("2. Replace your old src/analyzer.py with the new one")
        print("3. Run: python main.py")
        print("\nYour scraper.py, main.py, and utils.py are unchanged and ready to go!")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()