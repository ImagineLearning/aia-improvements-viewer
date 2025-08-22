"""
Configuration helper script for setting up CSS selectors.

This script helps you test and validate CSS selectors for your curriculum website.
Run this after configuring your credentials to test selectors interactively.
"""

import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from auth import WebAuthenticator, load_credentials


def load_config():
    """Load configuration from YAML file."""
    config_path = Path(__file__).parent / 'config' / 'config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def test_selectors_interactive():
    """Interactive selector testing."""
    print("=== Errata Locator - Selector Configuration Helper ===\n")
    
    # Load environment variables
    env_file = Path(__file__).parent / 'config' / '.env'
    if env_file.exists():
        load_dotenv(env_file)
    else:
        print("❌ No .env file found. Please create one with your credentials.")
        return
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return
    
    print("1. Testing authentication...")
    try:
        authenticator = WebAuthenticator(config)
        username, password = load_credentials()
        
        # Test login
        success = authenticator.login_with_selenium(username, password)
        if not success:
            print("❌ Authentication failed. Check your credentials and website configuration.")
            return
        
        print("✅ Authentication successful!")
        
        # Get the driver for testing
        driver = authenticator.get_authenticated_driver()
        
        # Navigate to first errata page
        if config['website']['errata_pages']:
            test_url = config['website']['base_url'] + config['website']['errata_pages'][0]
            print(f"\n2. Navigating to test page: {test_url}")
            driver.get(test_url)
            print(f"✅ Page loaded: {driver.title}")
            
            print("\n3. Testing CSS selectors...")
            selectors = config['selectors']
            
            # Test each selector
            for field_name, selector in selectors.items():
                print(f"\nTesting selector for '{field_name}': {selector}")
                
                try:
                    elements = driver.find_elements("css selector", selector)
                    count = len(elements)
                    
                    if count > 0:
                        print(f"  ✅ Found {count} element(s)")
                        
                        # Show first few examples
                        for i, element in enumerate(elements[:3]):
                            text = element.text.strip()[:100]  # First 100 chars
                            print(f"    Example {i+1}: '{text}{'...' if len(element.text) > 100 else ''}'")
                    else:
                        print(f"  ❌ No elements found - check this selector")
                        
                except Exception as e:
                    print(f"  ❌ Error testing selector: {e}")
            
            print(f"\n4. Page HTML structure analysis...")
            print("=" * 50)
            
            # Find potential errata containers
            common_selectors = [
                ".errata", ".erratum", ".correction", ".update", ".change",
                ".item", ".entry", ".record", ".row",
                "[class*='errata']", "[class*='correction']", "[class*='update']"
            ]
            
            print("Looking for potential errata containers:")
            for selector in common_selectors:
                try:
                    elements = driver.find_elements("css selector", selector)
                    if elements:
                        print(f"  Found {len(elements)} elements with selector: {selector}")
                except:
                    pass
            
            # Interactive mode
            print(f"\n5. Interactive selector testing")
            print("Enter CSS selectors to test them live, or 'quit' to exit:")
            
            while True:
                try:
                    user_selector = input("\nCSS Selector > ").strip()
                    
                    if user_selector.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    if not user_selector:
                        continue
                    
                    elements = driver.find_elements("css selector", user_selector)
                    count = len(elements)
                    
                    if count > 0:
                        print(f"Found {count} element(s):")
                        for i, element in enumerate(elements[:5]):  # Show first 5
                            text = element.text.strip()[:150]
                            print(f"  {i+1}. '{text}{'...' if len(element.text) > 150 else ''}'")
                        
                        if count > 5:
                            print(f"  ... and {count - 5} more")
                    else:
                        print("No elements found with that selector")
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error: {e}")
        
        # Cleanup
        authenticator.logout()
        print("\n✅ Testing completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")


def generate_selector_template():
    """Generate a template for common errata page patterns."""
    print("\n=== Common Selector Patterns ===")
    print("Copy and modify these in your config.yaml file:\n")
    
    patterns = {
        "Table-based errata": {
            "errata_container": "table.errata-table tr",
            "unit_field": "td:nth-child(1)",
            "resource_field": "td:nth-child(2)",
            "location_field": "td:nth-child(3)",
            "page_numbers": "td:nth-child(4)",
            "improvement_description": "td:nth-child(5)"
        },
        "List-based errata": {
            "errata_container": ".errata-list .errata-item",
            "unit_field": ".unit",
            "resource_field": ".resource",
            "location_field": ".location",
            "page_numbers": ".pages",
            "improvement_description": ".description"
        },
        "Card-based errata": {
            "errata_container": ".errata-cards .card",
            "unit_field": ".card-header .unit",
            "resource_field": ".card-body .resource",
            "location_field": ".card-body .location",
            "page_numbers": ".card-footer .pages",
            "improvement_description": ".card-body .description"
        }
    }
    
    for pattern_name, selectors in patterns.items():
        print(f"{pattern_name}:")
        print("selectors:")
        for field, selector in selectors.items():
            print(f'  {field}: "{selector}"')
        print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Errata Locator Configuration Helper")
    parser.add_argument('--templates', '-t', action='store_true', 
                       help='Show selector templates for common patterns')
    
    args = parser.parse_args()
    
    if args.templates:
        generate_selector_template()
    else:
        test_selectors_interactive()
