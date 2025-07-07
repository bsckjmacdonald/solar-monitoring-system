# Solar Hot Water Heater Monitoring System

A comprehensive monitoring system for solar hot water heaters using Raspberry Pi Zero and 1-wire temperature sensors.

## Overview

This system monitors the temperature of 4 different pipes in a solar hot water heating system using 1-wire sensors connected to a Raspberry Pi Zero. The system provides real-time monitoring, data storage, automatic backups, and a web interface for visualization.

## Features

### Data Collection
- **Real-time monitoring**: Reads temperature from up to 4 1-wire sensors every 5 seconds
- **Sensor verification**: Automatically detects and verifies connected sensors before each reading cycle
- **Robust data logging**: Stores readings locally with configurable retention period

### Data Storage & Backup
- **Local storage**: 90-day retention period to prevent SD card overflow
- **Automatic backup**: Hourly data files automatically uploaded to Google Drive after 60 minutes
- **Data integrity**: Reliable file handling and backup verification

### Web Interface
- **Live dashboard**: Real-time display showing current temperatures from all 4 sensors
- **Historical charts**: Interactive charts displaying data for past 24 hours, 48 hours, or 1 week
- **Responsive design**: Works on desktop and mobile devices

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
- Required Python packages (see `requirements.txt` when uploaded)
- Web browser for interface access
- Google Drive API credentials (for backup functionality)

## Repository Structure

```
solar-monitoring-system/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── src/                      # Source code
│   ├── main.py              # Main monitoring script
│   ├── sensor_reader.py     # 1-wire sensor interface
│   ├── data_manager.py      # Data storage and retention
│   ├── backup_manager.py    # Google Drive backup
│   └── web_interface/       # Web dashboard
│       ├── app.py           # Web server
│       ├── static/          # CSS, JS, images
│       └── templates/       # HTML templates
├── config/                   # Configuration files
│   ├── config.ini           # Main configuration
│   └── sensors.json         # Sensor mapping
├── data/                     # Local data storage (gitignored)
├── logs/                     # Log files (gitignored)
└── docs/                     # Documentation
    ├── installation.md      # Setup instructions
    ├── configuration.md     # Configuration guide
    └── troubleshooting.md   # Common issues
```

## Quick Start

*Installation and setup instructions will be added once the code is uploaded.*

## Configuration

*Configuration details will be documented once the code files are available.*

## Usage

*Usage instructions will be provided after code upload.*

## Development

This project was developed with assistance from Devin AI for continuous improvement and optimization.

### Contributing
- Follow existing code patterns and conventions
- Test changes thoroughly on Raspberry Pi hardware
- Update documentation for any new features

## License

*License information to be added by repository owner.*

---

## Next Steps

**For Repository Owner**: Please upload your solar monitoring system files according to the structure above:

1. **Core Python Scripts**: Upload your main monitoring script and related modules
2. **Web Interface**: Upload HTML, CSS, JavaScript files for the dashboard
3. **Configuration Files**: Upload configuration templates (remove any sensitive data)
4. **Dependencies**: Create `requirements.txt` with all Python package dependencies
5. **Documentation**: Add any setup notes, installation instructions, or usage guides

Once the code is uploaded, this repository will be ready for evaluation and improvement recommendations!
