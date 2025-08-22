"""
URL Discovery Script for ilclassroom.com Errata Pages

This script helps you discover and collect all the errata page URLs 
for grades Kindergarten through Algebra 2.
"""

import sys
import time
import re
from pathlib import Path
from typing import List, Dict

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))


def generate_expected_urls():
    """Generate expected URL patterns based on the sample URLs provided."""
    
    base_url = "https://sdphiladelphia.ilclassroom.com/wikis/"
    
    # Known URL patterns from samples
    known_urls = {
        "Kindergarten": "29245717-kindergarten-errata?path=Wiki.11180076%2FWiki.28930691%2FWiki.9879318%2FWiki.10424770",
        "Grade 1": "18746473-grade-1-errata?path=Wiki.11180076%2FWiki.28930691%2FWiki.9879318%2FWiki.10430165",
        "Grade 6": "20692555-grade-6-errata?path=Wiki.11180076%2FWiki.28930691%2FWiki.10690424%2FWiki.10793887",
        "Algebra 1": "34717795-algebra-1-errata?path=Wiki.11180076%2FWiki.28930691%2FWiki.10563159%2FWiki.10669204",
        "Geometry": "34803461-geometry-errata?path=Wiki.11180076%2FWiki.28930691%2FWiki.10563159%2FWiki.10685998"
    }
    
    # All grades we need to find
    all_grades = [
        "Kindergarten", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5",
        "Grade 6", "Grade 7", "Grade 8", 
        "Algebra 1", "Geometry", "Algebra 2"
    ]
    
    print("=== ilclassroom.com Errata URL Discovery ===\n")
    print("Known URLs from your samples:")
    print("-" * 60)
    
    for grade, url_path in known_urls.items():
        full_url = base_url + url_path
        print(f"{grade:12}: {full_url}")
    
    print(f"\n\nStill need to find URLs for:")
    print("-" * 40)
    
    missing_grades = [grade for grade in all_grades if grade not in known_urls]
    for grade in missing_grades:
        print(f"• {grade}")
    
    print(f"\n\nURL Pattern Analysis:")
    print("-" * 30)
    print("Base URL: https://sdphiladelphia.ilclassroom.com/wikis/")
    print("Pattern:  [ID]-[grade]-errata?path=[encoded-path]")
    print("\nPath patterns observed:")
    print("Elementary (K-5): Wiki.11180076%2FWiki.28930691%2FWiki.9879318%2FWiki.[specific-id]")
    print("Middle (6-8):     Wiki.11180076%2FWiki.28930691%2FWiki.10690424%2FWiki.[specific-id]")
    print("High School:      Wiki.11180076%2FWiki.28930691%2FWiki.10563159%2FWiki.[specific-id]")
    
    return known_urls, missing_grades


def create_url_search_script():
    """Create a script to help systematically search for missing URLs."""
    
    search_script = '''
# URL Search Strategy for Missing Errata Pages

## Method 1: Manual Navigation
1. Log into https://sdphiladelphia.ilclassroom.com
2. Navigate to the main curriculum/errata section
3. Look for grade-level sections
4. Copy URLs for each grade's errata page

## Method 2: URL Pattern Guessing
Based on the patterns observed, try these potential URLs:

### Elementary Grades (2-5)
Look for URLs following this pattern:
https://sdphiladelphia.ilclassroom.com/wikis/[ID]-grade-[X]-errata?path=Wiki.11180076%2FWiki.28930691%2FWiki.9879318%2FWiki.[specific-id]

### Middle School (7-8)  
Look for URLs following this pattern:
https://sdphiladelphia.ilclassroom.com/wikis/[ID]-grade-[X]-errata?path=Wiki.11180076%2FWiki.28930691%2FWiki.10690424%2FWiki.[specific-id]

### High School (Algebra 2)
Look for URLs following this pattern:
https://sdphiladelphia.ilclassroom.com/wikis/[ID]-algebra-2-errata?path=Wiki.11180076%2FWiki.28930691%2FWiki.10563159%2FWiki.[specific-id]

## Method 3: Use the URL Discovery Tool
Run this script with authentication to crawl and discover URLs automatically.
'''
    
    with open("url_search_guide.txt", "w") as f:
        f.write(search_script)
    
    print(f"\n✅ Created 'url_search_guide.txt' with search strategies")


def automated_url_discovery():
    """Attempt to automatically discover errata URLs by crawling the site."""
    
    print("\n=== Automated URL Discovery ===")
    print("This requires authentication and will crawl the site to find errata pages.")
    
    try:
        import yaml
        from dotenv import load_dotenv
        from auth import WebAuthenticator, load_credentials
        
        # Load environment and config
        env_file = Path(__file__).parent / 'config' / '.env'
        if not env_file.exists():
            print("❌ No .env file found. Please set up authentication first.")
            return []
        
        load_dotenv(env_file)
        
        config_path = Path(__file__).parent / 'config' / 'config.yaml'
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        print("🔑 Attempting to authenticate...")
        
        authenticator = WebAuthenticator(config)
        username, password = load_credentials()
        
        # Try to login
        success = authenticator.login_with_selenium(username, password)
        if not success:
            print("❌ Authentication failed. Cannot proceed with automated discovery.")
            return []
        
        print("✅ Authentication successful!")
        
        driver = authenticator.get_authenticated_driver()
        found_urls = []
        
        # Search strategy: look for errata-related links
        print("🔍 Searching for errata pages...")
        
        # Try to find a curriculum or errata navigation page
        search_terms = [
            "errata", "curriculum", "grade", "algebra", "geometry", "kindergarten"
        ]
        
        # Look for links containing these terms
        for term in search_terms:
            try:
                links = driver.find_elements("xpath", f"//a[contains(@href, '{term}') or contains(text(), '{term}')]")
                for link in links[:10]:  # Limit to first 10 to avoid spam
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    if href and 'errata' in href.lower():
                        found_urls.append({
                            'url': href,
                            'text': text,
                            'term': term
                        })
                        print(f"  Found: {text} -> {href}")
            except Exception as e:
                print(f"  Error searching for '{term}': {e}")
        
        authenticator.logout()
        
        if found_urls:
            print(f"\n✅ Found {len(found_urls)} potential errata URLs")
            return found_urls
        else:
            print("❌ No errata URLs found automatically")
            return []
            
    except ImportError:
        print("❌ Required modules not available. Run 'pip install -r requirements.txt' first.")
        return []
    except Exception as e:
        print(f"❌ Error during automated discovery: {e}")
        return []


def update_config_with_urls(urls_dict: Dict[str, str]):
    """Update the config.yaml file with discovered URLs."""
    
    try:
        config_path = Path(__file__).parent / 'config' / 'config.yaml'
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Build the errata_pages section
        errata_pages = []
        for grade, url_path in urls_dict.items():
            if not url_path.startswith('/'):
                # Extract path from full URL
                if 'sdphiladelphia.ilclassroom.com' in url_path:
                    url_path = url_path.split('sdphiladelphia.ilclassroom.com')[-1]
                else:
                    url_path = '/' + url_path
            
            errata_pages.append(f'    - "{url_path}"  # {grade}')
        
        errata_pages_str = '\n'.join(errata_pages)
        
        # Update the config file
        new_content = re.sub(
            r'errata_pages:\s*\n(.*?)(?=\n\s*\n|\n# |$)',
            f'errata_pages:\n{errata_pages_str}',
            content,
            flags=re.DOTALL
        )
        
        with open(config_path, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Updated config.yaml with {len(urls_dict)} URLs")
        
    except Exception as e:
        print(f"❌ Failed to update config: {e}")


def main():
    """Main function for URL discovery."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Discover errata URLs for ilclassroom.com")
    parser.add_argument('--auto', '-a', action='store_true', 
                       help='Attempt automated URL discovery (requires authentication)')
    parser.add_argument('--add-url', nargs=2, metavar=('GRADE', 'URL'),
                       help='Add a specific URL for a grade (e.g., --add-url "Grade 2" "https://...")')
    
    args = parser.parse_args()
    
    if args.add_url:
        grade, url = args.add_url
        print(f"Adding URL for {grade}: {url}")
        
        # For now, just show how to add it manually
        print(f"\nTo add this URL, edit config/config.yaml and add:")
        print(f'    - "{url}"  # {grade}')
        
    elif args.auto:
        automated_url_discovery()
    else:
        known_urls, missing_grades = generate_expected_urls()
        create_url_search_script()
        
        print(f"\n\n🎯 Next Steps:")
        print("1. Use the authentication method to log into the site")
        print("2. Navigate to find the missing grade URLs")
        print("3. Use --add-url to add them: python url_discovery.py --add-url 'Grade 2' 'https://...'")
        print("4. Or run with --auto to attempt automated discovery")


if __name__ == '__main__':
    main()
