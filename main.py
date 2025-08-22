"""
Main entry point for the Errata Locator script.

This script crawls curriculum websites to extract errata information
and saves it to a CSV file with the following columns:
- Date_Extracted
- Unit
- Resource  
- Location
- Instructional_Moment
- Page_Numbers
- Improvement_Description
- Improvement_Type
- Date_Updated
"""

import os
import sys
import argparse
import logging
import colorlog
from pathlib import Path
from typing import Dict, Any

import yaml
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

from scraper import ErrataScraper


def setup_logging(config: Dict[str, Any]) -> None:
    """Set up logging configuration with colors."""
    
    # Create logs directory if it doesn't exist
    log_file = Path(config.get('logging', {}).get('file', './logs/errata_locator.log'))
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Set up colored console logging
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    
    # Set up file logging
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(
        config.get('logging', {}).get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.get('logging', {}).get('level', 'INFO')))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    
    if config_path is None:
        config_path = Path(__file__).parent / 'config' / 'config.yaml'
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def load_environment_variables() -> None:
    """Load environment variables from .env file."""
    
    env_file = Path(__file__).parent / 'config' / '.env'
    
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded environment variables from {env_file}")
    else:
        print(f"No .env file found at {env_file}")
        print("Please create one from the credentials.env.template file")


def create_sample_env_file() -> None:
    """Create a sample .env file from the template."""
    
    template_path = Path(__file__).parent / 'config' / 'credentials.env.template'
    env_path = Path(__file__).parent / 'config' / '.env'
    
    if template_path.exists() and not env_path.exists():
        import shutil
        shutil.copy2(template_path, env_path)
        print(f"Created sample .env file at {env_path}")
        print("Please edit this file and add your actual credentials")
        return True
    
    return False


def validate_setup() -> bool:
    """Validate that all required files and configurations are in place."""
    
    required_files = [
        Path(__file__).parent / 'config' / 'config.yaml',
        Path(__file__).parent / 'config' / '.env',
    ]
    
    missing_files = []
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(str(file_path))
    
    if missing_files:
        print("Missing required files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        
        if str(Path(__file__).parent / 'config' / '.env') in missing_files:
            if create_sample_env_file():
                print("\nA sample .env file has been created. Please edit it with your credentials.")
            missing_files.remove(str(Path(__file__).parent / 'config' / '.env'))
        
        return len(missing_files) == 0
    
    return True


def main():
    """Main function."""
    
    parser = argparse.ArgumentParser(
        description="Extract errata information from curriculum websites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                     # Run full extraction
  python main.py --test-auth         # Test authentication only
  python main.py --incremental       # Run incremental update
  python main.py --use-requests      # Use requests instead of Selenium
  python main.py --config custom.yaml  # Use custom config file
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration YAML file (default: config/config.yaml)'
    )
    
    parser.add_argument(
        '--test-auth', '-t',
        action='store_true',
        help='Test authentication only, do not extract errata'
    )
    
    parser.add_argument(
        '--incremental', '-i',
        action='store_true',
        help='Run incremental update (append new errata to existing CSV)'
    )
    
    parser.add_argument(
        '--use-requests', '-r',
        action='store_true',
        help='Use requests-html instead of Selenium (faster but may miss dynamic content)'
    )
    
    parser.add_argument(
        '--validate-setup', '-v',
        action='store_true',
        help='Validate setup and configuration files'
    )
    
    args = parser.parse_args()
    
    # Validate setup if requested
    if args.validate_setup:
        if validate_setup():
            print("✓ Setup validation passed")
            return 0
        else:
            print("✗ Setup validation failed")
            return 1
    
    try:
        # Load environment variables
        load_environment_variables()
        
        # Load configuration
        config = load_config(args.config)
        
        # Set up logging
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        logger.info("Starting Errata Locator")
        logger.info(f"Configuration loaded from: {args.config or 'config/config.yaml'}")
        
        # Validate setup
        if not validate_setup():
            logger.error("Setup validation failed")
            return 1
        
        # Initialize scraper
        scraper = ErrataScraper(config)
        
        # Determine whether to use Selenium or requests
        use_selenium = not args.use_requests
        method = "Selenium" if use_selenium else "requests-html"
        logger.info(f"Using {method} for web scraping")
        
        # Run requested operation
        success = False
        
        if args.test_auth:
            logger.info("Running authentication test")
            success = scraper.test_authentication_only(use_selenium)
            
        elif args.incremental:
            logger.info("Running incremental update")
            success = scraper.run_incremental_update(use_selenium)
            
        else:
            logger.info("Running full extraction")
            success = scraper.run_full_extraction(use_selenium)
        
        # Print results
        if success:
            logger.info("Operation completed successfully")
            
            if not args.test_auth:
                stats = scraper.get_extraction_stats()
                logger.info(f"Extraction statistics: {stats}")
            
            return 0
        else:
            logger.error("Operation failed")
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
        
    except Exception as e:
        if 'logger' in locals():
            logger.error(f"Unexpected error: {e}", exc_info=True)
        else:
            print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
