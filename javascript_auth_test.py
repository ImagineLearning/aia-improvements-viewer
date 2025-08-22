#!/usr/bin/env python3
"""
JavaScript Authentication Test for IL Classroom
Handles Vue.js based login system
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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_selenium_driver(headless=True):
    """Set up Chrome driver for VPN/corporate environments"""
    chrome_options = Options()
    
    # Corporate VPN friendly options
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--remote-debugging-port=9222')
    
    # Add user agent to appear more like regular browser
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Conditional headless mode
    if headless:
        chrome_options.add_argument('--headless')
    
    # Disable images and CSS for faster loading (only in headless mode)
    if headless:
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
    
    try:
        # Try to use local Chrome driver first
        local_chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        
        chrome_binary = None
        for path in local_chrome_paths:
            if os.path.exists(path):
                chrome_binary = path
                break
        
        if chrome_binary:
            chrome_options.binary_location = chrome_binary
            # Try to create driver without webdriver manager first
            try:
                driver = webdriver.Chrome(options=chrome_options)
                driver.set_page_load_timeout(30)
                return driver
            except:
                pass
        
        # Fallback to webdriver manager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        logger.error(f"Failed to create Chrome driver: {e}")
        return None

def wait_for_vue_component(driver, component_id, timeout=20):
    """Wait for Vue.js component to load"""
    try:
        logger.info(f"Waiting for Vue component: {component_id}")
        
        # Wait for the component div to be present
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, component_id))
        )
        
        # Give Vue.js time to render the component content
        time.sleep(3)
        
        # Check if the component has been populated with content
        component = driver.find_element(By.ID, component_id)
        
        # Try to find login-related elements within the component
        login_elements = component.find_elements(By.CSS_SELECTOR, 
            'input[type="email"], input[type="text"], input[type="password"], button[type="submit"], .login-form, .sign-in')
        
        if login_elements:
            logger.info(f"Found {len(login_elements)} login-related elements in Vue component")
            return True
        else:
            logger.warning("Vue component loaded but no login elements found")
            return False
            
    except Exception as e:
        logger.error(f"Failed to wait for Vue component {component_id}: {e}")
        return False

def find_login_elements(driver):
    """Find login form elements in the Vue.js application"""
    logger.info("Searching for login elements...")
    
    # Common selectors for login forms
    email_selectors = [
        'input[type="email"]',
        'input[name="email"]',
        'input[placeholder*="email" i]',
        'input[id*="email" i]',
        'input[class*="email" i]'
    ]
    
    password_selectors = [
        'input[type="password"]',
        'input[name="password"]',
        'input[placeholder*="password" i]',
        'input[id*="password" i]',
        'input[class*="password" i]'
    ]
    
    submit_selectors = [
        'button[type="submit"]',
        'input[type="submit"]',
        'button:contains("Log in")',
        'button:contains("Sign in")',
        '.login-button',
        '.sign-in-button',
        'button[class*="login" i]',
        'button[class*="sign" i]'
    ]
    
    email_field = None
    password_field = None
    submit_button = None
    
    # Find email field
    for selector in email_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                email_field = elements[0]
                logger.info(f"Found email field with selector: {selector}")
                break
        except:
            continue
    
    # Find password field
    for selector in password_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                password_field = elements[0]
                logger.info(f"Found password field with selector: {selector}")
                break
        except:
            continue
    
    # Find submit button
    for selector in submit_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                submit_button = elements[0]
                logger.info(f"Found submit button with selector: {selector}")
                break
        except:
            continue
    
    # If no submit button found, look for any button that might work
    if not submit_button:
        try:
            buttons = driver.find_elements(By.TAG_NAME, 'button')
            for button in buttons:
                button_text = button.get_attribute('textContent').strip().lower()
                if any(word in button_text for word in ['log', 'sign', 'submit', 'enter']):
                    submit_button = button
                    logger.info(f"Found potential submit button with text: {button_text}")
                    break
        except:
            pass
    
    return email_field, password_field, submit_button

def test_javascript_auth():
    """Test JavaScript-based authentication"""
    
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
    
    driver = setup_selenium_driver(headless=False)  # Use visible browser for debugging
    if not driver:
        return False
    
    try:
        logger.info(f"Navigating to login page: {login_url}")
        driver.get(login_url)
        
        # Take initial screenshot
        driver.save_screenshot('login_page_loaded.png')
        logger.info("Saved screenshot: login_page_loaded.png")
        
        # Wait for Vue.js component to load
        if not wait_for_vue_component(driver, 'sessions-new-feature'):
            logger.error("Vue.js login component failed to load")
            return False
        
        # Take screenshot after Vue component loads
        driver.save_screenshot('vue_component_loaded.png')
        logger.info("Saved screenshot: vue_component_loaded.png")
        
        # Print page source for debugging
        with open('vue_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info("Saved page source: vue_page_source.html")
        
        # Find login elements
        email_field, password_field, submit_button = find_login_elements(driver)
        
        if not email_field:
            logger.error("Could not find email input field")
            return False
        
        if not password_field:
            logger.error("Could not find password input field")
            return False
        
        if not submit_button:
            logger.error("Could not find submit button")
            return False
        
        logger.info("All login elements found, attempting to login...")
        
        # Clear and fill email field
        email_field.clear()
        email_field.send_keys(email)
        logger.info("Email entered")
        
        # Clear and fill password field
        password_field.clear()
        password_field.send_keys(password)
        logger.info("Password entered")
        
        # Take screenshot before submitting
        driver.save_screenshot('before_submit.png')
        logger.info("Saved screenshot: before_submit.png")
        
        # Click submit button
        submit_button.click()
        logger.info("Submit button clicked")
        
        # Wait for response
        time.sleep(5)
        
        # Take screenshot after submitting
        driver.save_screenshot('after_submit.png')
        logger.info("Saved screenshot: after_submit.png")
        
        # Check if login was successful
        current_url = driver.current_url
        logger.info(f"Current URL after login attempt: {current_url}")
        
        # Look for success indicators
        if '/login' not in current_url or 'dashboard' in current_url or 'home' in current_url:
            logger.info("✅ Login appears successful!")
            
            # Save final page source
            with open('post_login_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.info("Saved post-login page source")
            
            return True
        else:
            logger.error("❌ Login failed - still on login page")
            
            # Check for error messages
            error_elements = driver.find_elements(By.CSS_SELECTOR, 
                '.error, .alert, .message, [class*="error"], [class*="alert"]')
            
            for error in error_elements:
                error_text = error.get_attribute('textContent').strip()
                if error_text:
                    logger.error(f"Error message found: {error_text}")
            
            return False
    
    except Exception as e:
        logger.error(f"Authentication test failed: {e}")
        return False
    
    finally:
        driver.quit()
        logger.info("Browser closed")

if __name__ == "__main__":
    logger.info("Starting JavaScript authentication test...")
    success = test_javascript_auth()
    
    if success:
        logger.info("🎉 JavaScript authentication test completed successfully!")
    else:
        logger.error("💥 JavaScript authentication test failed!")
        
        print("\n" + "="*60)
        print("TROUBLESHOOTING TIPS:")
        print("="*60)
        print("1. Check the screenshots generated:")
        print("   - login_page_loaded.png")
        print("   - vue_component_loaded.png") 
        print("   - before_submit.png")
        print("   - after_submit.png")
        print("\n2. Review the saved HTML files:")
        print("   - vue_page_source.html")
        print("   - post_login_source.html (if generated)")
        print("\n3. Verify your credentials in config/.env")
        print("4. Check if the website structure has changed")
        print("5. Try running with --headful mode to see browser interactions")
