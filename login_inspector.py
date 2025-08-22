"""
Manual Login Form Inspector

This script helps you manually inspect the login form to find the correct
form action URL and field names.
"""

import requests
import urllib3
from bs4 import BeautifulSoup

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def inspect_login_page():
    """Manually inspect the login page to understand its structure."""
    
    login_url = "http://sdphiladelphia.ilclassroom.com/login"
    
    print("🔍 Inspecting Login Page")
    print("=" * 30)
    print(f"URL: {login_url}")
    
    try:
        # Create a session with VPN-friendly settings
        session = requests.Session()
        session.verify = False
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Get the login page
        response = session.get(login_url, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"\n📋 Page Analysis")
            print("-" * 20)
            print(f"Title: {soup.title.string if soup.title else 'No title'}")
            
            # Find all forms
            forms = soup.find_all('form')
            print(f"Forms found: {len(forms)}")
            
            for i, form in enumerate(forms):
                print(f"\n🔍 Form {i+1}:")
                print(f"  Action: {form.get('action', 'Not specified')}")
                print(f"  Method: {form.get('method', 'GET')}")
                
                # Find input fields
                inputs = form.find_all('input')
                print(f"  Input fields ({len(inputs)}):")
                
                for inp in inputs:
                    input_type = inp.get('type', 'text')
                    input_name = inp.get('name', 'No name')
                    input_id = inp.get('id', 'No id')
                    input_placeholder = inp.get('placeholder', '')
                    
                    print(f"    - Type: {input_type}, Name: {input_name}, ID: {input_id}")
                    if input_placeholder:
                        print(f"      Placeholder: {input_placeholder}")
            
            # Look for specific login-related elements
            print(f"\n🔍 Login Element Analysis:")
            
            # Email/username fields
            email_fields = soup.find_all('input', {'type': 'email'})
            text_fields = soup.find_all('input', {'type': 'text'})
            username_fields = soup.find_all('input', attrs={'name': lambda x: x and 'user' in x.lower()})
            
            print(f"  Email fields: {len(email_fields)}")
            print(f"  Text fields: {len(text_fields)}")
            print(f"  Username-like fields: {len(username_fields)}")
            
            # Password fields
            password_fields = soup.find_all('input', {'type': 'password'})
            print(f"  Password fields: {len(password_fields)}")
            
            # Submit buttons
            submit_buttons = soup.find_all('input', {'type': 'submit'})
            button_tags = soup.find_all('button')
            print(f"  Submit inputs: {len(submit_buttons)}")
            print(f"  Button tags: {len(button_tags)}")
            
            # Look for tokens
            hidden_fields = soup.find_all('input', {'type': 'hidden'})
            print(f"  Hidden fields: {len(hidden_fields)}")
            
            for hidden in hidden_fields:
                name = hidden.get('name', '')
                if any(token in name.lower() for token in ['token', 'csrf', 'auth']):
                    print(f"    Token field: {name} = {hidden.get('value', '')[:20]}...")
            
            # Save the HTML for manual inspection
            with open('login_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"\n💾 Saved login page HTML to 'login_page.html' for manual inspection")
            
            # Generate suggested configuration
            print(f"\n📝 Suggested Configuration Updates:")
            print("-" * 35)
            
            if forms:
                main_form = forms[0]  # Assume first form is login form
                action = main_form.get('action', '')
                
                if action:
                    print(f"If form action is relative: '{action}'")
                    if action.startswith('/'):
                        print(f"  Try updating login_url in config to: \"{action}\"")
                    else:
                        print(f"  Try updating login_url in config to: \"/{action}\"")
                
                # Look for field names
                email_field = main_form.find('input', {'type': 'email'}) or main_form.find('input', attrs={'name': lambda x: x and 'email' in x.lower()})
                password_field = main_form.find('input', {'type': 'password'})
                submit_button = main_form.find('input', {'type': 'submit'}) or main_form.find('button')
                
                print("\nSuggested login selectors:")
                if email_field:
                    if email_field.get('id'):
                        print(f"  username_field: \"#{email_field['id']}\"")
                    elif email_field.get('name'):
                        print(f"  username_field: \"input[name='{email_field['name']}']\"")
                
                if password_field:
                    if password_field.get('id'):
                        print(f"  password_field: \"#{password_field['id']}\"")
                    elif password_field.get('name'):
                        print(f"  password_field: \"input[name='{password_field['name']}']\"")
                
                if submit_button:
                    if submit_button.get('id'):
                        print(f"  submit_button: \"#{submit_button['id']}\"")
                    elif submit_button.name == 'input':
                        print(f"  submit_button: \"input[type='submit']\"")
                    else:
                        print(f"  submit_button: \"button[type='submit']\"")
        
        else:
            print(f"❌ Failed to get login page. Status: {response.status_code}")
            print(f"Response text (first 500 chars):\n{response.text[:500]}")
    
    except Exception as e:
        print(f"❌ Error inspecting login page: {e}")


def test_form_submission():
    """Test different form submission approaches."""
    
    print(f"\n🧪 Testing Form Submission Methods")
    print("=" * 35)
    
    base_url = "http://sdphiladelphia.ilclassroom.com"
    
    # Different endpoints to try
    endpoints = [
        "/login",
        "/users/sign_in", 
        "/session",
        "/auth/login",
        "/authenticate"
    ]
    
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    test_data = {
        'email': 'test@example.com',
        'password': 'testpassword',
        'username': 'test@example.com',
        'user[email]': 'test@example.com',
        'user[password]': 'testpassword'
    }
    
    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\nTesting POST to: {url}")
        
        try:
            response = session.post(url, data=test_data, timeout=10, allow_redirects=False)
            print(f"  Status: {response.status_code}")
            
            if response.status_code in [302, 301]:
                print(f"  Redirect to: {response.headers.get('Location', 'Unknown')}")
            elif response.status_code == 200:
                print(f"  Response length: {len(response.text)}")
            elif response.status_code == 404:
                print(f"  ❌ Not found")
            else:
                print(f"  Other response")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")


if __name__ == '__main__':
    inspect_login_page()
    test_form_submission()
    
    print(f"\n🎯 Next Steps:")
    print("1. Open 'login_page.html' in a browser to manually inspect the form")
    print("2. Update the config.yaml with the correct field selectors")
    print("3. Update the login_url if the form action is different")
    print("4. Test again with the corrected configuration")
