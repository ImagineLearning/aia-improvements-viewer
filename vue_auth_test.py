#!/usr/bin/env python3
"""
Working Vue.js Authentication for IL Classroom
Using the discovered form elements
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

def authenticate_with_vue():
    """Authenticate using discovered Vue.js form elements"""
    
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
            
        logger.info(f"Using credentials: {email} / {'*' * len(password)}")
            
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
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        logger.info(f"🌐 Navigating to login page: {login_url}")
        driver.get(login_url)
        
        # Wait for Vue.js component to load
        logger.info("⏳ Waiting for Vue.js login component...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "sessions-new-feature"))
        )
        
        # Give Vue.js time to render the form
        time.sleep(3)
        
        # Find the actual login form elements (discovered from our test)
        logger.info("🔍 Finding login form elements...")
        
        # Get CSRF token from meta tag
        try:
            csrf_token_element = driver.find_element(By.CSS_SELECTOR, 'meta[name="csrf-token"]')
            csrf_token = csrf_token_element.get_attribute('content')
            logger.info(f"✅ Found CSRF token: {csrf_token[:10]}...")
        except Exception as e:
            logger.warning(f"⚠️ Could not find CSRF token: {e}")
            csrf_token = None
        
        # Find email field by name attribute
        try:
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "auth_key"))
            )
            logger.info("✅ Found email field")
        except Exception as e:
            logger.error(f"❌ Could not find email field: {e}")
            driver.save_screenshot('email_field_error.png')
            return False
        
        # Find password field by name attribute
        try:
            password_field = driver.find_element(By.NAME, "password")
            logger.info("✅ Found password field")
        except Exception as e:
            logger.error(f"❌ Could not find password field: {e}")
            driver.save_screenshot('password_field_error.png')
            return False
        
        # Find CSRF token field (authenticity_token)
        try:
            authenticity_token_field = driver.find_element(By.NAME, "authenticity_token")
            logger.info("✅ Found authenticity token field")
        except Exception as e:
            logger.warning(f"⚠️ Could not find authenticity token field: {e}")
            authenticity_token_field = None
        
        # Find submit button by text content
        try:
            submit_buttons = driver.find_elements(By.TAG_NAME, "button")
            submit_button = None
            for button in submit_buttons:
                if button.get_attribute('textContent').strip() == 'Log in':
                    submit_button = button
                    break
            
            if not submit_button:
                raise Exception("Submit button with 'Log in' text not found")
            
            logger.info("✅ Found submit button")
        except Exception as e:
            logger.error(f"❌ Could not find submit button: {e}")
            driver.save_screenshot('submit_button_error.png')
            return False
        
        # Take screenshot before filling
        driver.save_screenshot('before_filling.png')
        logger.info("📸 Screenshot saved: before_filling.png")
        
        # Fill in the form
        logger.info("📝 Filling in credentials...")
        
        # Fill CSRF token if available
        if authenticity_token_field and csrf_token:
            try:
                authenticity_token_field.clear()
                authenticity_token_field.send_keys(csrf_token)
                logger.info("🔒 CSRF token filled")
            except Exception as e:
                logger.warning(f"⚠️ Could not fill CSRF token: {e}")
        
        # Clear and fill email field
        email_field.clear()
        email_field.send_keys(email)
        logger.info("✉️ Email entered")
        
        # Clear and fill password field
        password_field.clear()
        password_field.send_keys(password)
        logger.info("🔒 Password entered")
        
        # Take screenshot before submitting
        driver.save_screenshot('before_submit.png')
        logger.info("📸 Screenshot saved: before_submit.png")
        
        # Click submit button
        logger.info("🚀 Submitting login form...")
        submit_button.click()
        
        # Wait for response
        logger.info("⏳ Waiting for authentication response...")
        time.sleep(5)
        
        # Take screenshot after submitting
        driver.save_screenshot('after_submit.png')
        logger.info("📸 Screenshot saved: after_submit.png")
        
        # Check if login was successful
        current_url = driver.current_url
        logger.info(f"📍 Current URL after login: {current_url}")
        
        # Check for success indicators
        success_indicators = [
            '/login' not in current_url,
            'dashboard' in current_url.lower(),
            'home' in current_url.lower(),
            'wikis' in current_url.lower()
        ]
        
        login_success = any(success_indicators)
        
        if login_success:
            logger.info("🎉 LOGIN SUCCESSFUL!")
            logger.info(f"✅ Redirected to: {current_url}")
            
            # Save successful login page
            with open('successful_login_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.info("💾 Saved successful login page: successful_login_page.html")
            
            # Take final success screenshot
            driver.save_screenshot('login_success.png')
            logger.info("📸 Success screenshot saved: login_success.png")
            
        else:
            logger.error("❌ LOGIN FAILED")
            logger.error(f"Still at URL: {current_url}")
            
            # Look for error messages
            try:
                error_selectors = [
                    '.error', '.alert', '.message', '.flash-message',
                    '[class*="error"]', '[class*="alert"]', '[class*="invalid"]'
                ]
                
                for selector in error_selectors:
                    error_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for error in error_elements:
                        error_text = error.get_attribute('textContent').strip()
                        if error_text and len(error_text) > 0:
                            logger.error(f"🚨 Error message: {error_text}")
                            
            except Exception as e:
                logger.warning(f"Could not check for error messages: {e}")
            
            # Save error page
            with open('login_error_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.info("💾 Saved error page: login_error_page.html")
        
        driver.quit()
        return login_success
        
    except Exception as e:
        logger.error(f"Authentication failed with error: {e}")
        if 'driver' in locals():
            driver.save_screenshot('authentication_error.png')
            driver.quit()
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting Vue.js Authentication Test...")
    success = authenticate_with_vue()
    
    print("\n" + "="*60)
    if success:
        print("🎉 AUTHENTICATION SUCCESSFUL!")
        print("="*60)
        print("The login process worked! Check these files:")
        print("✅ successful_login_page.html - Post-login page content")
        print("✅ login_success.png - Success screenshot")
        print("✅ before_filling.png - Form before filling")
        print("✅ before_submit.png - Form after filling")
        print("✅ after_submit.png - Response after submission")
    else:
        print("❌ AUTHENTICATION FAILED!")
        print("="*60)
        print("Check these debugging files:")
        print("🔍 login_error_page.html - Error page content")
        print("🔍 *_error.png - Error screenshots")
        print("🔍 before_*.png - Screenshots during process")
        print("\nTroubleshooting suggestions:")
        print("1. Verify credentials in config/.env")
        print("2. Check if website requires different login method")
        print("3. Look for CAPTCHA or additional verification")
        print("4. Check error messages in saved HTML files")
