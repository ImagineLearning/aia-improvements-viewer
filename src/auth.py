"""
Authentication module for handling login to the curriculum website.
"""

import os
import time
import logging
import urllib3
from typing import Optional, Dict, Any
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Disable SSL warnings for corporate VPNs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AuthenticationError(Exception):
    """Custom exception for authentication failures."""
    pass


class WebAuthenticator:
    """Handles authentication for the curriculum website."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session: Optional[HTMLSession] = None
        self.driver: Optional[webdriver.Chrome] = None
        
    def setup_selenium_driver(self) -> webdriver.Chrome:
        """Set up Chrome WebDriver with VPN-friendly options (same as working version)."""
        chrome_options = Options()
        
        # EXACT same options as working kindergarten script
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        try:
            # Use system Chrome directly (no WebDriverManager)
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)
            
            return driver
        except Exception as e:
            self.logger.error(f"Failed to create Chrome driver: {e}")
            raise
    
    def login_with_selenium(self, username: str, password: str) -> bool:
        """
        Perform login using Selenium WebDriver (exact working method).
        
        Args:
            username: User's login username  
            password: User's login password
            
        Returns:
            bool: True if login successful, False otherwise
            
        Raises:
            AuthenticationError: If login fails
        """
        try:
            self.driver = self.setup_selenium_driver()
            
            # Navigate to login page
            login_url = self.config['website']['base_url'] + self.config['website']['login_url']
            self.logger.info(f"🌐 Logging in at: {login_url}")
            self.driver.get(login_url)
            
            # Wait for Vue.js component (exact same as working version)
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.presence_of_element_located((By.ID, "sessions-new-feature")))
            time.sleep(3)
            
            # Fill login form with exact same field names as working version
            email_field = self.driver.find_element(By.NAME, "auth_key")
            password_field = self.driver.find_element(By.NAME, "password")
            
            email_field.clear()
            email_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit with Enter key (exact same as working version)
            from selenium.webdriver.common.keys import Keys
            password_field.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Check for success (exact same logic as working version)
            current_url = self.driver.current_url
            if "/login" not in current_url and ("welcome" in current_url or "resources" in current_url):
                self.logger.info(f"✅ Login successful! Current URL: {current_url}")
                return True
            else:
                self.logger.error(f"❌ Login failed! URL: {current_url}")
                return False
                
        except Exception as e:
            self.logger.error(f"Login failed with error: {e}")
            raise AuthenticationError(f"Authentication failed: {e}")
    
    def login_with_requests(self, username: str, password: str) -> bool:
        """
        Perform login using requests-html session with VPN support.
        
        Args:
            username: User's login username
            password: User's login password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            self.session = HTMLSession()
            
            # VPN-friendly session configuration
            self.session.verify = False  # Skip SSL verification for corporate certs
            
            # Configure proxy if available
            proxies = {}
            if os.environ.get('HTTP_PROXY'):
                proxies['http'] = os.environ.get('HTTP_PROXY')
            if os.environ.get('HTTPS_PROXY'):
                proxies['https'] = os.environ.get('HTTPS_PROXY')
            
            if proxies:
                self.session.proxies.update(proxies)
                self.logger.info(f"Using proxies: {proxies}")
            
            # VPN-friendly headers
            self.session.headers.update({
                'User-Agent': self.config['scraping']['user_agent'],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            })
            
            # Get login page
            login_url = self.config['website']['base_url'] + self.config['website']['login_url']
            self.logger.info(f"Getting login page: {login_url}")
            
            response = self.session.get(login_url, timeout=30)
            self.logger.info(f"Login page response: {response.status_code}")
            
            if response.status_code != 200:
                self.logger.error(f"Login page returned status {response.status_code}")
                return False
            
            # Try to render JavaScript (but don't fail if it doesn't work on VPN)
            try:
                response.html.render(timeout=20)
            except Exception as e:
                self.logger.warning(f"Could not render JavaScript (VPN issue): {e}")
                # Continue without JavaScript rendering
            
            # Prepare login data
            login_data = {
                'username': username,
                'password': password,
                'email': username,  # Some sites use email field
            }
            
            # Look for CSRF token if present
            try:
                csrf_token = response.html.find('input[name="csrf_token"]', first=True)
                if csrf_token:
                    login_data['csrf_token'] = csrf_token.attrs.get('value', '')
                
                # Check for other common token names
                for token_name in ['authenticity_token', '_token', 'csrfmiddlewaretoken']:
                    token_elem = response.html.find(f'input[name="{token_name}"]', first=True)
                    if token_elem:
                        login_data[token_name] = token_elem.attrs.get('value', '')
                        break
            except Exception as e:
                self.logger.warning(f"Could not find CSRF token: {e}")
            
            # Submit login form
            self.logger.info("Submitting login form...")
            login_response = self.session.post(
                login_url, 
                data=login_data,
                timeout=30,
                allow_redirects=True
            )
            
            self.logger.info(f"Login response status: {login_response.status_code}")
            self.logger.info(f"Final URL: {login_response.url}")
            
            # Check if login was successful
            success_indicators = [
                self.config['login']['success_indicator'],
                'dashboard', 'main-content', 'logout', 'profile'
            ]
            
            for indicator in success_indicators:
                if indicator in login_response.text.lower():
                    self.logger.info(f"Login successful! Found indicator: {indicator}")
                    return True
            
            # Additional check: if we're redirected away from login page, it might be success
            if 'login' not in login_response.url.lower():
                self.logger.info("Login likely successful (redirected from login page)")
                return True
            
            self.logger.error("Login failed - no success indicators found")
            return False
                
        except Exception as e:
            self.logger.error(f"Login failed with error: {e}")
            return False
    
    def get_authenticated_session(self) -> Optional[HTMLSession]:
        """Get the authenticated requests session."""
        return self.session
    
    def get_authenticated_driver(self) -> Optional[webdriver.Chrome]:
        """Get the authenticated Selenium driver."""
        return self.driver
    
    def logout(self):
        """Clean up and logout."""
        if self.session:
            self.session.close()
            self.session = None
            
        if self.driver:
            self.driver.quit()
            self.driver = None
            
        self.logger.info("Logged out and cleaned up resources")
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        if self.driver:
            try:
                # Check if we can still find the success indicator
                self.driver.find_element(By.CSS_SELECTOR, self.config['login']['success_indicator'])
                return True
            except:
                return False
        return False


def load_credentials() -> tuple[str, str]:
    """
    Load credentials from environment variables.
    
    Returns:
        tuple: (username, password)
        
    Raises:
        ValueError: If credentials are not found
    """
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    
    if not username or not password:
        raise ValueError(
            "Credentials not found. Please set USERNAME and PASSWORD environment variables "
            "or create a .env file with these values."
        )
    
    return username, password
