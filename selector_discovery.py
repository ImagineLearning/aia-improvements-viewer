#!/usr/bin/env python3
"""
CSS Selector Discovery Tool for IL Classroom Errata Pages
Based on analysis of the actual HTML structure
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

def discover_selectors():
    """Discover and test CSS selectors for errata data extraction"""
    
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
            
        logger.info(f"Using credentials: {email}")
            
    except Exception as e:
        logger.error(f"Failed to load credentials: {e}")
        return False
    
    # Load configuration
    try:
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        base_url = config['website']['base_url']
        errata_pages = config['website']['errata_pages']
        
        # Test only Kindergarten first
        test_url = base_url + errata_pages[0]  # Kindergarten
        
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
        
        # Login
        login_url = f"{base_url}/login"
        logger.info(f"🌐 Logging in at: {login_url}")
        driver.get(login_url)
        
        # Wait for Vue.js component
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "sessions-new-feature"))
        )
        time.sleep(3)
        
        # Fill login form
        email_field = driver.find_element(By.NAME, "auth_key")
        password_field = driver.find_element(By.NAME, "password")
        
        email_field.clear()
        email_field.send_keys(email)
        password_field.clear()
        password_field.send_keys(password)
        
        # Submit with Enter key
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)
        
        current_url = driver.current_url
        if "/login" not in current_url and ("welcome" in current_url or "resources" in current_url):
            logger.info(f"✅ Login successful! Current URL: {current_url}")
        else:
            logger.error(f"❌ Login failed! URL: {current_url}")
            return False
        
        # Navigate to Kindergarten errata page
        logger.info(f"📚 Testing Kindergarten errata page: {test_url}")
        driver.get(test_url)
        time.sleep(3)
        
        # First, expand all accordion sections to make content visible
        accordion_buttons = driver.find_elements(By.CSS_SELECTOR, ".section-accordion button")
        logger.info(f"🔍 Found {len(accordion_buttons)} accordion sections to expand")
        
        for i, button in enumerate(accordion_buttons):
            try:
                if button.get_attribute("aria-expanded") == "false":
                    logger.info(f"  Expanding accordion section {i+1}")
                    button.click()
                    time.sleep(1)
            except Exception as e:
                logger.warning(f"  Could not expand accordion {i+1}: {e}")
        
        # Now discover the CSS selectors
        logger.info("\n🔍 DISCOVERING CSS SELECTORS...")
        
        # 1. Unit sections (accordion sections)
        unit_sections = driver.find_elements(By.CSS_SELECTOR, ".section-accordion")
        logger.info(f"📦 Unit sections found: {len(unit_sections)}")
        
        extracted_data = []
        
        for i, section in enumerate(unit_sections):
            try:
                # Get unit name from button text
                button = section.find_element(By.CSS_SELECTOR, "button")
                unit_name = button.text.strip()
                logger.info(f"\n📖 Processing {unit_name}")
                
                # Find tables within this section
                tables = section.find_elements(By.CSS_SELECTOR, "table")
                logger.info(f"  📊 Tables found: {len(tables)}")
                
                for j, table in enumerate(tables):
                    logger.info(f"    🔹 Analyzing table {j+1}")
                    
                    # Get table headers
                    headers = table.find_elements(By.CSS_SELECTOR, "thead th")
                    header_texts = [h.text.strip() for h in headers]
                    logger.info(f"      Headers: {header_texts}")
                    
                    # Get table body rows
                    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
                    logger.info(f"      Data rows: {len(rows)}")
                    
                    for k, row in enumerate(rows):
                        cells = row.find_elements(By.CSS_SELECTOR, "td")
                        cell_texts = [cell.text.strip() for cell in cells]
                        
                        # Skip empty rows
                        if not any(cell_texts) or all(cell == "\u00a0" or cell == "" for cell in cell_texts):
                            continue
                            
                        logger.info(f"        Row {k+1}: {cell_texts}")
                        
                        # Map the data based on expected structure
                        if len(cell_texts) >= 3:
                            data_entry = {
                                'date_extracted': time.strftime('%Y-%m-%d'),
                                'unit': unit_name,
                                'resource': cell_texts[0] if len(cell_texts) > 0 else '',
                                'location': '',  # Could be extracted from resource if needed
                                'instructional_moment': '',  # Not in current structure
                                'page_numbers': '',  # Could be extracted from resource
                                'improvement_description': cell_texts[1] if len(cell_texts) > 1 else '',
                                'improvement_type': 'Correction',  # Default type
                                'date_updated': cell_texts[2] if len(cell_texts) > 2 else ''
                            }
                            extracted_data.append(data_entry)
            
            except Exception as e:
                logger.error(f"  ❌ Error processing section {i+1}: {e}")
        
        # Display results
        logger.info(f"\n📊 EXTRACTION RESULTS:")
        logger.info(f"Total data entries extracted: {len(extracted_data)}")
        
        if extracted_data:
            logger.info("\n🎯 SAMPLE DATA:")
            for i, entry in enumerate(extracted_data[:3]):  # Show first 3 entries
                logger.info(f"Entry {i+1}:")
                for key, value in entry.items():
                    logger.info(f"  {key}: {value}")
                logger.info("")
        
        # Generate optimized CSS selectors
        selectors = {
            'accordion_sections': '.section-accordion',
            'accordion_button': '.section-accordion button',
            'unit_name': '.section-accordion button',  # Extract text from button
            'tables': '.section-accordion table',
            'table_headers': 'thead th',
            'table_rows': 'tbody tr',
            'table_cells': 'td',
            'component_cell': 'tbody tr td:nth-child(1)',
            'improvement_cell': 'tbody tr td:nth-child(2)',
            'date_cell': 'tbody tr td:nth-child(3)'
        }
        
        logger.info("\n🎯 RECOMMENDED CSS SELECTORS:")
        for name, selector in selectors.items():
            logger.info(f"  {name}: {selector}")
        
        # Test selectors
        logger.info("\n🧪 TESTING SELECTORS:")
        
        # Test accordion sections
        test_sections = driver.find_elements(By.CSS_SELECTOR, selectors['accordion_sections'])
        logger.info(f"✅ Accordion sections: {len(test_sections)} found")
        
        # Test tables
        test_tables = driver.find_elements(By.CSS_SELECTOR, selectors['tables'])
        logger.info(f"✅ Tables: {len(test_tables)} found")
        
        # Test component cells
        test_components = driver.find_elements(By.CSS_SELECTOR, selectors['component_cell'])
        logger.info(f"✅ Component cells: {len(test_components)} found")
        
        # Test improvement cells
        test_improvements = driver.find_elements(By.CSS_SELECTOR, selectors['improvement_cell'])
        logger.info(f"✅ Improvement cells: {len(test_improvements)} found")
        
        # Test date cells
        test_dates = driver.find_elements(By.CSS_SELECTOR, selectors['date_cell'])
        logger.info(f"✅ Date cells: {len(test_dates)} found")
        
        # Save updated configuration
        logger.info("\n💾 UPDATING CONFIG FILE...")
        
        # Update the config with discovered selectors
        config['selectors'] = {
            'errata_container': '.section-accordion',
            'unit_section': '.section-accordion',
            'unit_name': '.section-accordion button',
            'accordion_button': '.section-accordion button[aria-expanded="false"]',
            'errata_table': '.section-accordion table',
            'table_rows': 'tbody tr',
            'component_field': 'td:nth-child(1)',
            'improvement_description': 'td:nth-child(2)', 
            'date_updated': 'td:nth-child(3)',
            # These aren't in the current structure but keeping for compatibility
            'unit_field': '',  # Will be extracted from section title
            'resource_field': 'td:nth-child(1)',  # Same as component
            'location_field': '',  # Not present
            'instructional_moment_field': '',  # Not present
            'page_numbers': '',  # Could extract from component text
            'improvement_type': ''  # Will default to 'Correction'
        }
        
        with open('config/config.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info("✅ Configuration updated successfully!")
        
        return extracted_data
        
    except Exception as e:
        logger.error(f"Selector discovery failed: {e}")
        return False
    
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    logger.info("🚀 Starting CSS selector discovery...")
    results = discover_selectors()
    
    if results:
        logger.info(f"✅ Discovery completed successfully! Found {len(results)} data entries")
    else:
        logger.error("❌ Discovery failed!")
