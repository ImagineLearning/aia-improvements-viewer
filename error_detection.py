#!/usr/bin/env python3
"""
Error Detection Script for IL Classroom Login
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

def detect_login_errors():
    """Look for login errors and try different authentication approaches"""
    
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
        
        # Find all form elements to understand the page structure
        forms = driver.find_elements(By.TAG_NAME, "form")
        logger.info(f"🔍 Found {len(forms)} form(s)")
        
        for i, form in enumerate(forms):
            logger.info(f"Form {i}:")
            logger.info(f"  Action: {form.get_attribute('action')}")
            logger.info(f"  Method: {form.get_attribute('method')}")
            
            # Find all inputs in this form
            inputs = form.find_elements(By.TAG_NAME, "input")
            logger.info(f"  Inputs: {len(inputs)}")
            for j, inp in enumerate(inputs):
                input_type = inp.get_attribute('type')
                input_name = inp.get_attribute('name')
                input_value = inp.get_attribute('value')[:20] if inp.get_attribute('value') else ''
                logger.info(f"    Input {j}: name='{input_name}', type='{input_type}', value='{input_value}...'")
        
        # Try to find and fill the login form properly
        try:
            # Method 1: Try finding the form and submitting it properly
            email_field = driver.find_element(By.NAME, "auth_key")
            password_field = driver.find_element(By.NAME, "password")
            
            # Clear and fill
            email_field.clear()
            email_field.send_keys(email)
            
            password_field.clear()
            password_field.send_keys(password)
            
            # Take a screenshot before submit
            driver.save_screenshot('error_detection_before_submit.png')
            
            # Try submitting with Enter key first
            logger.info("🔑 Trying to submit with Enter key...")
            password_field.send_keys(Keys.RETURN)
            
            # Wait a moment
            time.sleep(3)
            
            # Check for any error messages
            error_selectors = [
                '.flash-message.flash-alert',
                '.alert-danger',
                '.error-message',
                '.field-error',
                '.invalid-feedback',
                '[role="alert"]',
                '.text-danger',
                '.error'
            ]
            
            for selector in error_selectors:
                try:
                    error_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for error in error_elements:
                        error_text = error.get_attribute('textContent').strip()
                        if error_text:
                            logger.error(f"🚨 Found error message: {error_text}")
                except:
                    continue
            
            # Take screenshot after attempt
            driver.save_screenshot('error_detection_after_enter.png')
            
            # Check current URL
            current_url = driver.current_url
            logger.info(f"📍 URL after Enter key: {current_url}")
            
            # If still on login page, try clicking the button
            if '/login' in current_url:
                logger.info("🖱️ Still on login page, trying button click...")
                
                # Find and click the submit button
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    button_text = button.get_attribute('textContent').strip()
                    if 'Log in' in button_text or 'Sign in' in button_text:
                        logger.info(f"Clicking button: {button_text}")
                        button.click()
                        break
                
                time.sleep(3)
                driver.save_screenshot('error_detection_after_click.png')
                
                # Check URL again
                current_url = driver.current_url
                logger.info(f"📍 URL after button click: {current_url}")
                
                # Check for errors again
                for selector in error_selectors:
                    try:
                        error_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for error in error_elements:
                            error_text = error.get_attribute('textContent').strip()
                            if error_text:
                                logger.error(f"🚨 Found error after click: {error_text}")
                    except:
                        continue
            
            # Save final page content
            with open('error_detection_final.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            
            # Check if we succeeded
            if '/login' not in current_url:
                logger.info("🎉 LOGIN SUCCESSFUL!")
                return True
            else:
                logger.error("❌ LOGIN FAILED - still on login page")
                
                # Try to find any validation messages in the page source
                page_source = driver.page_source.lower()
                error_keywords = ['invalid', 'incorrect', 'wrong', 'error', 'failed', 'denied']
                for keyword in error_keywords:
                    if keyword in page_source:
                        logger.warning(f"⚠️ Found '{keyword}' in page source")
                
                return False
                
        except Exception as e:
            logger.error(f"Error during login attempt: {e}")
            driver.save_screenshot('error_detection_exception.png')
            return False
        
    except Exception as e:
        logger.error(f"Driver setup failed: {e}")
        return False
    
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    logger.info("🔍 Starting error detection...")
    success = detect_login_errors()
    
    if success:
        logger.info("✅ Error detection completed - login successful!")
    else:
        logger.error("❌ Error detection completed - login failed!")
