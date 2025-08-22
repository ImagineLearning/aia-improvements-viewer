#!/usr/bin/env python3
"""
Script to find missing grade level URLs by testing patterns.
"""

import requests
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def setup_driver():
    """Set up Chrome driver."""
    chrome_options = Options()
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

def login(driver, email, password):
    """Login to the site."""
    base_url = "http://sdphiladelphia.ilclassroom.com"
    login_url = f"{base_url}/login"
    
    print(f"🔐 Logging in at: {login_url}")
    driver.get(login_url)
    
    # Wait for Vue.js component
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "sessions-new-feature"))
    )
    time.sleep(3)
    
    # Fill login form
    email_field = driver.find_element(By.NAME, "auth_key")
    password_field = driver.find_element(By.NAME, "password")
    
    email_field.clear()
    email_field.send_keys(email)
    password_field.clear()
    password_field.send_keys(password)
    
    # Submit
    password_field.send_keys(Keys.RETURN)
    time.sleep(5)
    
    current_url = driver.current_url
    if "/login" not in current_url and ("welcome" in current_url or "resources" in current_url):
        print(f"✅ Login successful!")
        return True
    else:
        print(f"❌ Login failed!")
        return False

def test_url_patterns():
    """Test different URL patterns to find missing grade levels."""
    
    # Load credentials
    from dotenv import load_dotenv
    load_dotenv()
    
    email = os.getenv('ERRATA_USERNAME')
    password = os.getenv('ERRATA_PASSWORD')
    
    if not email or not password:
        print("❌ Please set credentials in .env file")
        return
    
    driver = setup_driver()
    
    try:
        # Login
        if not login(driver, email, password):
            return
        
        base_url = "http://sdphiladelphia.ilclassroom.com"
        
        # Known working URLs for reference
        known_urls = [
            "/wikis/29245717-kindergarten-errata",
            "/wikis/18746473-grade-1-errata", 
            "/wikis/20692555-grade-6-errata",
            "/wikis/34717795-algebra-1-errata",
            "/wikis/34803461-geometry-errata"
        ]
        
        print("\n🔍 Testing known URLs first:")
        for url in known_urls:
            full_url = base_url + url
            print(f"Testing: {url}")
            driver.get(full_url)
            time.sleep(2)
            
            title = driver.title
            if "errata" in title.lower() or "not found" not in title.lower():
                print(f"  ✅ {title}")
            else:
                print(f"  ❌ {title}")
        
        print("\n🔍 Now let's search for grade-level pages...")
        
        # Try to find a wiki or navigation page that might list all errata pages
        search_urls = [
            "/search?q=errata",
            "/wikis?search=errata", 
            "/wikis/11180076-welcome-to-il-classroom",  # Main wiki
            "/resources/11180076-welcome-to-il-classroom"  # Main resources
        ]
        
        for search_url in search_urls:
            print(f"\n🔎 Checking: {search_url}")
            driver.get(base_url + search_url)
            time.sleep(3)
            
            # Look for links containing 'errata'
            try:
                links = driver.find_elements(By.XPATH, "//a[contains(@href, 'errata') or contains(text(), 'errata')]")
                print(f"  Found {len(links)} potential errata links:")
                
                for link in links[:10]:  # Show first 10
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if href and 'errata' in href.lower():
                        print(f"    {text}: {href}")
                        
            except Exception as e:
                print(f"  Error searching: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    test_url_patterns()
