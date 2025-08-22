#!/usr/bin/env python3
"""
Kindergarten data extraction using the EXACT working authentication method.
"""

import os
import sys
import time
import yaml
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import logging

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from parser import ErrataParser

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_kindergarten_data_working():
    """Extract kindergarten data using the EXACT working authentication."""
    
    print("🎯 Kindergarten Data Extraction - EXACT Working Method")
    print("=" * 60)
    
    # Load credentials using the EXACT same method that works
    try:
        with open('config/.env', 'r') as f:
            lines = f.readlines()
        
        email = None
        password = None
        for line in lines:
            if line.startswith('USERNAME=') or line.startswith('EMAIL='):
                email = line.split('=', 1)[1].strip()
            elif line.startswith('PASSWORD='):
                password = line.split('=', 1)[1].strip()
        
        if not email or not password:
            logger.error("Email or password not found in config/.env file")
            return False
            
        logger.info(f"Using credentials: {email}")
            
    except Exception as e:
        logger.error(f"Failed to load credentials: {e}")
        return False
    
    # Load configuration
    try:
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        base_url = config['website']['base_url']
        
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return False
    
    # Initialize parser
    parser = ErrataParser(config)
    
    # Set up Chrome with the EXACT same options
    chrome_options = Options()
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        # Login using the EXACT same approach that works
        login_url = f"{base_url}/login"
        logger.info(f"🌐 Logging in at: {login_url}")
        driver.get(login_url)
        
        # Wait for Vue.js component - EXACT same as working version
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "sessions-new-feature"))
        )
        time.sleep(3)
        
        # Fill login form with EXACT same field names
        email_field = driver.find_element(By.NAME, "auth_key")
        password_field = driver.find_element(By.NAME, "password")
        
        email_field.clear()
        email_field.send_keys(email)
        password_field.clear()
        password_field.send_keys(password)
        
        # Submit with Enter key - EXACT same as working version
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)
        
        current_url = driver.current_url
        if "/login" not in current_url and ("welcome" in current_url or "resources" in current_url):
            logger.info(f"✅ Login successful! Current URL: {current_url}")
        else:
            logger.error(f"❌ Login failed! URL: {current_url}")
            return False
        
        # Navigate to kindergarten errata page
        kindergarten_url = f"{base_url}/wikis/29245717-kindergarten-errata?path=Wiki.11180076%2FWiki.28930691%2FWiki.9879318%2FWiki.10424770"
        
        print(f"\n📄 Navigating to Kindergarten errata page...")
        driver.get(kindergarten_url)
        time.sleep(5)
        
        page_title = driver.title
        print(f"✅ Page loaded: {page_title}")
        
        # NOW use our updated parser on the authenticated page
        print("\n🔍 Extracting data with our parser...")
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
                print(f"    📊 {len(unit_records)} record(s)")
                
                for i, record in enumerate(unit_records[:2]):  # Show first 2 per unit
                    print(f"\n    📝 Record {i+1}:")
                    print(f"       🎓 Grade Level: {record['Grade_Level']}")
                    print(f"       📖 Resource: {record['Resource']}")
                    print(f"       📍 Location: {record['Location']}")
                    print(f"       📄 Page Numbers: {record['Page_Numbers']}")
                    print(f"       ✏️  Improvement: {record['Improvement_Description'][:80]}...")
                    print(f"       📅 Date Updated: {record['Date_Updated']}")
                
                if len(unit_records) > 2:
                    print(f"       ... and {len(unit_records) - 2} more records")
            
            print(f"\n📄 Sample CSV Output (first 3 records):")
            print("Date_Extracted,Grade_Level,Unit,Resource,Location,Instructional_Moment,Page_Numbers,Improvement_Description,Improvement_Type,Date_Updated")
            
            # Show first 3 records as CSV
            for i, record in enumerate(errata_records[:3]):
                escaped_description = record['Improvement_Description'].replace('"', '""')
                csv_line = f"{record['Date_Extracted']},\"{record['Grade_Level']}\",\"{record['Unit']}\",\"{record['Resource']}\",\"{record['Location']}\",\"{record['Instructional_Moment']}\",\"{record['Page_Numbers']}\",\"{escaped_description[:100]}...\",\"{record['Improvement_Type']}\",{record['Date_Updated']}"
                print(f"Row {i+1}: {csv_line}")
            
            if len(errata_records) > 3:
                print(f"... and {len(errata_records) - 3} more records")
            
            print(f"\n🎉 SUCCESS! Extracted {len(errata_records)} records from Kindergarten errata!")
            print(f"✅ The system is working! Ready for full extraction.")
            
        else:
            print("❌ No errata records found")
            print("   Let's debug what's on the page...")
            
            # Debug: check for accordion sections manually  
            accordions = driver.find_elements(By.CSS_SELECTOR, ".section-accordion")
            print(f"   🔍 Found {len(accordions)} accordion sections")
            
            if accordions:
                for i, section in enumerate(accordions[:2]):
                    try:
                        button = section.find_element(By.CSS_SELECTOR, "button")
                        print(f"   📚 Section {i+1}: {button.text}")
                        
                        # Check for tables
                        tables = section.find_elements(By.CSS_SELECTOR, "table")
                        print(f"   📊 Tables in section: {len(tables)}")
                        
                        if tables:
                            rows = section.find_elements(By.CSS_SELECTOR, "tbody tr")
                            print(f"   📝 Rows in tables: {len(rows)}")
                    except Exception as e:
                        print(f"   ❌ Error checking section {i+1}: {e}")
            else:
                # Look for any tables at all
                all_tables = driver.find_elements(By.CSS_SELECTOR, "table")
                print(f"   📊 Total tables on page: {len(all_tables)}")
        
        return len(errata_records) > 0
        
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if driver:
            driver.quit()
            print("\n🧹 Browser closed")

if __name__ == "__main__":
    success = extract_kindergarten_data_working()
    if success:
        print("\n🎯 Kindergarten data extraction successful!")
        print("🚀 Ready to run full extraction: python extract_all.py")
    else:
        print("\n❌ Kindergarten data extraction failed")
