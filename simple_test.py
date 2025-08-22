#!/usr/bin/env python3
"""
Simple test to verify authentication and extract kindergarten data.
"""

import os
import time
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_chrome_driver():
    """Set up Chrome WebDriver with minimal options."""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        logger.error(f"Failed to create Chrome driver: {e}")
        raise

def simple_login_test():
    """Simple login test to the kindergarten page."""
    
    print("🔍 Simple Kindergarten Data Extraction Test")
    print("=" * 50)
    
    # Load credentials from .env
    username = os.getenv('ERRATA_USERNAME')
    password = os.getenv('ERRATA_PASSWORD')
    
    if not username or not password:
        print("❌ Credentials not found in environment variables")
        print("   Make sure .env file has ERRATA_USERNAME and ERRATA_PASSWORD")
        return
    
    print(f"📧 Using username: {username}")
    
    driver = None
    
    try:
        # Set up driver
        print("🔧 Setting up Chrome browser...")
        driver = setup_chrome_driver()
        
        # Navigate to login page
        print("🌐 Navigating to login page...")
        login_url = "http://sdphiladelphia.ilclassroom.com/login"
        driver.get(login_url)
        time.sleep(3)
        
        # Find and fill login form
        print("🔐 Filling login form...")
        
        # Try different username field selectors
        username_selectors = ["#user_email", "#email", "input[name='user[email]']"]
        username_field = None
        
        for selector in username_selectors:
            try:
                username_field = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
        
        if not username_field:
            print("❌ Could not find username field")
            return
        
        username_field.clear()
        username_field.send_keys(username)
        
        # Find password field
        password_field = driver.find_element(By.CSS_SELECTOR, "#user_password")
        password_field.clear()
        password_field.send_keys(password)
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        submit_button.click()
        
        print("⏳ Waiting for login to complete...")
        time.sleep(5)
        
        # Check if login was successful
        current_url = driver.current_url
        if "login" in current_url:
            print("❌ Login appears to have failed - still on login page")
            print(f"Current URL: {current_url}")
            return
        else:
            print("✅ Login appears successful!")
            print(f"Current URL: {current_url}")
        
        # Navigate to kindergarten errata page
        print("📄 Navigating to kindergarten errata page...")
        kindergarten_url = "http://sdphiladelphia.ilclassroom.com/wikis/29245717-kindergarten-errata?path=Wiki.11180076%2FWiki.28930691%2FWiki.9879318%2FWiki.10424770"
        driver.get(kindergarten_url)
        time.sleep(5)
        
        # Look for accordion sections
        print("🔍 Looking for accordion sections...")
        accordion_sections = driver.find_elements(By.CSS_SELECTOR, ".section-accordion")
        
        print(f"📊 Found {len(accordion_sections)} accordion sections")
        
        if accordion_sections:
            print("\n🗂️  Accordion sections found:")
            for i, section in enumerate(accordion_sections[:3]):  # First 3 sections
                try:
                    button = section.find_element(By.CSS_SELECTOR, "button")
                    unit_name = button.text.strip()
                    print(f"   {i+1}. {unit_name}")
                    
                    # Try to expand and look for tables
                    if button.get_attribute("aria-expanded") == "false":
                        print(f"      Expanding section...")
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(1)
                    
                    # Look for tables
                    tables = section.find_elements(By.CSS_SELECTOR, "table")
                    print(f"      Found {len(tables)} table(s)")
                    
                    if tables:
                        rows = section.find_elements(By.CSS_SELECTOR, "tbody tr")
                        print(f"      Found {len(rows)} data row(s)")
                        
                        # Show first row as sample
                        if rows:
                            cells = rows[0].find_elements(By.TAG_NAME, "td")
                            if len(cells) >= 3:
                                print(f"      Sample: {cells[0].text[:50]}... | {cells[1].text[:30]}... | {cells[2].text}")
                    
                except Exception as e:
                    print(f"      Error processing section {i+1}: {e}")
        else:
            print("❌ No accordion sections found")
            print("   The page structure might be different than expected")
            
            # Let's see what's actually on the page
            print("\n🔍 Page analysis:")
            print(f"   Page title: {driver.title}")
            print(f"   Page URL: {driver.current_url}")
            
            # Look for any tables
            all_tables = driver.find_elements(By.CSS_SELECTOR, "table")
            print(f"   Total tables found: {len(all_tables)}")
            
            # Look for common content indicators
            content_divs = driver.find_elements(By.CSS_SELECTOR, ".content, .main-content, .wiki-content")
            print(f"   Content divs found: {len(content_divs)}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            print("\n🧹 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    simple_login_test()
