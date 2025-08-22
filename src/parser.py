"""
HTML parser module for extracting errata data from web pages.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class ErrataParser:
    """Handles parsing of HTML content to extract errata information."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.selectors = config['selectors']
    
    def parse_page_with_selenium(self, driver) -> List[Dict[str, Any]]:
        """
        Parse errata data from a page using Selenium WebDriver.
        Handles accordion-based structure where each section contains a table.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            List[Dict[str, Any]]: List of extracted errata records
        """
        errata_list = []
        
        try:
            # Extract grade level from page title or URL
            grade_level = self._extract_grade_level(driver)
            
            # Find all accordion sections
            accordion_sections = driver.find_elements(By.CSS_SELECTOR, self.selectors['errata_container'])
            
            self.logger.info(f"Found {len(accordion_sections)} accordion sections")
            
            for section in accordion_sections:
                # Extract unit name from the button
                unit_name = self._extract_unit_name(section)
                
                # Expand the accordion if it's collapsed
                self._expand_accordion_section(section, driver)
                
                # Extract data from the table in this section
                table_data = self._extract_table_data(section, unit_name, grade_level)
                
                if table_data:
                    errata_list.extend(table_data)
            
            self.logger.info(f"Successfully extracted {len(errata_list)} errata records")
            return errata_list
            
        except Exception as e:
            self.logger.error(f"Failed to parse page with Selenium: {e}")
            return []
    
    def parse_page_with_beautifulsoup(self, html_content: str, page_url: str = "", page_title: str = "") -> List[Dict[str, Any]]:
        """
        Parse errata data from HTML content using BeautifulSoup.
        Handles accordion-based structure where each section contains a table.
        
        Args:
            html_content: Raw HTML content as string
            page_url: URL of the page (for grade level extraction)
            page_title: Title of the page (for grade level extraction)
            
        Returns:
            List[Dict[str, Any]]: List of extracted errata records
        """
        errata_list = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract grade level from title or URL
            grade_level = self._extract_grade_level_from_strings(page_title, page_url)
            
            # Find all accordion sections
            accordion_sections = soup.select(self.selectors['errata_container'])
            
            self.logger.info(f"Found {len(accordion_sections)} accordion sections")
            
            for section in accordion_sections:
                # Extract unit name from the button
                unit_name = self._extract_unit_name_soup(section)
                
                # Extract data from the table in this section
                table_data = self._extract_table_data_soup(section, unit_name, grade_level)
                
                if table_data:
                    errata_list.extend(table_data)
            
            self.logger.info(f"Successfully extracted {len(errata_list)} errata records")
            return errata_list
            
        except Exception as e:
            self.logger.error(f"Failed to parse page with BeautifulSoup: {e}")
            return []
    
    def _extract_grade_level(self, driver) -> str:
        """
        Extract grade level from page title or URL.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            str: Grade level (e.g., "Kindergarten", "Grade 1", "Algebra 1")
        """
        try:
            # First try to extract from page title
            page_title = driver.title
            
            # Common grade level patterns
            grade_patterns = [
                r'kindergarten',
                r'grade\s*(\d+)',
                r'algebra\s*(\d+)',
                r'geometry',
                r'pre-algebra',
                r'calculus'
            ]
            
            import re
            for pattern in grade_patterns:
                match = re.search(pattern, page_title, re.IGNORECASE)
                if match:
                    if 'kindergarten' in pattern:
                        return 'Kindergarten'
                    elif 'grade' in pattern:
                        return f'Grade {match.group(1)}'
                    elif 'algebra' in pattern:
                        return f'Algebra {match.group(1)}'
                    elif 'geometry' in pattern:
                        return 'Geometry'
                    elif 'pre-algebra' in pattern:
                        return 'Pre-Algebra'
                    elif 'calculus' in pattern:
                        return 'Calculus'
            
            # Fallback: try to extract from URL
            current_url = driver.current_url
            
            url_patterns = [
                (r'kindergarten', 'Kindergarten'),
                (r'grade-(\d+)', 'Grade {}'),
                (r'algebra-(\d+)', 'Algebra {}'),
                (r'geometry', 'Geometry'),
                (r'pre-algebra', 'Pre-Algebra'),
                (r'calculus', 'Calculus')
            ]
            
            for pattern, format_str in url_patterns:
                match = re.search(pattern, current_url, re.IGNORECASE)
                if match:
                    if '{}' in format_str:
                        return format_str.format(match.group(1))
                    else:
                        return format_str
            
            # If no pattern matches, try to extract any grade-related text from title
            title_words = page_title.lower().split()
            for word in title_words:
                if any(grade_word in word for grade_word in ['kindergarten', 'grade', 'algebra', 'geometry']):
                    return page_title.split('|')[0].strip()  # Return first part of title
            
            return "Unknown Grade"
            
        except Exception as e:
            self.logger.warning(f"Could not extract grade level: {e}")
            return "Unknown Grade"

    def _extract_unit_name(self, section) -> str:
        """
        Extract unit name from accordion section button.
        
        Args:
            section: Selenium element for accordion section
            
        Returns:
            str: Unit name or empty string if not found
        """
        try:
            button = section.find_element(By.CSS_SELECTOR, "button")
            unit_name = button.text.strip()
            self.logger.debug(f"Extracted unit name: {unit_name}")
            return unit_name
        except Exception as e:
            self.logger.warning(f"Could not extract unit name: {e}")
            return ""
    
    def _expand_accordion_section(self, section, driver):
        """
        Expand accordion section if it's collapsed.
        
        Args:
            section: Selenium element for accordion section
            driver: Selenium WebDriver instance
        """
        try:
            button = section.find_element(By.CSS_SELECTOR, "button")
            aria_expanded = button.get_attribute("aria-expanded")
            
            if aria_expanded == "false":
                self.logger.debug("Expanding collapsed accordion section")
                driver.execute_script("arguments[0].click();", button)
                # Small delay to let the accordion expand
                import time
                time.sleep(0.5)
        except Exception as e:
            self.logger.warning(f"Could not expand accordion section: {e}")
    
    def _extract_table_data(self, section, unit_name: str, grade_level: str) -> List[Dict[str, Any]]:
        """
        Extract data from table within an accordion section.
        
        Args:
            section: Selenium element for accordion section
            unit_name: Name of the unit/section
            grade_level: Grade level for this page
            
        Returns:
            List[Dict[str, Any]]: List of errata records from this section
        """
        records = []
        
        try:
            # Find table rows in this section
            rows = section.find_elements(By.CSS_SELECTOR, self.selectors['table_rows'])
            
            self.logger.debug(f"Found {len(rows)} table rows in section '{unit_name}'")
            
            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) >= 3:
                        # Extract data based on discovered structure:
                        # Column 1: Component (Resource/Location)
                        # Column 2: Improvement Description  
                        # Column 3: Date Updated
                        
                        component_text = cells[0].text.strip()
                        improvement_text = cells[1].text.strip()
                        date_text = cells[2].text.strip()
                        
                        # Parse component text to extract Resource and Location
                        resource, location, page_numbers = self._parse_component_text(component_text)
                        
                        errata_record = {
                            'Date_Extracted': datetime.now().strftime('%Y-%m-%d'),
                            'Grade_Level': grade_level,
                            'Unit': unit_name,
                            'Resource': resource,
                            'Location': location,
                            'Instructional_Moment': '',  # Not available in current structure
                            'Page_Numbers': page_numbers,
                            'Improvement_Description': improvement_text,
                            'Improvement_Type': '',  # Would need to be inferred from description
                            'Date_Updated': self._normalize_date(date_text)
                        }
                        
                        # Clean the record
                        errata_record = self._clean_errata_data(errata_record)
                        
                        if self._is_valid_errata_record(errata_record):
                            records.append(errata_record)
                            
                except Exception as e:
                    self.logger.warning(f"Failed to extract row data: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed to extract table data from section '{unit_name}': {e}")
        
        return records
    
    def _parse_component_text(self, component_text: str) -> tuple:
        """
        Parse component text to extract Resource, Location, and Page Numbers.
        
        Examples:
        - "Teacher Edition Glossary, pgs. 346-347" -> ("Teacher Edition Glossary", "", "346-347")
        - "Student Edition Unit 2" -> ("Student Edition", "Unit 2", "")
        
        Args:
            component_text: Raw component text from table
            
        Returns:
            tuple: (resource, location, page_numbers)
        """
        if not component_text:
            return "", "", ""
        
        # Extract page numbers first
        page_numbers = ""
        page_match = re.search(r'(?:pgs?\.?\s*|pages?\s*)(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)', component_text, re.IGNORECASE)
        if page_match:
            page_numbers = page_match.group(1)
            # Remove page info from component text
            component_text = re.sub(r',?\s*(?:pgs?\.?\s*|pages?\s*)\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*', '', component_text, flags=re.IGNORECASE).strip()
        
        # Try to identify common resource types
        resource_patterns = [
            r'(Teacher Edition.*?)(?:,|$)',
            r'(Student Edition.*?)(?:,|$)',
            r'(Teacher Guide.*?)(?:,|$)',
            r'(Student Guide.*?)(?:,|$)',
            r'(Glossary.*?)(?:,|$)',
            r'(Answer Key.*?)(?:,|$)',
        ]
        
        resource = ""
        location = ""
        
        for pattern in resource_patterns:
            match = re.search(pattern, component_text, re.IGNORECASE)
            if match:
                resource = match.group(1).strip()
                # Remove the resource part to get location
                remaining_text = component_text.replace(match.group(0), '').strip().strip(',').strip()
                if remaining_text:
                    location = remaining_text
                break
        
        # If no specific resource pattern matched, use the whole text as resource
        if not resource:
            resource = component_text
        
        return resource, location, page_numbers
    
    def _extract_grade_level_from_strings(self, page_title: str, page_url: str) -> str:
        """
        Extract grade level from title and URL strings.
        
        Args:
            page_title: Page title
            page_url: Page URL
            
        Returns:
            str: Grade level
        """
        import re
        
        # Try title first
        if page_title:
            grade_patterns = [
                r'kindergarten',
                r'grade\s*(\d+)',
                r'algebra\s*(\d+)',
                r'geometry',
                r'pre-algebra',
                r'calculus'
            ]
            
            for pattern in grade_patterns:
                match = re.search(pattern, page_title, re.IGNORECASE)
                if match:
                    if 'kindergarten' in pattern:
                        return 'Kindergarten'
                    elif 'grade' in pattern:
                        return f'Grade {match.group(1)}'
                    elif 'algebra' in pattern:
                        return f'Algebra {match.group(1)}'
                    elif 'geometry' in pattern:
                        return 'Geometry'
                    elif 'pre-algebra' in pattern:
                        return 'Pre-Algebra'
                    elif 'calculus' in pattern:
                        return 'Calculus'
        
        # Try URL if title didn't work
        if page_url:
            url_patterns = [
                (r'kindergarten', 'Kindergarten'),
                (r'grade-(\d+)', 'Grade {}'),
                (r'algebra-(\d+)', 'Algebra {}'),
                (r'geometry', 'Geometry'),
                (r'pre-algebra', 'Pre-Algebra'),
                (r'calculus', 'Calculus')
            ]
            
            for pattern, format_str in url_patterns:
                match = re.search(pattern, page_url, re.IGNORECASE)
                if match:
                    if '{}' in format_str:
                        return format_str.format(match.group(1))
                    else:
                        return format_str
        
        return "Unknown Grade"
    
    def _extract_unit_name_soup(self, section) -> str:
        """
        Extract unit name from accordion section button using BeautifulSoup.
        
        Args:
            section: BeautifulSoup element for accordion section
            
        Returns:
            str: Unit name or empty string if not found
        """
        try:
            button = section.select_one("button")
            if button:
                unit_name = button.get_text(strip=True)
                self.logger.debug(f"Extracted unit name: {unit_name}")
                return unit_name
            return ""
        except Exception as e:
            self.logger.warning(f"Could not extract unit name: {e}")
            return ""
    
    def _extract_table_data_soup(self, section, unit_name: str, grade_level: str) -> List[Dict[str, Any]]:
        """
        Extract data from table within an accordion section using BeautifulSoup.
        
        Args:
            section: BeautifulSoup element for accordion section
            unit_name: Name of the unit/section
            grade_level: Grade level for this page
            
        Returns:
            List[Dict[str, Any]]: List of errata records from this section
        """
        records = []
        
        try:
            # Find table rows in this section
            rows = section.select(self.selectors['table_rows'])
            
            self.logger.debug(f"Found {len(rows)} table rows in section '{unit_name}'")
            
            for row in rows:
                try:
                    cells = row.find_all("td")
                    
                    if len(cells) >= 3:
                        # Extract data based on discovered structure:
                        # Column 1: Component (Resource/Location)
                        # Column 2: Improvement Description  
                        # Column 3: Date Updated
                        
                        component_text = cells[0].get_text(strip=True)
                        improvement_text = cells[1].get_text(strip=True)
                        date_text = cells[2].get_text(strip=True)
                        
                        # Parse component text to extract Resource and Location
                        resource, location, page_numbers = self._parse_component_text(component_text)
                        
                        errata_record = {
                            'Date_Extracted': datetime.now().strftime('%Y-%m-%d'),
                            'Grade_Level': grade_level,
                            'Unit': unit_name,
                            'Resource': resource,
                            'Location': location,
                            'Instructional_Moment': '',  # Not available in current structure
                            'Page_Numbers': page_numbers,
                            'Improvement_Description': improvement_text,
                            'Improvement_Type': '',  # Would need to be inferred from description
                            'Date_Updated': self._normalize_date(date_text)
                        }
                        
                        # Clean the record
                        errata_record = self._clean_errata_data(errata_record)
                        
                        if self._is_valid_errata_record(errata_record):
                            records.append(errata_record)
                            
                except Exception as e:
                    self.logger.warning(f"Failed to extract row data: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed to extract table data from section '{unit_name}': {e}")
        
        return records
        """
        Extract errata data from a single Selenium element.
        
        Args:
            container: Selenium WebElement containing errata data
            driver: Selenium WebDriver instance for context
            
        Returns:
            Optional[Dict[str, Any]]: Extracted errata data or None if extraction fails
        """
        try:
            errata_data = {}
            
            # Extract each field using the configured selectors
            errata_data['Unit'] = self._safe_extract_text(container, self.selectors['unit_field'])
            errata_data['Resource'] = self._safe_extract_text(container, self.selectors['resource_field'])
            errata_data['Location'] = self._safe_extract_text(container, self.selectors['location_field'])
            errata_data['Instructional_Moment'] = self._safe_extract_text(container, self.selectors['instructional_moment_field'])
            errata_data['Page_Numbers'] = self._safe_extract_text(container, self.selectors['page_numbers'])
            errata_data['Improvement_Description'] = self._safe_extract_text(container, self.selectors['improvement_description'])
            errata_data['Improvement_Type'] = self._safe_extract_text(container, self.selectors['improvement_type'])
            errata_data['Date_Updated'] = self._safe_extract_text(container, self.selectors['date_updated'])
            
            # Clean and normalize the extracted data
            errata_data = self._clean_errata_data(errata_data)
            
            # Validate that we have at least some meaningful data
            if self._is_valid_errata_record(errata_data):
                return errata_data
            else:
                self.logger.warning("Skipping invalid errata record")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to extract errata from element: {e}")
            return None
    
    def _extract_errata_from_soup_element(self, container) -> Optional[Dict[str, Any]]:
        """
        Extract errata data from a single BeautifulSoup element.
        
        Args:
            container: BeautifulSoup element containing errata data
            
        Returns:
            Optional[Dict[str, Any]]: Extracted errata data or None if extraction fails
        """
        try:
            errata_data = {}
            
            # Extract each field using the configured selectors
            errata_data['Unit'] = self._safe_extract_soup_text(container, self.selectors['unit_field'])
            errata_data['Resource'] = self._safe_extract_soup_text(container, self.selectors['resource_field'])
            errata_data['Location'] = self._safe_extract_soup_text(container, self.selectors['location_field'])
            errata_data['Instructional_Moment'] = self._safe_extract_soup_text(container, self.selectors['instructional_moment_field'])
            errata_data['Page_Numbers'] = self._safe_extract_soup_text(container, self.selectors['page_numbers'])
            errata_data['Improvement_Description'] = self._safe_extract_soup_text(container, self.selectors['improvement_description'])
            errata_data['Improvement_Type'] = self._safe_extract_soup_text(container, self.selectors['improvement_type'])
            errata_data['Date_Updated'] = self._safe_extract_soup_text(container, self.selectors['date_updated'])
            
            # Clean and normalize the extracted data
            errata_data = self._clean_errata_data(errata_data)
            
            # Validate that we have at least some meaningful data
            if self._is_valid_errata_record(errata_data):
                return errata_data
            else:
                self.logger.warning("Skipping invalid errata record")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to extract errata from soup element: {e}")
            return None
    
    def _safe_extract_text(self, container, selector: str) -> str:
        """
        Safely extract text from a Selenium element using CSS selector.
        
        Args:
            container: Parent Selenium element
            selector: CSS selector string
            
        Returns:
            str: Extracted text or empty string if not found
        """
        try:
            element = container.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except NoSuchElementException:
            return ""
        except Exception as e:
            self.logger.debug(f"Failed to extract text with selector '{selector}': {e}")
            return ""
    
    def _safe_extract_soup_text(self, container, selector: str) -> str:
        """
        Safely extract text from a BeautifulSoup element using CSS selector.
        
        Args:
            container: Parent BeautifulSoup element
            selector: CSS selector string
            
        Returns:
            str: Extracted text or empty string if not found
        """
        try:
            element = container.select_one(selector)
            if element:
                return element.get_text(strip=True)
            return ""
        except Exception as e:
            self.logger.debug(f"Failed to extract text with selector '{selector}': {e}")
            return ""
    
    def _clean_errata_data(self, errata_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize extracted errata data.
        
        Args:
            errata_data: Raw extracted data
            
        Returns:
            Dict[str, Any]: Cleaned errata data
        """
        cleaned_data = {}
        
        for key, value in errata_data.items():
            if isinstance(value, str):
                # Remove extra whitespace and normalize
                cleaned_value = re.sub(r'\s+', ' ', value.strip())
                
                # Specific cleaning for different fields
                if key == 'Page_Numbers':
                    cleaned_value = self._normalize_page_numbers(cleaned_value)
                elif key == 'Date_Updated':
                    cleaned_value = self._normalize_date(cleaned_value)
                elif key in ['Unit', 'Resource', 'Location']:
                    cleaned_value = self._normalize_categorical_field(cleaned_value)
                
                cleaned_data[key] = cleaned_value
            else:
                cleaned_data[key] = value
        
        return cleaned_data
    
    def _normalize_page_numbers(self, page_text: str) -> str:
        """
        Normalize page number text to a consistent format.
        
        Args:
            page_text: Raw page number text
            
        Returns:
            str: Normalized page number string
        """
        if not page_text:
            return ""
        
        # Extract numbers and ranges from text
        # Examples: "pages 12-15" -> "12-15", "page 7" -> "7", "pp. 20, 25" -> "20, 25"
        
        # Remove common prefixes/suffixes
        page_text = re.sub(r'\b(pages?|pp?\.?)\s*', '', page_text, flags=re.IGNORECASE)
        
        # Extract number ranges and individual numbers
        numbers = re.findall(r'\d+(?:-\d+)?', page_text)
        
        if numbers:
            return ', '.join(numbers)
        
        return page_text
    
    def _normalize_date(self, date_text: str) -> str:
        """
        Normalize date text to YYYY-MM-DD format.
        
        Args:
            date_text: Raw date text
            
        Returns:
            str: Normalized date string or original if conversion fails
        """
        if not date_text:
            return ""
        
        # Common date patterns to try
        date_patterns = [
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2})/(\d{1,2})/(\d{4})',   # MM/DD/YYYY
            r'(\d{1,2})-(\d{1,2})-(\d{4})',   # MM-DD-YYYY
            r'(\d{4})/(\d{1,2})/(\d{1,2})',   # YYYY/MM/DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_text)
            if match:
                try:
                    if pattern.startswith(r'(\d{4})'):  # Year first
                        year, month, day = match.groups()
                    else:  # Month/day first
                        month, day, year = match.groups()
                    
                    # Validate and format
                    date_obj = datetime.strptime(f"{year}-{int(month):02d}-{int(day):02d}", "%Y-%m-%d")
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        
        return date_text
    
    def _normalize_categorical_field(self, text: str) -> str:
        """
        Normalize categorical fields like Unit, Resource, Location.
        
        Args:
            text: Raw categorical text
            
        Returns:
            str: Normalized categorical text
        """
        if not text:
            return ""
        
        # Capitalize first letter of each word
        normalized = ' '.join(word.capitalize() for word in text.split())
        
        # Handle common abbreviations and formats
        abbreviations = {
            'Te': 'Teacher Edition',
            'Tg': 'Teacher Guide',
            'Tcg': 'Teacher Course Guide',
            'Se': 'Student Edition',
        }
        
        for abbrev, full_form in abbreviations.items():
            normalized = re.sub(rf'\b{abbrev}\b', full_form, normalized, flags=re.IGNORECASE)
        
        return normalized
    
    def _is_valid_errata_record(self, errata_data: Dict[str, Any]) -> bool:
        """
        Validate that an errata record has sufficient data.
        
        Args:
            errata_data: Extracted errata data
            
        Returns:
            bool: True if record is valid
        """
        # Require at least Unit and Resource to be present
        required_fields = ['Unit', 'Resource']
        
        for field in required_fields:
            if not errata_data.get(field):
                return False
        
        # Check if we have improvement description (main content)
        if not errata_data.get('Improvement_Description'):
            return False
        
        return True
    
    def extract_metadata(self, driver_or_soup) -> Dict[str, Any]:
        """
        Extract page metadata like title, last updated, etc.
        
        Args:
            driver_or_soup: Selenium driver or BeautifulSoup object
            
        Returns:
            Dict[str, Any]: Page metadata
        """
        metadata = {}
        
        try:
            if hasattr(driver_or_soup, 'title'):  # Selenium driver
                metadata['page_title'] = driver_or_soup.title
                metadata['current_url'] = driver_or_soup.current_url
            else:  # BeautifulSoup
                title_tag = driver_or_soup.find('title')
                metadata['page_title'] = title_tag.get_text(strip=True) if title_tag else ""
            
            metadata['extraction_timestamp'] = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Failed to extract metadata: {e}")
        
        return metadata
