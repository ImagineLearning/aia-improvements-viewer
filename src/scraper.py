"""
Main scraper module for coordinating the errata extraction process.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from auth import WebAuthenticator, load_credentials, AuthenticationError
from parser import ErrataParser
from csv_writer import CSVWriter


class ErrataScraper:
    """Main scraper class that coordinates authentication, parsing, and data export."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.authenticator = WebAuthenticator(config)
        self.parser = ErrataParser(config)
        self.csv_writer = CSVWriter(config)
        
        self.all_errata = []
        self.extraction_metadata = {}
    
    def run_full_extraction(self, use_selenium: bool = True) -> bool:
        """
        Run the complete errata extraction process.
        
        Args:
            use_selenium: Whether to use Selenium (True) or requests-html (False)
            
        Returns:
            bool: True if extraction completed successfully
        """
        try:
            self.logger.info("Starting errata extraction process")
            
            # Step 1: Load credentials and authenticate
            if not self._authenticate(use_selenium):
                return False
            
            # Step 2: Extract errata from all configured pages
            if not self._extract_all_errata(use_selenium):
                return False
            
            # Step 3: Process and save data
            if not self._process_and_save_data():
                return False
            
            # Step 4: Generate summary report
            self._generate_summary_report()
            
            self.logger.info("Errata extraction completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            return False
        finally:
            # Always clean up
            self.authenticator.logout()
    
    def _authenticate(self, use_selenium: bool) -> bool:
        """
        Handle authentication process.
        
        Args:
            use_selenium: Whether to use Selenium for authentication
            
        Returns:
            bool: True if authentication successful
        """
        try:
            username, password = load_credentials()
            
            if use_selenium:
                success = self.authenticator.login_with_selenium(username, password)
            else:
                success = self.authenticator.login_with_requests(username, password)
            
            if not success:
                self.logger.error("Authentication failed")
                return False
            
            self.logger.info("Authentication successful")
            return True
            
        except ValueError as e:
            self.logger.error(f"Credential error: {e}")
            return False
        except AuthenticationError as e:
            self.logger.error(f"Authentication error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected authentication error: {e}")
            return False
    
    def _extract_all_errata(self, use_selenium: bool) -> bool:
        """
        Extract errata from all configured pages.
        
        Args:
            use_selenium: Whether to use Selenium for extraction
            
        Returns:
            bool: True if extraction successful
        """
        errata_pages = self.config['website']['errata_pages']
        base_url = self.config['website']['base_url']
        
        self.logger.info(f"Extracting errata from {len(errata_pages)} pages")
        
        for page_path in errata_pages:
            try:
                full_url = base_url + page_path
                self.logger.info(f"Processing page: {full_url}")
                
                page_errata = self._extract_from_single_page(full_url, use_selenium)
                
                if page_errata:
                    self.all_errata.extend(page_errata)
                    self.logger.info(f"Extracted {len(page_errata)} errata from {full_url}")
                else:
                    self.logger.warning(f"No errata found on {full_url}")
                
                # Add delay between requests
                delay = self.config['scraping']['delay_between_requests']
                if delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"Failed to extract from {page_path}: {e}")
                continue
        
        total_errata = len(self.all_errata)
        self.logger.info(f"Total errata extracted: {total_errata}")
        
        return total_errata > 0
    
    def _extract_from_single_page(self, url: str, use_selenium: bool) -> List[Dict[str, Any]]:
        """
        Extract errata from a single page.
        
        Args:
            url: Full URL to extract from
            use_selenium: Whether to use Selenium
            
        Returns:
            List[Dict[str, Any]]: Extracted errata records
        """
        try:
            if use_selenium:
                driver = self.authenticator.get_authenticated_driver()
                if not driver:
                    self.logger.error("No authenticated driver available")
                    return []
                
                driver.get(url)
                
                # Wait for page to load
                time.sleep(2)
                
                # Extract metadata
                metadata = self.parser.extract_metadata(driver)
                self.extraction_metadata[url] = metadata
                
                # Parse errata data
                return self.parser.parse_page_with_selenium(driver)
                
            else:
                session = self.authenticator.get_authenticated_session()
                if not session:
                    self.logger.error("No authenticated session available")
                    return []
                
                response = session.get(url)
                response.html.render()  # Execute JavaScript if needed
                
                # Extract metadata
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.html.html, 'html.parser')
                metadata = self.parser.extract_metadata(soup)
                self.extraction_metadata[url] = metadata
                
                # Parse errata data
                return self.parser.parse_page_with_beautifulsoup(response.html.html)
                
        except Exception as e:
            self.logger.error(f"Failed to extract from {url}: {e}")
            return []
    
    def _process_and_save_data(self) -> bool:
        """
        Process extracted data and save to CSV.
        
        Returns:
            bool: True if processing and saving successful
        """
        try:
            if not self.all_errata:
                self.logger.warning("No errata data to process")
                return False
            
            # Validate the data
            validation_warnings = self.csv_writer.validate_data(self.all_errata)
            if validation_warnings:
                self.logger.warning("Data validation warnings:")
                for warning in validation_warnings:
                    self.logger.warning(f"  {warning}")
            
            # Deduplicate against existing data
            deduplicated_errata = self.csv_writer.deduplicate_errata(self.all_errata)
            
            if not deduplicated_errata:
                self.logger.info("No new errata found after deduplication")
                return True
            
            # Create backup of existing data
            if not self.csv_writer.create_backup():
                self.logger.warning("Failed to create backup, continuing anyway")
            
            # Write new data
            success = self.csv_writer.write_errata_data(deduplicated_errata)
            
            if success:
                self.logger.info(f"Successfully saved {len(deduplicated_errata)} errata records")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to process and save data: {e}")
            return False
    
    def _generate_summary_report(self):
        """Generate and log a summary report of the extraction."""
        try:
            summary = self.csv_writer.create_summary_report(self.all_errata)
            
            self.logger.info("EXTRACTION SUMMARY:")
            self.logger.info("=" * 50)
            for line in summary.split('\n'):
                self.logger.info(line)
            self.logger.info("=" * 50)
            
            # Save summary to file
            summary_path = Path(self.config['output']['csv_path']).parent / "extraction_summary.txt"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary)
                f.write(f"\n\nExtraction Metadata:\n")
                for url, metadata in self.extraction_metadata.items():
                    f.write(f"\nURL: {url}\n")
                    for key, value in metadata.items():
                        f.write(f"  {key}: {value}\n")
            
            self.logger.info(f"Summary report saved to: {summary_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary report: {e}")
    
    def run_incremental_update(self, use_selenium: bool = True) -> bool:
        """
        Run an incremental update, appending only new errata to existing CSV.
        
        Args:
            use_selenium: Whether to use Selenium
            
        Returns:
            bool: True if update successful
        """
        try:
            self.logger.info("Starting incremental errata update")
            
            # Same process as full extraction, but deduplication will handle filtering
            return self.run_full_extraction(use_selenium)
            
        except Exception as e:
            self.logger.error(f"Incremental update failed: {e}")
            return False
    
    def test_authentication_only(self, use_selenium: bool = True) -> bool:
        """
        Test authentication without running full extraction.
        
        Args:
            use_selenium: Whether to use Selenium for testing
            
        Returns:
            bool: True if authentication test successful
        """
        try:
            self.logger.info("Testing authentication...")
            
            success = self._authenticate(use_selenium)
            
            if success:
                self.logger.info("Authentication test successful")
                
                # Test navigation to first errata page
                if self.config['website']['errata_pages']:
                    test_url = self.config['website']['base_url'] + self.config['website']['errata_pages'][0]
                    self.logger.info(f"Testing navigation to: {test_url}")
                    
                    if use_selenium:
                        driver = self.authenticator.get_authenticated_driver()
                        if driver:
                            driver.get(test_url)
                            self.logger.info(f"Successfully navigated to test page: {driver.title}")
                    else:
                        session = self.authenticator.get_authenticated_session()
                        if session:
                            response = session.get(test_url)
                            self.logger.info(f"Successfully accessed test page (status: {response.status_code})")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Authentication test failed: {e}")
            return False
        finally:
            self.authenticator.logout()
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the last extraction.
        
        Returns:
            Dict[str, Any]: Extraction statistics
        """
        return {
            'total_errata_extracted': len(self.all_errata),
            'pages_processed': len(self.extraction_metadata),
            'extraction_metadata': self.extraction_metadata
        }
