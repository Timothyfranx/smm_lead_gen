"""
Quick setup script to add X accounts to your scraper
Run this to setup new accounts: python setup_accounts.py
"""

import os
import sys
from src.scraper import Scraper

def main():
    print("\n" + "="*70)
    print(" X ACCOUNT SETUP WIZARD")
    print("="*70)
    
    print("\nThis script will help you save X account sessions for scraping.")
    print("You'll need to login manually in a browser window that will open.\n")
    
    # Ask how many accounts to setup
    while True:
        try:
            num_accounts = input("How many accounts do you want to setup? (1-10): ")
            num_accounts = int(num_accounts)
            if 1 <= num_accounts <= 10:
                break
            print("❌ Please enter a number between 1 and 10")
        except ValueError:
            print("❌ Please enter a valid number")
    
    print(f"\n✅ Setting up {num_accounts} account(s)...\n")
    
    # Setup each account
    for i in range(1, num_accounts + 1):
        print("\n" + "-"*70)
        print(f" ACCOUNT {i} of {num_accounts}")
        print("-"*70)
        
        # Get account name
        while True:
            account_name = input(f"\nEnter a name for account #{i} (e.g., 'account1', 'main', 'backup'): ").strip()
            if account_name and account_name.replace('_', '').replace('-', '').isalnum():
                break
            print("❌ Invalid name. Use only letters, numbers, dashes, and underscores.")
        
        # Setup the account
        print(f"\n🚀 Opening browser for '{account_name}'...")
        print("You'll need to:")
        print("  1. Login to X")
        print("  2. Complete any 2FA if needed")
        print("  3. Wait until you see your HOME feed")
        print("  4. Come back here and press ENTER\n")
        
        scraper = Scraper(headless=False)
        
        try:
            success = scraper.setup_new_account(account_name)
            
            if success:
                print(f"\n✅ Account '{account_name}' saved successfully!")
            else:
                print(f"\n❌ Failed to save '{account_name}'")
                
        except Exception as e:
            print(f"\n❌ Error setting up '{account_name}': {e}")
        finally:
            scraper.close()
        
        # Ask if they want to continue
        if i < num_accounts:
            continue_setup = input("\nContinue to next account? (y/n): ").lower()
            if continue_setup != 'y':
                print(f"\n⚠️  Setup stopped. {i} account(s) configured.")
                break
    
    print("\n" + "="*70)
    print(" SETUP COMPLETE!")
    print("="*70)
    print("\n✅ Your accounts are ready to use.")
    print("\nTo start scraping, update your main.py:")
    print("  Option 1 (single account):")
    print("    scraper.run('account1')")
    print("\n  Option 2 (with rotation):")
    print("    from src.scraper import run_with_rotation")
    print("    leads = run_with_rotation(['account1', 'account2', 'account3'])")
    print("\n")

if __name__ == "__main__":
    main()