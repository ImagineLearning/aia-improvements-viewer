#!/usr/bin/env python3
"""
Simple Selenium test without webdriver manager
"""

import os
import time
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_simple_selenium():
    """Simple Selenium test"""
    
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
            
    except Exception as e:
        logger.error(f"Failed to load credentials: {e}")
        return False
    
    # Load configuration
    try:
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        base_url = config['website']['base_url']
        login_url = f"{base_url}/login"
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
        # Try to create driver without service specification
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        logger.info(f"Navigating to login page: {login_url}")
        driver.get(login_url)
        
        # Wait a bit for page to load
        time.sleep(5)
        
        # Take screenshot
        driver.save_screenshot('simple_test.png')
        logger.info("Screenshot saved: simple_test.png")
        
        # Print current URL
        logger.info(f"Current URL: {driver.current_url}")
        
        # Print page title
        logger.info(f"Page title: {driver.title}")
        
        # Look for Vue component
        try:
            vue_component = driver.find_element(By.ID, "sessions-new-feature")
            logger.info("✅ Found Vue.js login component!")
            
            # Wait for it to load content
            time.sleep(3)
            
            # Take another screenshot
            driver.save_screenshot('vue_loaded.png')
            logger.info("Screenshot with Vue component saved: vue_loaded.png")
            
        except Exception as e:
            logger.error(f"Vue component not found: {e}")
        
        # Try to find any input fields
        inputs = driver.find_elements(By.TAG_NAME, 'input')
        logger.info(f"Found {len(inputs)} input elements")
        
        for i, inp in enumerate(inputs):
            input_type = inp.get_attribute('type')
            input_name = inp.get_attribute('name')
            input_placeholder = inp.get_attribute('placeholder')
            logger.info(f"Input {i}: type={input_type}, name={input_name}, placeholder={input_placeholder}")
        
        # Try to find any buttons
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        logger.info(f"Found {len(buttons)} button elements")
        
        for i, btn in enumerate(buttons):
            button_text = btn.get_attribute('textContent').strip()
            button_type = btn.get_attribute('type')
            logger.info(f"Button {i}: text='{button_text}', type={button_type}")
        
        # Save page source
        with open('simple_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info("Page source saved: simple_page_source.html")
        
        driver.quit()
        return True
        
    except Exception as e:
        logger.error(f"Selenium test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting simple Selenium test...")
    success = test_simple_selenium()
    
    if success:
        logger.info("🎉 Simple Selenium test completed!")
    else:
        logger.error("💥 Simple Selenium test failed!")
