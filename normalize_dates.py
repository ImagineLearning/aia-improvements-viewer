#!/usr/bin/env python3
"""
One-time script to clean up existing date formats in the CSV file.
"""

import sys
import os
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from csv_writer import CSVWriter
import yaml

def load_config():
    """Load configuration."""
    config_path = Path('src/config/config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    print("🔧 Cleaning up date formats in existing CSV file...")
    
    # Load config
    config = load_config()
    csv_writer = CSVWriter(config)
    
    # Read existing CSV
    csv_path = Path('output/sample_errata_changes.csv')
    if not csv_path.exists():
        print("❌ CSV file not found!")
        return 1
    
    df = pd.read_csv(csv_path)
    print(f"📊 Loaded {len(df)} records")
    
    # Show sample of current date formats
    print("\n📅 Current Date_Updated formats (sample):")
    date_samples = df['Date_Updated'].dropna().unique()[:10]
    for date in date_samples:
        print(f"  {date}")
    
    # Convert DataFrame back to list of dicts for processing
    errata_list = df.to_dict('records')
    
    # Normalize dates
    print("\n🔄 Normalizing dates...")
    normalized_errata = csv_writer.normalize_errata_dates(errata_list)
    
    # Create backup before overwriting
    print("💾 Creating backup...")
    backup_success = csv_writer.create_backup()
    if backup_success:
        print("✅ Backup created successfully")
    else:
        print("⚠️ Backup failed, continuing anyway")
    
    # Save normalized data
    print("💾 Saving normalized data...")
    success = csv_writer.write_errata_data(normalized_errata, mode='w')
    
    if success:
        print("✅ Date normalization completed!")
        
        # Show sample of normalized dates
        new_df = pd.read_csv(csv_path)
        print("\n📅 Normalized Date_Updated formats (sample):")
        new_date_samples = new_df['Date_Updated'].dropna().unique()[:10]
        for date in new_date_samples:
            print(f"  {date}")
        
        print(f"\n🎉 Successfully normalized {len(normalized_errata)} records!")
    else:
        print("❌ Failed to save normalized data")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
