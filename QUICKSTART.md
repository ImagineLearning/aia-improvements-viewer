# Errata Locator - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. **Virtual Environment Setup** ✅ COMPLETED
```powershell
# Navigate to project directory
cd "c:\Users\RyandelaGarza\.vscode\AIA Builds\Errata-Locator"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies (or use Python tools in VS Code)
pip install -r requirements.txt
```

### 2. **Configure Your Credentials**
Edit the file: `config\.env`
```env
USERNAME=your_actual_username
PASSWORD=your_actual_password
```

### 3. **Update Website Configuration**
Edit the file: `config\config.yaml`

Update these sections with your curriculum website details:
```yaml
website:
  base_url: "https://your-curriculum-website.com"
  login_url: "/login"
  errata_pages:
    - "/errata/page1"
    - "/errata/page2"
```

### 4. **Update CSS Selectors**
In `config\config.yaml`, update the selectors to match your website's HTML structure:
```yaml
selectors:
  errata_container: ".errata-item"        # Container for each errata entry
  unit_field: ".unit"                     # Unit identifier
  resource_field: ".resource-type"        # Resource type
  location_field: ".location"             # Location within resource
  instructional_moment_field: ".moment"   # Instructional moment
  page_numbers: ".pages"                  # Page numbers
  improvement_description: ".description" # Description of change
  improvement_type: ".type"               # Type of improvement
  date_updated: ".date"                   # Date of update
```

## 🧪 Testing

### Test Authentication
```powershell
python main.py --test-auth
```

### Test Full Setup
```powershell
python main.py --validate-setup
```

## 🏃‍♂️ Running the Script

### First Run (Full Extraction)
```powershell
python main.py
```

### Subsequent Runs (Incremental Updates)
```powershell
python main.py --incremental
```

## 📁 Output

Your errata data will be saved to:
- **Main CSV**: `output\errata_changes.csv`
- **Backups**: `output\backups\`
- **Logs**: `logs\errata_locator.log`
- **Summary**: `output\extraction_summary.txt`

## 🛠️ Available Commands

| Command | Description |
|---------|-------------|
| `python main.py` | Full extraction (overwrites existing CSV) |
| `python main.py --incremental` | Add only new errata to existing CSV |
| `python main.py --test-auth` | Test login without extracting data |
| `python main.py --use-requests` | Use requests instead of Selenium (faster) |
| `python main.py --validate-setup` | Check configuration and files |

## 🎯 Expected CSV Output

The script will generate a CSV with these columns:
- **Date_Extracted**: When the data was scraped
- **Unit**: Curriculum unit (Unit 1, Unit 2, etc.)
- **Resource**: Type of resource (Teacher Guide, Student Edition, etc.)
- **Location**: Specific location (Lesson 3 Section A, Chapter 2, etc.)
- **Instructional_Moment**: Activity type (Warm-up, Activity, Lesson Synthesis, etc.)
- **Page_Numbers**: Relevant pages (12-15, 7, 20, 25, etc.)
- **Improvement_Description**: What was changed/corrected
- **Improvement_Type**: Type of change (Correction, Update, Enhancement)
- **Date_Updated**: When the improvement was made

## ⚠️ Common Issues

1. **Chrome Driver Issues**: The script auto-downloads Chrome driver, but make sure Chrome browser is installed
2. **Authentication Failures**: Double-check your credentials and website URLs
3. **No Data Found**: Verify CSS selectors match your website's HTML structure
4. **PowerShell Execution Policy**: If scripts won't run, you may need to run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## 🔄 Automation

To run automatically, set up a Windows scheduled task:
```powershell
# Example: Run every weekday at 9 AM
$trigger = New-ScheduledTaskTrigger -Daily -At "09:00AM" -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday
$action = New-ScheduledTaskAction -Execute "python" -Argument "main.py --incremental" -WorkingDirectory "c:\Users\RyandelaGarza\.vscode\AIA Builds\Errata-Locator"
Register-ScheduledTask -TaskName "ErrataLocator" -Trigger $trigger -Action $action
```

## 📞 Need Help?

1. Check the logs: `logs\errata_locator.log`
2. Run setup validation: `python main.py --validate-setup`
3. Test authentication only: `python main.py --test-auth`
4. Enable debug logging in `config\config.yaml`:
   ```yaml
   logging:
     level: "DEBUG"
   ```
