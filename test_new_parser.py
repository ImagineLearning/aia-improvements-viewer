#!/usr/bin/env python3
"""
Test script for the updated parser with accordion structure.
"""

import sys
import os
import yaml
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from auth import WebAuthenticator
from parser import ErrataParser

def test_new_parser():
    """Test the updated parser with real data."""
    
    # Load configuration
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Test URLs
    test_urls = [
        "http://sdphiladelphia.ilclassroom.com/wikis/29245717-kindergarten-errata?path=Wiki.11180076%2FWiki.28930691%2FWiki.9879318%2FWiki.10424770",
        "http://sdphiladelphia.ilclassroom.com/wikis/18746473-grade-1-errata?path=Wiki.11180076%2FWiki.28930691%2FWiki.9879318%2FWiki.10430165"
    ]
    
    # Load credentials
    from dotenv import load_dotenv
    load_dotenv()
    
    username = os.getenv('ERRATA_USERNAME')
    password = os.getenv('ERRATA_PASSWORD')
    
    if not username or not password:
        print("❌ Credentials not found in .env file")
        return
    
    print("🔧 Testing updated parser...")
    
    # Initialize components
    authenticator = WebAuthenticator(config)
    parser = ErrataParser(config)
    
    try:
        # Authenticate
        print("🔐 Authenticating...")
        driver = authenticator.authenticate(username, password)
        
        if not driver:
            print("❌ Authentication failed")
            return
        
        print("✅ Authentication successful!")
        
        # Test parser on each URL
        for i, url in enumerate(test_urls):
            print(f"\n📄 Testing URL {i+1}: {url.split('/')[-1].split('-')[0].title()}")
            
            # Navigate to the page
            driver.get(url)
            
            # Wait for page to load
            import time
            time.sleep(3)
            
            # Parse the page
            errata_records = parser.parse_page_with_selenium(driver)
            
            print(f"📊 Extracted {len(errata_records)} records")
            
            # Show sample records
            for j, record in enumerate(errata_records[:3]):  # Show first 3 records
                print(f"\n🔍 Record {j+1}:")
                print(f"  Unit: {record['Unit']}")
                print(f"  Resource: {record['Resource']}")
                print(f"  Location: {record['Location']}")
                print(f"  Page Numbers: {record['Page_Numbers']}")
                print(f"  Improvement: {record['Improvement_Description'][:100]}...")
                print(f"  Date: {record['Date_Updated']}")
            
            if len(errata_records) > 3:
                print(f"  ... and {len(errata_records) - 3} more records")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if 'driver' in locals():
            driver.quit()
        print("\n🧹 Cleanup completed")

if __name__ == "__main__":
    test_new_parser()
