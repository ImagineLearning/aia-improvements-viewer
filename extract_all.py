#!/usr/bin/env python3
"""
Full errata extraction script.
Extracts data from all errata pages and saves to CSV.
"""

import sys
import os
import yaml
import logging
from pathlib import Path
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from auth import WebAuthenticator
from parser import ErrataParser
from csv_writer import CSVWriter

def setup_logging():
    """Set up logging configuration."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'extraction.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Main extraction function."""
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🔍 Errata Locator - Full Extraction")
    print("=" * 50)
    
    # Load configuration
    try:
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return 1
    
    # Load credentials
    from dotenv import load_dotenv
    load_dotenv()
    
    username = os.getenv('ERRATA_USERNAME')
    password = os.getenv('ERRATA_PASSWORD')
    
    if not username or not password or username == 'your_username_here':
        print("❌ Please update the .env file with your actual credentials")
        print("   ERRATA_USERNAME=your_actual_username")
        print("   ERRATA_PASSWORD=your_actual_password")
        return 1
    
    # Initialize components
    authenticator = WebAuthenticator(config)
    parser = ErrataParser(config)
    csv_writer = CSVWriter(config)
    
    driver = None
    all_records = []
    
    try:
        # Authenticate
        print("\n🔐 Authenticating with ilclassroom.com...")
        success = authenticator.login_with_selenium(username, password)
        
        if not success:
            logger.error("Authentication failed")
            return 1
        
        driver = authenticator.get_authenticated_driver()
        print("✅ Authentication successful!")
        
        # Extract data from all pages
        base_url = config['website']['base_url']
        errata_pages = config['website']['errata_pages']
        
        print(f"\n📄 Extracting data from {len(errata_pages)} pages...")
        
        for i, page_path in enumerate(errata_pages):
            page_name = page_path.split('-')[1].replace('-', ' ').title() if '-' in page_path else f"Page {i+1}"
            print(f"\n🔄 Processing: {page_name}")
            
            # Navigate to the page
            full_url = base_url + page_path
            driver.get(full_url)
            
            # Wait for page to load
            import time
            time.sleep(3)
            
            # Parse the page
            page_records = parser.parse_page_with_selenium(driver)
            
            if page_records:
                all_records.extend(page_records)
                print(f"  ✅ Extracted {len(page_records)} records")
                
                # Show sample
                if page_records:
                    sample = page_records[0]
                    print(f"  📝 Sample: {sample['Unit']} - {sample['Resource']}")
            else:
                print(f"  ⚠️  No records found")
        
        print(f"\n📊 Total records extracted: {len(all_records)}")
        
        if all_records:
            # Save to CSV
            print("\n💾 Saving to CSV...")
            
            # Ensure output directory exists
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            csv_path = csv_writer.write_errata_data(all_records)
            print(f"✅ Data saved to: {csv_path}")
            
            # Show summary by unit
            print("\n📈 Summary by Unit:")
            unit_counts = {}
            for record in all_records:
                unit = record['Unit']
                unit_counts[unit] = unit_counts.get(unit, 0) + 1
            
            for unit, count in sorted(unit_counts.items()):
                print(f"  {unit}: {count} records")
            
            # Show sample of saved data
            print(f"\n🔍 Sample of extracted data:")
            for i, record in enumerate(all_records[:3]):
                print(f"\nRecord {i+1}:")
                print(f"  Date Extracted: {record['Date_Extracted']}")
                print(f"  Unit: {record['Unit']}")
                print(f"  Resource: {record['Resource']}")
                print(f"  Location: {record['Location']}")
                print(f"  Page Numbers: {record['Page_Numbers']}")
                print(f"  Improvement: {record['Improvement_Description'][:80]}...")
                print(f"  Date Updated: {record['Date_Updated']}")
            
            print(f"\n🎉 Extraction completed successfully!")
            print(f"📁 Output file: {csv_path}")
            
        else:
            print("❌ No data was extracted")
            return 1
    
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # Clean up
        if driver:
            driver.quit()
            print("\n🧹 Browser closed")
    
    return 0

if __name__ == "__main__":
    exit(main())
