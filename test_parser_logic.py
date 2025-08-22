#!/usr/bin/env python3
"""
Test script for parser logic without authentication.
Uses saved HTML content to test parsing.
"""

import sys
import yaml
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from parser import ErrataParser

def test_parser_logic():
    """Test the parser logic with mock HTML content."""
    
    # Load configuration
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    print("🔧 Testing parser logic...")
    
    # Initialize parser
    parser = ErrataParser(config)
    
    # Create mock HTML content that matches the accordion structure
    mock_html = '''
    <div class="content">
        <div class="section-accordion">
            <button aria-expanded="false">Unit 1: Numbers and Counting</button>
            <div class="accordion-content">
                <table>
                    <tbody>
                        <tr>
                            <td>Teacher Edition Glossary, pgs. 346-347</td>
                            <td>Updated definition for "number line" to include more visual examples and clearer language for kindergarten students.</td>
                            <td>2024-01-15</td>
                        </tr>
                        <tr>
                            <td>Student Workbook Unit 1</td>
                            <td>Corrected spelling error on page 12 and added missing number in counting sequence.</td>
                            <td>2024-01-10</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <div class="section-accordion">
            <button aria-expanded="false">Unit 2: Addition and Subtraction</button>
            <div class="accordion-content">
                <table>
                    <tbody>
                        <tr>
                            <td>Teacher Edition, pgs. 89-92</td>
                            <td>Added additional scaffolding examples for students struggling with subtraction concepts.</td>
                            <td>2024-01-20</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    '''
    
    try:
        # Test BeautifulSoup parsing
        print("📄 Testing BeautifulSoup parsing...")
        errata_records = parser.parse_page_with_beautifulsoup(mock_html)
        
        print(f"📊 Extracted {len(errata_records)} records")
        
        # Show all records
        for i, record in enumerate(errata_records):
            print(f"\n🔍 Record {i+1}:")
            print(f"  Unit: '{record['Unit']}'")
            print(f"  Resource: '{record['Resource']}'")
            print(f"  Location: '{record['Location']}'")
            print(f"  Page Numbers: '{record['Page_Numbers']}'")
            print(f"  Improvement: '{record['Improvement_Description'][:100]}...'")
            print(f"  Date: '{record['Date_Updated']}'")
        
        # Test component text parsing
        print("\n🧪 Testing component text parsing...")
        test_components = [
            "Teacher Edition Glossary, pgs. 346-347",
            "Student Workbook Unit 1",
            "Teacher Edition, pgs. 89-92",
            "Answer Key Section 2, pages 15-20",
            "Student Guide Chapter 3"
        ]
        
        for component in test_components:
            resource, location, pages = parser._parse_component_text(component)
            print(f"  '{component}' -> Resource: '{resource}', Location: '{location}', Pages: '{pages}'")
        
        print("\n✅ Parser logic test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parser_logic()
