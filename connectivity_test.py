"""
Connectivity and Login URL Tester for ilclassroom.com

This script helps diagnose connection and login issues.
"""

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time


def test_basic_connectivity():
    """Test basic connectivity to the site."""
    print("=== Testing Basic Connectivity ===")
    
    base_urls = [
        "https://sdphiladelphia.ilclassroom.com",
        "https://sdphiladelphia.ilclassroom.com/",
        "http://sdphiladelphia.ilclassroom.com",  # Try HTTP
    ]
    
    for url in base_urls:
        try:
            print(f"Testing {url}...")
            response = requests.get(url, timeout=10)
            print(f"  ✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ Connected successfully!")
                return url
            
        except requests.exceptions.ConnectTimeout:
            print(f"  ❌ Connection timeout")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection error (DNS/network issue)")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return None


def find_login_page():
    """Try to find the correct login page."""
    print("\n=== Finding Login Page ===")
    
    # Get working base URL
    base_url = test_basic_connectivity()
    if not base_url:
        print("❌ Cannot connect to base site. Check network connection.")
        return None
    
    # Common login paths for educational platforms
    login_paths = [
        "/users/sign_in",
        "/login",
        "/signin",
        "/sign_in",
        "/auth/login",
        "/account/login",
        "/user/login",
    ]
    
    working_login_url = None
    
    for path in login_paths:
        try:
            url = base_url.rstrip('/') + path
            print(f"Testing {url}...")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Check if it looks like a login page
                content = response.text.lower()
                login_indicators = ['password', 'email', 'username', 'sign in', 'login']
                
                if any(indicator in content for indicator in login_indicators):
                    print(f"  ✅ Found login page!")
                    working_login_url = url
                    break
                else:
                    print(f"  ⚠️  Page exists but doesn't look like login")
            else:
                print(f"  ❌ Status: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return working_login_url


def test_login_with_selenium(login_url):
    """Test login using Selenium to see the actual page."""
    print(f"\n=== Testing Login Page with Selenium ===")
    
    try:
        # Set up Chrome driver
        chrome_options = Options()
        # Remove headless mode so we can see what's happening
        # chrome_options.add_argument("--headless")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"Navigating to: {login_url}")
        driver.get(login_url)
        
        # Wait for page to load
        time.sleep(3)
        
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Look for form fields
        print("\nLooking for login form fields...")
        
        # Try different selectors for email/username field
        email_selectors = [
            "#user_email", "#email", "#username", 
            "input[name='user[email]']", "input[name='email']", "input[name='username']",
            "input[type='email']", "input[placeholder*='email']", "input[placeholder*='username']"
        ]
        
        password_selectors = [
            "#user_password", "#password", 
            "input[name='user[password]']", "input[name='password']",
            "input[type='password']"
        ]
        
        submit_selectors = [
            "input[type='submit']", "button[type='submit']", 
            ".btn-primary", ".submit-btn", "button:contains('Sign')", "input[value*='Sign']"
        ]
        
        found_fields = {}
        
        for selector in email_selectors:
            try:
                element = driver.find_element("css selector", selector)
                print(f"  ✅ Found email field: {selector}")
                found_fields['email'] = selector
                break
            except:
                continue
        
        for selector in password_selectors:
            try:
                element = driver.find_element("css selector", selector)
                print(f"  ✅ Found password field: {selector}")
                found_fields['password'] = selector
                break
            except:
                continue
        
        for selector in submit_selectors:
            try:
                element = driver.find_element("css selector", selector)
                print(f"  ✅ Found submit button: {selector}")
                found_fields['submit'] = selector
                break
            except:
                continue
        
        if len(found_fields) >= 2:
            print(f"\n✅ Found login form with {len(found_fields)} fields!")
            print("Suggested selectors for config.yaml:")
            print("login:")
            if 'email' in found_fields:
                print(f'  username_field: "{found_fields["email"]}"')
            if 'password' in found_fields:
                print(f'  password_field: "{found_fields["password"]}"')
            if 'submit' in found_fields:
                print(f'  submit_button: "{found_fields["submit"]}"')
        else:
            print("❌ Could not find complete login form")
        
        # Keep browser open for manual inspection
        print(f"\n🔍 Browser is open for manual inspection.")
        print("Check the page and press Enter to continue...")
        input()
        
        driver.quit()
        
        return found_fields
        
    except Exception as e:
        print(f"❌ Selenium test failed: {e}")
        return {}


def main():
    """Main diagnostic function."""
    print("🔧 ilclassroom.com Connectivity & Login Diagnostics")
    print("=" * 55)
    
    # Test basic connectivity
    base_url = test_basic_connectivity()
    
    if not base_url:
        print("\n❌ Cannot connect to the site. Please check:")
        print("1. Your internet connection")
        print("2. The URL spelling: sdphiladelphia.ilclassroom.com")
        print("3. VPN or firewall settings")
        return
    
    # Find login page
    login_url = find_login_page()
    
    if not login_url:
        print("\n❌ Could not find login page. The site structure may be different.")
        print("Try manually navigating to the site and finding the login page.")
        return
    
    # Test with Selenium
    login_fields = test_login_with_selenium(login_url)
    
    if login_fields:
        print(f"\n✅ Diagnostics complete!")
        print(f"Working login URL: {login_url}")
        print("Update your config/config.yaml with the found selectors.")
    else:
        print(f"\n⚠️  Could not fully analyze login form.")
        print("You may need to manually inspect the page source.")


if __name__ == '__main__':
    main()
