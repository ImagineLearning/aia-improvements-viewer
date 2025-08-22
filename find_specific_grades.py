#!/usr/bin/env python3
"""
Test specific grade URLs to find Grade 4, Grade 7, and Algebra 2.
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
    
    print(f"🔐 Logging in...")
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

def test_specific_urls():
    """Test specific URLs for missing grades."""
    
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
        
        # Search for more specific terms
        search_terms = ["grade 4", "grade 7", "algebra 2", "algebra-2", "errata"]
        
        for term in search_terms:
            print(f"\n🔍 Searching for: '{term}'")
            search_url = f"{base_url}/search?q={term.replace(' ', '+')}"
            driver.get(search_url)
            time.sleep(3)
            
            # Look for errata links
            try:
                links = driver.find_elements(By.XPATH, "//a[contains(@href, 'errata')]")
                errata_links = []
                
                for link in links:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if href and 'errata' in href.lower():
                        errata_links.append((text, href))
                
                # Remove duplicates and show unique URLs
                unique_links = {}
                for text, href in errata_links:
                    if href not in unique_links:
                        unique_links[href] = text
                
                print(f"  Found {len(unique_links)} unique errata URLs:")
                for href, text in unique_links.items():
                    # Extract just the path part
                    path = href.replace(base_url, '') if base_url in href else href
                    print(f"    {text}: {path}")
                        
            except Exception as e:
                print(f"  Error searching: {e}")
    
    finally:
        driver.quit()
        print("\n🧹 Browser closed")

if __name__ == "__main__":
    test_specific_urls()
