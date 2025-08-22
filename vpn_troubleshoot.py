"""
VPN-Friendly Web Scraping Configuration and Troubleshooting

This script provides VPN-compatible configurations and alternative approaches
for scraping when behind corporate firewalls/VPNs.
"""

import requests
import os
from pathlib import Path


def test_vpn_connectivity():
    """Test connectivity through corporate VPN."""
    print("=== VPN Connectivity Diagnostics ===\n")
    
    # Test basic internet connectivity
    test_sites = [
        "http://httpbin.org/get",  # Simple HTTP test
        "https://httpbin.org/get", # HTTPS test
        "http://sdphiladelphia.ilclassroom.com",  # Target site
    ]
    
    # Common proxy settings to try
    proxy_configs = [
        None,  # No proxy
        {
            'http': os.environ.get('HTTP_PROXY', ''),
            'https': os.environ.get('HTTPS_PROXY', '')
        } if os.environ.get('HTTP_PROXY') else None,
        # Add common corporate proxy patterns
        {'http': 'http://proxy.company.com:8080', 'https': 'http://proxy.company.com:8080'},
    ]
    
    for i, site in enumerate(test_sites):
        print(f"{i+1}. Testing {site}")
        
        for j, proxy in enumerate(proxy_configs):
            if proxy and not any(proxy.values()):
                continue
                
            try:
                proxy_desc = f"proxy {proxy}" if proxy else "no proxy"
                print(f"   Trying with {proxy_desc}...")
                
                response = requests.get(
                    site, 
                    proxies=proxy,
                    timeout=10,
                    verify=False  # Skip SSL verification for corporate certs
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Success with {proxy_desc}")
                    return proxy
                else:
                    print(f"   ⚠️  Status {response.status_code} with {proxy_desc}")
                    
            except requests.exceptions.ProxyError:
                print(f"   ❌ Proxy error")
            except requests.exceptions.SSLError:
                print(f"   ❌ SSL certificate error")
            except requests.exceptions.ConnectTimeout:
                print(f"   ❌ Connection timeout")
            except requests.exceptions.ConnectionError as e:
                print(f"   ❌ Connection error: {str(e)[:100]}...")
            except Exception as e:
                print(f"   ❌ Other error: {str(e)[:100]}...")
        
        print()
    
    return None


def create_vpn_friendly_config():
    """Create VPN-friendly configuration updates."""
    
    config_updates = {
        'requests_config': '''
# Add these to your Python script for VPN compatibility:

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Disable SSL warnings for corporate certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create a session with retry strategy
session = requests.Session()

# Retry strategy
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"]
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# VPN-friendly headers
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
})
''',
        
        'selenium_config': '''
# VPN-friendly Selenium configuration:

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()

# VPN-friendly options
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--allow-running-insecure-content")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
chrome_options.add_argument("--ignore-certificate-errors-spki-list")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")

# Corporate proxy settings (if needed)
# chrome_options.add_argument("--proxy-server=http://proxy.company.com:8080")

# Disable images and CSS for faster loading
chrome_options.add_experimental_option("prefs", {
    "profile.managed_default_content_settings.images": 2,
    "profile.default_content_setting_values.notifications": 2
})
''',
        
        'environment_variables': '''
# Environment variables to set for VPN/proxy support:

# If your company uses a proxy, set these:
set HTTP_PROXY=http://proxy.company.com:8080
set HTTPS_PROXY=http://proxy.company.com:8080
set NO_PROXY=localhost,127.0.0.1,.company.com

# Alternative format:
$env:HTTP_PROXY="http://proxy.company.com:8080"
$env:HTTPS_PROXY="http://proxy.company.com:8080"
$env:NO_PROXY="localhost,127.0.0.1,.company.com"
'''
    }
    
    return config_updates


def create_vpn_compatible_auth():
    """Create a VPN-compatible authentication module."""
    
    auth_code = '''"""
VPN-Compatible Authentication Module
"""

import requests
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
import time

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class VPNCompatibleAuthenticator:
    """VPN-friendly authentication."""
    
    def __init__(self, config):
        self.config = config
        self.session = None
        self.driver = None
    
    def create_vpn_session(self):
        """Create a VPN-compatible requests session."""
        session = requests.Session()
        
        # Get proxy settings from environment
        proxies = {}
        if os.environ.get('HTTP_PROXY'):
            proxies['http'] = os.environ.get('HTTP_PROXY')
        if os.environ.get('HTTPS_PROXY'):
            proxies['https'] = os.environ.get('HTTPS_PROXY')
        
        if proxies:
            session.proxies.update(proxies)
        
        # VPN-friendly settings
        session.verify = False  # Skip SSL verification
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        
        return session
    
    def create_vpn_driver(self):
        """Create a VPN-compatible Selenium driver."""
        chrome_options = Options()
        
        # VPN-friendly options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        # Corporate proxy (uncomment and modify if needed)
        # proxy = os.environ.get('HTTP_PROXY')
        # if proxy:
        #     chrome_options.add_argument(f"--proxy-server={proxy}")
        
        # Performance optimizations
        chrome_options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        })
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            return driver
        except Exception as e:
            print(f"Failed to create Chrome driver: {e}")
            return None
    
    def test_requests_login(self, username, password):
        """Test login using requests session."""
        try:
            session = self.create_vpn_session()
            login_url = self.config['website']['base_url'] + self.config['website']['login_url']
            
            print(f"Testing requests login to: {login_url}")
            
            # Get login page
            response = session.get(login_url, timeout=30)
            print(f"Login page status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Successfully reached login page with requests")
                return True
            else:
                print(f"❌ Login page returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Requests login test failed: {e}")
            return False
    
    def test_selenium_login(self, username, password):
        """Test login using Selenium."""
        try:
            driver = self.create_vpn_driver()
            if not driver:
                return False
            
            login_url = self.config['website']['base_url'] + self.config['website']['login_url']
            print(f"Testing Selenium login to: {login_url}")
            
            driver.get(login_url)
            time.sleep(3)
            
            print(f"Page title: {driver.title}")
            print(f"Current URL: {driver.current_url}")
            print("✅ Successfully reached login page with Selenium")
            
            driver.quit()
            return True
            
        except Exception as e:
            print(f"❌ Selenium login test failed: {e}")
            return False
'''
    
    return auth_code


def main():
    """Main VPN diagnostics and setup."""
    print("🔧 VPN-Friendly Errata Locator Setup")
    print("=" * 40)
    
    # Test VPN connectivity
    working_proxy = test_vpn_connectivity()
    
    print("\n" + "=" * 40)
    print("📋 VPN Configuration Recommendations")
    print("=" * 40)
    
    if working_proxy:
        print(f"✅ Found working proxy configuration: {working_proxy}")
    else:
        print("⚠️  No proxy configuration worked, trying direct connection")
    
    # Create configuration files
    configs = create_vpn_friendly_config()
    
    # Save configurations to files
    output_dir = Path("vpn_configs")
    output_dir.mkdir(exist_ok=True)
    
    for name, content in configs.items():
        file_path = output_dir / f"{name}.txt"
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"📁 Created: {file_path}")
    
    # Create VPN-compatible auth module
    auth_code = create_vpn_compatible_auth()
    with open(output_dir / "vpn_auth.py", 'w') as f:
        f.write(auth_code)
    print(f"📁 Created: {output_dir / 'vpn_auth.py'}")
    
    print(f"\n🎯 Next Steps for VPN Setup:")
    print("1. Check if your company provides proxy settings")
    print("2. Ask IT for the corporate proxy server details")
    print("3. Set environment variables if needed:")
    print("   $env:HTTP_PROXY='http://proxy.company.com:8080'")
    print("4. Try the alternative authentication methods")
    print("5. Consider using requests-only mode (--use-requests)")
    
    print(f"\n💡 Alternative Approaches:")
    print("- Run the script from a personal device (if allowed)")
    print("- Use VPN split-tunneling if available")
    print("- Ask IT to whitelist ilclassroom.com")
    print("- Export data manually and use CSV processing only")


if __name__ == '__main__':
    main()
