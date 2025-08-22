#!/usr/bin/env python3
"""
Sample extraction from kindergarten errata page.
Shows exactly what data we can extract.
"""

import sys
import os
import yaml
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from auth import WebAuthenticator
from parser import ErrataParser

def sample_kindergarten_extraction():
    """Run a sample extraction from the kindergarten errata page."""
    
    print("🎯 Kindergarten Errata Sample Extraction")
    print("=" * 50)
    
    # Load configuration
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Load credentials
    from dotenv import load_dotenv
    load_dotenv()
    
    username = os.getenv('ERRATA_USERNAME')
    password = os.getenv('ERRATA_PASSWORD')
    
    if not username or not password or username == 'your_username_here':
        print("⚠️  Credentials not configured yet.")
        print("   Please update the .env file with your actual ilclassroom.com credentials:")
        print("   ERRATA_USERNAME=your_actual_username")
        print("   ERRATA_PASSWORD=your_actual_password")
        print("\n🔍 For now, showing expected data structure based on our analysis...")
        
        show_expected_structure()
        return
    
    # Initialize components
    authenticator = WebAuthenticator(config)
    parser = ErrataParser(config)
    
    # Kindergarten page URL
    kindergarten_url = "http://sdphiladelphia.ilclassroom.com/wikis/29245717-kindergarten-errata?path=Wiki.11180076%2FWiki.28930691%2FWiki.9879318%2FWiki.10424770"
    
    driver = None
    
    try:
        print("\n🔐 Authenticating with ilclassroom.com...")
        
        # Perform login
        success = authenticator.login_with_selenium(username, password)
        
        if not success:
            print("❌ Authentication failed")
            return
        
        # Get the authenticated driver
        driver = authenticator.driver
        
        print("✅ Authentication successful!")
        
        print(f"\n📄 Navigating to Kindergarten Errata page...")
        driver.get(kindergarten_url)
        
        # Wait for page to load
        import time
        time.sleep(3)
        
        print("🔍 Extracting data from page...")
        errata_records = parser.parse_page_with_selenium(driver)
        
        print(f"\n📊 Extraction Results:")
        print(f"   Total records found: {len(errata_records)}")
        
        if errata_records:
            print(f"\n🗂️  Data by Unit:")
            
            # Group by unit
            units = {}
            for record in errata_records:
                unit = record['Unit']
                if unit not in units:
                    units[unit] = []
                units[unit].append(record)
            
            for unit_name, unit_records in units.items():
                print(f"\n📚 {unit_name}")
                print(f"    {len(unit_records)} record(s)")
                
                for i, record in enumerate(unit_records[:2]):  # Show first 2 per unit
                    print(f"\n    📝 Record {i+1}:")
                    print(f"       Resource: {record['Resource']}")
                    print(f"       Location: {record['Location']}")
                    print(f"       Page Numbers: {record['Page_Numbers']}")
                    print(f"       Improvement: {record['Improvement_Description'][:80]}...")
                    print(f"       Date Updated: {record['Date_Updated']}")
                
                if len(unit_records) > 2:
                    print(f"       ... and {len(unit_records) - 2} more records")
            
            print(f"\n📄 Sample CSV Output:")
            print("Date_Extracted,Unit,Resource,Location,Instructional_Moment,Page_Numbers,Improvement_Description,Improvement_Type,Date_Updated")
            
            # Show first 3 records as CSV
            for record in errata_records[:3]:
                csv_line = f"{record['Date_Extracted']},{record['Unit']},{record['Resource']},{record['Location']},{record['Instructional_Moment']},{record['Page_Numbers']},\"{record['Improvement_Description'][:50]}...\",{record['Improvement_Type']},{record['Date_Updated']}"
                print(csv_line)
            
            if len(errata_records) > 3:
                print(f"... and {len(errata_records) - 3} more records")
            
        else:
            print("❌ No errata records found")
            print("   This might indicate:")
            print("   - Page structure has changed")
            print("   - CSS selectors need updating")
            print("   - Page hasn't fully loaded")
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("\n🧹 Browser closed")

def show_expected_structure():
    """Show the expected data structure based on our previous analysis."""
    
    print("\n📋 Expected Data Structure (from previous analysis):")
    print("\nBased on our discovery, kindergarten errata pages contain:")
    print("• 3-6 accordion sections (units)")
    print("• Each section has a table with 3 columns:")
    print("  1. Component (Resource/Location info)")
    print("  2. Improvement Description")
    print("  3. Date Updated")
    
    print("\n📝 Sample Expected Records:")
    
    sample_records = [
        {
            'Date_Extracted': '2025-08-22',
            'Unit': 'Unit 1: Numbers And Counting',
            'Resource': 'Teacher Edition Glossary',
            'Location': '',
            'Instructional_Moment': '',
            'Page_Numbers': '346-347',
            'Improvement_Description': 'Updated definition for "number line" to include more visual examples and clearer language for kindergarten students.',
            'Improvement_Type': '',
            'Date_Updated': '2024-01-15'
        },
        {
            'Date_Extracted': '2025-08-22',
            'Unit': 'Unit 1: Numbers And Counting',
            'Resource': 'Student Workbook Unit 1',
            'Location': '',
            'Instructional_Moment': '',
            'Page_Numbers': '',
            'Improvement_Description': 'Corrected spelling error on page 12 and added missing number in counting sequence.',
            'Improvement_Type': '',
            'Date_Updated': '2024-01-10'
        },
        {
            'Date_Extracted': '2025-08-22',
            'Unit': 'Unit 2: Shapes And Patterns',
            'Resource': 'Teacher Edition',
            'Location': '',
            'Instructional_Moment': '',
            'Page_Numbers': '89-92',
            'Improvement_Description': 'Added additional scaffolding examples for students struggling with shape recognition concepts.',
            'Improvement_Type': '',
            'Date_Updated': '2024-01-20'
        }
    ]
    
    print(f"\n📊 Sample Output ({len(sample_records)} records):")
    
    for i, record in enumerate(sample_records):
        print(f"\n🔍 Record {i+1}:")
        print(f"  Unit: '{record['Unit']}'")
        print(f"  Resource: '{record['Resource']}'")
        print(f"  Page Numbers: '{record['Page_Numbers']}'")
        print(f"  Improvement: '{record['Improvement_Description']}'")
        print(f"  Date Updated: '{record['Date_Updated']}'")
    
    print(f"\n📄 Sample CSV Format:")
    print("Date_Extracted,Unit,Resource,Location,Instructional_Moment,Page_Numbers,Improvement_Description,Improvement_Type,Date_Updated")
    
    for record in sample_records:
        csv_line = f"{record['Date_Extracted']},{record['Unit']},{record['Resource']},{record['Location']},{record['Instructional_Moment']},{record['Page_Numbers']},\"{record['Improvement_Description']}\",{record['Improvement_Type']},{record['Date_Updated']}"
        print(csv_line)
    
    print(f"\n✨ To see actual data:")
    print("1. Update .env file with your credentials")
    print("2. Run: python sample_kindergarten.py")
    print("3. Or run full extraction: python extract_all.py")

if __name__ == "__main__":
    sample_kindergarten_extraction()
