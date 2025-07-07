# Solar Hot Water Heater Monitoring System

A comprehensive monitoring system for solar hot water heaters using Raspberry Pi Zero and 1-wire temperature sensors.

## Overview

This system monitors the temperature of 4 different pipes in a solar hot water heating system using 1-wire sensors connected to a Raspberry Pi Zero. The system provides real-time monitoring, data storage, automatic backups, and a web interface for visualization.

## Features

### Data Collection
- **Real-time monitoring**: Reads temperature from up to 4 1-wire sensors every 5 seconds
- **Sensor verification**: Automatically detects and verifies connected sensors before each reading cycle
- **Robust data logging**: Stores readings locally with append-only JSONL format to reduce SD card wear
- **Simulated sensors**: Falls back to simulated sensors for development and testing

### Data Storage & Backup
- **Local storage**: 90-day retention period to prevent SD card overflow
- **Automatic backup**: Hourly data files automatically uploaded to Google Drive after 60 minutes
- **Data integrity**: Reliable file handling and backup verification
- **SD card optimization**: Append-only logging reduces write operations by 99%

### Web Interface
- **Live dashboard**: Real-time display showing current temperatures from all 4 sensors
- **Historical charts**: Interactive charts displaying data for past 24 hours, 48 hours, or 1 week
- **Responsive design**: Works on desktop and mobile devices
- **Security**: HTTP Basic Authentication protects access to the web interface

### Recent Improvements
- **SD Card Wear Fix**: Switched from JSON to append-only JSONL format, reducing writes from 720 full file rewrites to single line appends per hour
- **Security Enhancements**: Added HTTP Basic Authentication, configurable debug mode, and production-ready settings
- **Backward Compatibility**: System reads both old JSON and new JSONL data formats seamlessly

## Hardware Requirements

- Raspberry Pi Zero (or Zero W for WiFi)
- Up to 4 x DS18B20 1-wire temperature sensors
- 4.7kΩ pull-up resistor for 1-wire bus
- MicroSD card (16GB+ recommended)
- Network connectivity (WiFi or Ethernet adapter)
- Power supply for Raspberry Pi

## Software Requirements

- Raspberry Pi OS (Raspbian)
- Python 3.x
- Required Python packages (see `requirements.txt`)
- Web browser for interface access
- Google Drive API credentials (for backup functionality)

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env file with your settings
nano .env
```

Required environment variables:
- `GOOGLE_DRIVE_FOLDER_ID`: Your Google Drive folder ID for backups
- `GOOGLE_CREDENTIALS_FILE`: Path to Google Drive API credentials
- `WEB_DEBUG`: Set to False for production
- `WEB_USERNAME`: Username for web interface authentication
- `WEB_PASSWORD`: Secure password for web interface

### 3. Set up Google Drive API
1. Create a Google Cloud project and enable the Drive API
2. Create service account credentials or OAuth credentials
3. Download the credentials JSON file
4. Update `GOOGLE_CREDENTIALS_FILE` in your `.env` file

### 4. Run the System
```bash
# Start the monitoring service
python sensor_monitor.py

# In another terminal, start the web interface
python web_app.py
```

### 5. Access Web Interface
- Open browser to `http://your-pi-ip:8080`
- Login with the credentials set in your `.env` file
- View real-time temperatures and historical charts

## File Structure

```
solar-monitoring-system/
├── README.md                    # This documentation
├── requirements.txt             # Python dependencies
├── config.py                    # Configuration settings
├── sensor_monitor.py            # Main monitoring service
├── web_app.py                   # Flask web interface
├── google_drive_uploader.py     # Google Drive backup integration
├── diagnose_sensors.py          # Sensor diagnostic utility
├── run_monitor.py               # Service runner script
├── migrate_data_format.py       # Data migration utility
├── test_improvements.py         # Test suite for improvements
├── templates/
│   └── index.html              # Web interface template
├── data/                        # Local data storage (auto-created)
├── env.example                  # Environment variables template
├── .env                         # Your environment settings (create this)
├── setup-autostart.sh          # Auto-start setup script
├── solar-monitor.service        # Systemd service file
└── IMPROVEMENTS.md              # Documentation of recent improvements
```

## Data Migration

If you have existing JSON data files, use the migration script to convert them to the new JSONL format:

```bash
python migrate_data_format.py
```

This will:
- Convert all existing JSON files to JSONL format
- Backup original files to `data/backup_json_files/`
- Preserve all historical data

## Systemd Service Setup

To run the monitoring system as a service:

```bash
# Make setup script executable
chmod +x setup-autostart.sh

# Run setup (will install service and start it)
sudo ./setup-autostart.sh

# Check service status
sudo systemctl status solar-monitor
```

## Troubleshooting

### Sensor Issues
- Run `python diagnose_sensors.py` to check sensor connectivity
- Verify 1-wire interface is enabled: `sudo raspi-config` → Interface Options → 1-Wire
- Check wiring and pull-up resistor (4.7kΩ)

### Web Interface Issues
- Check if port 8080 is available: `sudo netstat -tlnp | grep :8080`
- Verify authentication credentials in `.env` file
- Check Flask logs for error messages

### Google Drive Upload Issues
- Verify credentials file exists and is readable
- Check Google Drive API quotas and permissions
- Review upload logs in the monitoring output

## Development

This project was developed with assistance from Devin AI for continuous improvement and optimization.

### Contributing
- Follow existing code patterns and conventions
- Test changes thoroughly on Raspberry Pi hardware
- Update documentation for any new features
- Run the test suite: `python test_improvements.py`

### Testing
The system includes comprehensive tests for:
- Append-only logging functionality
- Web interface data reading
- Security configuration
- Data migration scripts

## Performance Optimizations

### SD Card Longevity
- **Before**: 720 full file rewrites per hour (~50MB+ writes)
- **After**: Single line appends per reading (~70KB writes per hour)
- **Result**: 99% reduction in SD card wear

### Security
- HTTP Basic Authentication on all web routes
- Configurable debug mode (disabled by default)
- Environment-based configuration management

## License

*License information to be added by repository owner.*
