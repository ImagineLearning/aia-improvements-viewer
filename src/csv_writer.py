"""
CSV writer module for formatting and saving errata data.
"""

import os
import csv
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path


class CSVWriter:
    """Handles writing errata data to CSV files."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.csv_path = Path(config['output']['csv_path'])
        self.backup_path = Path(config['output']['backup_path'])
        self.columns = config['output']['csv_columns']
        
        # Ensure output directories exist
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_path.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self) -> bool:
        """
        Create a backup of the existing CSV file.
        
        Returns:
            bool: True if backup created successfully or no file to backup
        """
        try:
            if self.csv_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"errata_changes_backup_{timestamp}.csv"
                backup_file_path = self.backup_path / backup_filename
                
                # Copy existing file to backup location
                import shutil
                shutil.copy2(self.csv_path, backup_file_path)
                
                self.logger.info(f"Backup created: {backup_file_path}")
                return True
            else:
                self.logger.info("No existing CSV file to backup")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False
    
    def write_errata_data(self, errata_list: List[Dict[str, Any]], mode: str = 'w') -> bool:
        """
        Write errata data to CSV file.
        
        Args:
            errata_list: List of dictionaries containing errata data
            mode: Write mode ('w' for overwrite, 'a' for append)
            
        Returns:
            bool: True if write successful
        """
        try:
            # Add extraction timestamp to each record
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for errata in errata_list:
                if 'Date_Extracted' not in errata:
                    errata['Date_Extracted'] = current_time
            
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(errata_list)
            
            # Ensure all required columns are present
            for col in self.columns:
                if col not in df.columns:
                    df[col] = ""  # Add empty column if missing
            
            # Reorder columns to match configuration
            df = df[self.columns]
            
            # Write to CSV
            write_header = mode == 'w' or not self.csv_path.exists()
            df.to_csv(self.csv_path, mode=mode, index=False, header=write_header, encoding='utf-8')
            
            self.logger.info(f"Successfully wrote {len(errata_list)} errata records to {self.csv_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write CSV: {e}")
            return False
    
    def append_errata_data(self, errata_list: List[Dict[str, Any]]) -> bool:
        """
        Append new errata data to existing CSV file.
        
        Args:
            errata_list: List of dictionaries containing new errata data
            
        Returns:
            bool: True if append successful
        """
        return self.write_errata_data(errata_list, mode='a')
    
    def load_existing_data(self) -> pd.DataFrame:
        """
        Load existing CSV data for comparison and deduplication.
        
        Returns:
            pd.DataFrame: Existing data or empty DataFrame if file doesn't exist
        """
        try:
            if self.csv_path.exists():
                df = pd.read_csv(self.csv_path, encoding='utf-8')
                self.logger.info(f"Loaded {len(df)} existing records from {self.csv_path}")
                return df
            else:
                self.logger.info("No existing CSV file found")
                return pd.DataFrame(columns=self.columns)
                
        except Exception as e:
            self.logger.error(f"Failed to load existing data: {e}")
            return pd.DataFrame(columns=self.columns)
    
    def deduplicate_errata(self, new_errata: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicates from new errata data based on existing records.
        
        Args:
            new_errata: List of new errata records
            
        Returns:
            List[Dict[str, Any]]: Deduplicated errata records
        """
        try:
            existing_df = self.load_existing_data()
            
            if existing_df.empty:
                return new_errata
            
            new_df = pd.DataFrame(new_errata)
            
            # Define key columns for duplicate detection
            key_columns = ['Unit', 'Resource', 'Location', 'Instructional_Moment', 'Page_Numbers']
            
            # Find duplicates by comparing key columns
            merged = new_df.merge(
                existing_df[key_columns], 
                on=key_columns, 
                how='left', 
                indicator=True
            )
            
            # Keep only records that don't exist in the existing data
            unique_records = merged[merged['_merge'] == 'left_only'].drop('_merge', axis=1)
            
            deduplicated_list = unique_records.to_dict('records')
            
            duplicates_found = len(new_errata) - len(deduplicated_list)
            if duplicates_found > 0:
                self.logger.info(f"Removed {duplicates_found} duplicate records")
            
            return deduplicated_list
            
        except Exception as e:
            self.logger.error(f"Failed to deduplicate errata: {e}")
            return new_errata
    
    def create_summary_report(self, errata_list: List[Dict[str, Any]]) -> str:
        """
        Create a summary report of the processed errata data.
        
        Args:
            errata_list: List of errata records
            
        Returns:
            str: Summary report text
        """
        try:
            df = pd.DataFrame(errata_list)
            
            if df.empty:
                return "No errata data found."
            
            summary = []
            summary.append(f"Total Errata Records: {len(df)}")
            summary.append(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            summary.append("")
            
            # Summary by Unit
            if 'Unit' in df.columns:
                unit_counts = df['Unit'].value_counts()
                summary.append("Records by Unit:")
                for unit, count in unit_counts.items():
                    summary.append(f"  {unit}: {count}")
                summary.append("")
            
            # Summary by Resource
            if 'Resource' in df.columns:
                resource_counts = df['Resource'].value_counts()
                summary.append("Records by Resource:")
                for resource, count in resource_counts.items():
                    summary.append(f"  {resource}: {count}")
                summary.append("")
            
            # Summary by Improvement Type
            if 'Improvement_Type' in df.columns:
                type_counts = df['Improvement_Type'].value_counts()
                summary.append("Records by Improvement Type:")
                for imp_type, count in type_counts.items():
                    summary.append(f"  {imp_type}: {count}")
            
            return "\n".join(summary)
            
        except Exception as e:
            self.logger.error(f"Failed to create summary report: {e}")
            return f"Error creating summary: {e}"
    
    def validate_data(self, errata_list: List[Dict[str, Any]]) -> List[str]:
        """
        Validate errata data for completeness and consistency.
        
        Args:
            errata_list: List of errata records to validate
            
        Returns:
            List[str]: List of validation warnings/errors
        """
        warnings = []
        
        for i, errata in enumerate(errata_list):
            record_num = i + 1
            
            # Check for required fields
            if not errata.get('Unit'):
                warnings.append(f"Record {record_num}: Missing Unit")
            
            if not errata.get('Resource'):
                warnings.append(f"Record {record_num}: Missing Resource")
            
            # Check date format for Date_Updated if present
            if errata.get('Date_Updated'):
                try:
                    datetime.strptime(errata['Date_Updated'], '%Y-%m-%d')
                except ValueError:
                    warnings.append(f"Record {record_num}: Invalid Date_Updated format (should be YYYY-MM-DD)")
            
            # Check for unusually long descriptions
            if errata.get('Improvement_Description') and len(errata['Improvement_Description']) > 500:
                warnings.append(f"Record {record_num}: Very long Improvement_Description (>500 chars)")
        
        return warnings
