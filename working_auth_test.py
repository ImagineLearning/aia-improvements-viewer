#!/usr/bin/env python3
"""
Working Authentication Test for IL Classroom
Based on the successful error_detection.py approach
"""

import os
import time
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_working_login():
    """Test the working login approach and navigate to errata pages"""
    
    # Load credentials
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
            logger.error("Email or password not found in .env file")
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
        errata_pages = config['website']['errata_pages']
        
        # Create a mapping of grade names to URLs
        grade_names = [
            "Kindergarten", "Grade 1", "Grade 6", "Algebra 1", "Geometry"
        ]
        grade_urls = dict(zip(grade_names, errata_pages))
        
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return False
    
    chrome_options = Options()
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        # Login
        login_url = f"{base_url}/login"
        logger.info(f"🌐 Logging in at: {login_url}")
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
        
        # Submit with Enter key
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)
        
        current_url = driver.current_url
        if "/login" not in current_url and ("welcome" in current_url or "resources" in current_url):
            logger.info(f"✅ Login successful! Current URL: {current_url}")
        else:
            logger.error(f"❌ Login failed! URL: {current_url}")
            return False
        
        # Now test each errata page
        logger.info("🔍 Testing errata page access...")
        errata_results = {}
        
        for grade, url_path in grade_urls.items():
            full_url = base_url + url_path
            logger.info(f"\n📚 Testing {grade}: {full_url}")
            
            try:
                driver.get(full_url)
                time.sleep(3)
                
                # Take screenshot for analysis
                screenshot_name = f"errata_{grade.replace(' ', '_').lower()}.png"
                driver.save_screenshot(screenshot_name)
                
                # Check page title and basic content
                page_title = driver.title
                logger.info(f"  Page title: {page_title}")
                
                # Look for common errata indicators
                errata_indicators = [
                    "errata", "corrections", "changes", "updates", "revisions",
                    "amendments", "modifications", "fixes"
                ]
                
                page_text = driver.page_source.lower()
                found_indicators = [ind for ind in errata_indicators if ind in page_text]
                
                if found_indicators:
                    logger.info(f"  ✅ Found errata indicators: {found_indicators}")
                else:
                    logger.warning(f"  ⚠️ No errata indicators found")
                
                # Look for tables, lists, or structured content
                tables = driver.find_elements(By.TAG_NAME, "table")
                lists = driver.find_elements(By.TAG_NAME, "ul")
                divs = driver.find_elements(By.TAG_NAME, "div")
                
                logger.info(f"  Content structure: {len(tables)} tables, {len(lists)} lists, {len(divs)} divs")
                
                # Save page source for analysis
                with open(f"errata_{grade.replace(' ', '_').lower()}.html", 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                
                errata_results[grade] = {
                    'url': full_url,
                    'title': page_title,
                    'indicators': found_indicators,
                    'tables': len(tables),
                    'lists': len(lists),
                    'accessible': True
                }
                
            except Exception as e:
                logger.error(f"  ❌ Error accessing {grade}: {e}")
                errata_results[grade] = {
                    'url': full_url,
                    'error': str(e),
                    'accessible': False
                }
        
        # Summary
        logger.info("\n📊 ERRATA PAGE ACCESS SUMMARY:")
        for grade, result in errata_results.items():
            if result.get('accessible'):
                logger.info(f"✅ {grade}: {result['title']}")
                if result['indicators']:
                    logger.info(f"   Errata indicators: {result['indicators']}")
                logger.info(f"   Structure: {result['tables']} tables, {result['lists']} lists")
            else:
                logger.error(f"❌ {grade}: {result.get('error', 'Unknown error')}")
        
        return errata_results
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
    
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    logger.info("🚀 Starting working authentication test...")
    results = test_working_login()
    
    if results:
        logger.info("✅ Authentication test completed successfully!")
        
        # Check if we found any errata content
        accessible_pages = [grade for grade, data in results.items() if data.get('accessible')]
        logger.info(f"\n📈 Results: {len(accessible_pages)} pages accessible")
        
        # Look for pages with errata indicators
        pages_with_errata = [
            grade for grade, data in results.items() 
            if data.get('accessible') and data.get('indicators')
        ]
        
        if pages_with_errata:
            logger.info(f"🎯 Found errata content on: {pages_with_errata}")
        else:
            logger.warning("⚠️ No obvious errata indicators found - may need manual selector identification")
    else:
        logger.error("❌ Authentication test failed!")
