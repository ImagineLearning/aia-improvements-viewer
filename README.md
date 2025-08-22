# Errata Locator

A Python script that automatically extracts errata information from curriculum websites and exports it to CSV format.

## Features

- 🔐 **Secure Authentication**: Handles login with VPN compatibility  
- 🕷️ **Web Scraping**: Extracts data from accordion-structured errata pages
- 📊 **CSV Export**: Outputs structured data with configurable columns
- 🔍 **Data Validation**: Ensures data quality and consistency
- 📝 **Comprehensive Logging**: Detailed logs for troubleshooting
- ⚡ **Automated Processing**: End-to-end extraction with minimal setup

## Output Format

The script generates a CSV file with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| Date_Extracted | When the data was extracted | 2025-08-21 14:30:15 |
| Unit | Curriculum unit identifier | Unit 1, Unit 2, etc. |
| Resource | Type of resource | Teacher Guide, Teacher Edition Glossary, Student Edition |
| Location | Specific location within resource | Lesson 3 Section A, Chapter 2 |
| Instructional_Moment | Type of instructional activity | Warm-up, Activity, Lesson Synthesis |
| Page_Numbers | Relevant page numbers | 12-15, 7, 20, 25 |
| Improvement_Description | Description of the change/correction | Updated calculation formula |
| Improvement_Type | Type of improvement | Correction, Update, Enhancement |
| Date_Updated | When the improvement was made | 2025-08-15 |

## Installation

1. **Clone or download the project**:
   ```powershell
   cd "c:\Users\RyandelaGarza\.vscode\AIA Builds\Errata-Locator"
   ```

2. **Install Python dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Set up configuration**:
   - Copy `config/credentials.env.template` to `config/.env`
   - Edit `config/.env` with your actual website credentials
   - Update `config/config.yaml` with your website's specific URLs and selectors

## Configuration

### Credentials (config/.env)
```env
USERNAME=your_username_here
PASSWORD=your_password_here
```

### Website Configuration (config/config.yaml)
Update the following sections for your specific curriculum website:

```yaml
website:
  base_url: "https://your-curriculum-site.com"
  login_url: "/login"
  errata_pages:
    - "/errata/unit1"
    - "/errata/unit2"

selectors:
  errata_container: ".errata-list"
  unit_field: ".unit-name"
  resource_field: ".resource-type"
  # ... other selectors
```

## Usage

### Basic Commands

**Full extraction** (recommended for first run):
```powershell
python main.py
```

**Test authentication only**:
```powershell
python main.py --test-auth
```

**Incremental update** (add only new errata):
```powershell
python main.py --incremental
```

**Use requests instead of Selenium** (faster, but may miss dynamic content):
```powershell
python main.py --use-requests
```

**Validate setup**:
```powershell
python main.py --validate-setup
```

### Advanced Options

**Use custom configuration file**:
```powershell
python main.py --config path/to/custom-config.yaml
```

**Combine options**:
```powershell
python main.py --incremental --use-requests
```

## Project Structure

```
Errata-Locator/
├── main.py                    # Entry point script
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── src/
│   ├── auth.py               # Authentication handling
│   ├── scraper.py            # Main scraping coordination
│   ├── parser.py             # HTML parsing and data extraction
│   └── csv_writer.py         # CSV output and data processing
├── config/
│   ├── config.yaml           # Main configuration
│   ├── credentials.env.template  # Template for credentials
│   └── .env                  # Your actual credentials (create this)
├── output/
│   ├── errata_changes.csv    # Generated CSV file
│   └── backups/              # Automatic backups
└── logs/
    └── errata_locator.log    # Application logs
```

## Troubleshooting

### Common Issues

1. **Import errors when running**:
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check that you're running from the correct directory

2. **Authentication failures**:
   - Verify credentials in `config/.env`
   - Test authentication only: `python main.py --test-auth`
   - Check that the login URL and selectors are correct

3. **No data extracted**:
   - Verify the errata page URLs in `config.yaml`
   - Check CSS selectors for data extraction
   - Try using Selenium instead of requests: remove `--use-requests` flag

4. **Chrome driver issues** (when using Selenium):
   - The script automatically downloads the Chrome driver
   - Make sure Chrome browser is installed
   - Check firewall/antivirus settings

### Debugging

**Enable debug logging** by editing `config/config.yaml`:
```yaml
logging:
  level: "DEBUG"
```

**Check log files** in the `logs/` directory for detailed error information.

## Customization

### Adding New Data Fields

1. Add new selectors to `config/config.yaml`:
   ```yaml
   selectors:
     new_field: ".new-field-selector"
   ```

2. Add the field to CSV columns:
   ```yaml
   output:
     csv_columns:
       - "Date_Extracted"
       - "New_Field"
       # ... other columns
   ```

3. Update parsing logic in `src/parser.py` if needed.

### Different Website Structures

If your curriculum website has a different structure:

1. Update the `selectors` section in `config/config.yaml`
2. Modify the login process in `src/auth.py` if needed
3. Adjust parsing logic in `src/parser.py` for your specific HTML structure

## Scheduling

To run the script automatically:

### Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, weekly, etc.)
4. Action: Start a program
5. Program: `python`
6. Arguments: `main.py --incremental`
7. Start in: `c:\Users\RyandelaGarza\.vscode\AIA Builds\Errata-Locator`

### PowerShell Scheduled Job
```powershell
$trigger = New-ScheduledTaskTrigger -Daily -At "09:00AM"
$action = New-ScheduledTaskAction -Execute "python" -Argument "main.py --incremental" -WorkingDirectory "c:\Users\RyandelaGarza\.vscode\AIA Builds\Errata-Locator"
Register-ScheduledTask -TaskName "ErrataLocator" -Trigger $trigger -Action $action
```

## Security Notes

- Never commit the `.env` file to version control
- Use environment variables for sensitive credentials
- The script respects rate limiting to avoid overwhelming servers
- Consider using application-specific passwords if available

## Support

For issues or questions:
1. Check the logs in `logs/errata_locator.log`
2. Run with `--validate-setup` to check configuration
3. Test authentication separately with `--test-auth`
4. Enable debug logging for more detailed information
