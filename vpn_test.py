#!/usr/bin/env python3
"""
VPN-compatible test using existing Chrome driver.
"""

import os
import time
import ssl
import certifi
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging

# Disable SSL warnings and set up for VPN
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_chrome_driver_vpn():
    """Set up Chrome WebDriver with VPN-compatible settings."""
    chrome_options = Options()
    
    # VPN-friendly options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--ignore-certificate-errors-spki-list")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    # Try to use system Chrome driver first
    try:
        # Try common Chrome driver locations
        possible_paths = [
            "chromedriver.exe",
            "C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe",
            "C:\\Windows\\System32\\chromedriver.exe"
        ]
        
        driver_path = None
        for path in possible_paths:
            if os.path.exists(path):
                driver_path = path
                break
        
        if driver_path:
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            # Try without explicit service (uses system PATH)
            driver = webdriver.Chrome(options=chrome_options)
        
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(60)  # Longer timeout for VPN
        return driver
        
    except Exception as e:
        logger.error(f"Failed to create Chrome driver: {e}")
        
        # Fallback: try with webdriver-manager but disable SSL verification
        try:
            os.environ['WDM_SSL_VERIFY'] = '0'
            from webdriver_manager.chrome import ChromeDriverManager
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            driver.set_page_load_timeout(60)
            return driver
        except Exception as e2:
            logger.error(f"Fallback also failed: {e2}")
            raise

def vpn_login_test():
    """VPN-compatible login test."""
    
    print("🔍 VPN-Compatible Kindergarten Data Test")
    print("=" * 50)
    
    # Load credentials from .env
    username = os.getenv('ERRATA_USERNAME')
    password = os.getenv('ERRATA_PASSWORD')
    
    if not username or not password:
        print("❌ Credentials not found in environment variables")
        return
    
    print(f"📧 Using username: {username}")
    
    driver = None
    
    try:
        # Set up driver
        print("🔧 Setting up VPN-compatible Chrome browser...")
        driver = setup_chrome_driver_vpn()
        print("✅ Chrome driver setup successful!")
        
        # Navigate to login page
        print("🌐 Navigating to login page...")
        login_url = "http://sdphiladelphia.ilclassroom.com/login"
        driver.get(login_url)
        print(f"📄 Page loaded: {driver.title}")
        time.sleep(3)
        
        # Find and fill login form
        print("🔐 Filling login form...")
        
        # Try different username field selectors
        username_selectors = ["#user_email", "#email", "input[name='user[email]']", "input[type='email']"]
        username_field = None
        
        for selector in username_selectors:
            try:
                username_field = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Found username field with selector: {selector}")
                break
            except:
                continue
        
        if not username_field:
            print("❌ Could not find username field")
            # Show page source snippet for debugging
            page_source = driver.page_source[:1000]
            print(f"Page source preview: {page_source}")
            return
        
        username_field.clear()
        username_field.send_keys(username)
        print("✅ Username entered")
        
        # Find password field
        password_selectors = ["#user_password", "#password", "input[name='user[password]']", "input[type='password']"]
        password_field = None
        
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Found password field with selector: {selector}")
                break
            except:
                continue
        
        if not password_field:
            print("❌ Could not find password field")
            # Show all input fields for debugging
            inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"Found {len(inputs)} input fields:")
            for inp in inputs:
                input_type = inp.get_attribute("type")
                input_name = inp.get_attribute("name")
                input_id = inp.get_attribute("id")
                print(f"  Type: {input_type}, Name: {input_name}, ID: {input_id}")
            return
        
        password_field.clear()
        password_field.send_keys(password)
        print("✅ Password entered")
        
        # Submit form
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            submit_button.click()
            print("✅ Login form submitted")
        except Exception as e:
            print(f"❌ Could not find/click submit button: {e}")
            return
        
        print("⏳ Waiting for login to complete...")
        time.sleep(5)
        
        # Check if login was successful
        current_url = driver.current_url
        if "login" in current_url:
            print("❌ Login appears to have failed - still on login page")
            print(f"Current URL: {current_url}")
            print(f"Page title: {driver.title}")
            return
        else:
            print("✅ Login appears successful!")
            print(f"Current URL: {current_url}")
            print(f"Page title: {driver.title}")
        
        # Navigate to kindergarten errata page
        print("\n📄 Navigating to kindergarten errata page...")
        kindergarten_url = "http://sdphiladelphia.ilclassroom.com/wikis/29245717-kindergarten-errata?path=Wiki.11180076%2FWiki.28930691%2FWiki.9879318%2FWiki.10424770"
        driver.get(kindergarten_url)
        time.sleep(5)
        
        print(f"📄 Errata page loaded: {driver.title}")
        
        # Look for accordion sections
        print("🔍 Looking for accordion sections...")
        accordion_sections = driver.find_elements(By.CSS_SELECTOR, ".section-accordion")
        
        print(f"📊 Found {len(accordion_sections)} accordion sections")
        
        if accordion_sections:
            print("\n🗂️  Processing accordion sections:")
            total_records = 0
            
            for i, section in enumerate(accordion_sections):
                try:
                    button = section.find_element(By.CSS_SELECTOR, "button")
                    unit_name = button.text.strip()
                    print(f"\n   📚 Section {i+1}: {unit_name}")
                    
                    # Expand if collapsed
                    if button.get_attribute("aria-expanded") == "false":
                        print(f"      ⬇️  Expanding section...")
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(1)
                    
                    # Look for tables and extract data
                    tables = section.find_elements(By.CSS_SELECTOR, "table")
                    print(f"      📊 Found {len(tables)} table(s)")
                    
                    if tables:
                        rows = section.find_elements(By.CSS_SELECTOR, "tbody tr")
                        print(f"      📝 Found {len(rows)} data row(s)")
                        total_records += len(rows)
                        
                        # Show first few rows as samples
                        for j, row in enumerate(rows[:2]):  # Show first 2 rows
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) >= 3:
                                component = cells[0].text.strip()
                                improvement = cells[1].text.strip()
                                date_updated = cells[2].text.strip()
                                
                                print(f"         🔍 Record {j+1}:")
                                print(f"            Component: {component[:50]}...")
                                print(f"            Improvement: {improvement[:50]}...")
                                print(f"            Date: {date_updated}")
                        
                        if len(rows) > 2:
                            print(f"         ... and {len(rows) - 2} more records")
                    
                except Exception as e:
                    print(f"      ❌ Error processing section {i+1}: {e}")
            
            print(f"\n📈 Summary:")
            print(f"   Total sections: {len(accordion_sections)}")
            print(f"   Total records found: {total_records}")
            
            if total_records > 0:
                print("\n✅ SUCCESS! Data extraction is working!")
                print("   You can now run the full extraction with:")
                print("   python extract_all.py")
            else:
                print("\n⚠️  No data records found in tables")
        else:
            print("❌ No accordion sections found")
            print("   Checking page content...")
            
            # Debug: look for any content
            all_text = driver.find_element(By.TAG_NAME, "body").text
            if "errata" in all_text.lower():
                print("   ✅ Found 'errata' text on page")
            else:
                print("   ❌ No 'errata' text found")
                
            print(f"   Page text preview: {all_text[:200]}...")
        
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
    
    vpn_login_test()
