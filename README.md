# Solar Water Heater Monitoring System

A Raspberry Pi Zero-based system to monitor solar water heater performance using 4 1-wire temperature sensors.

## Features

- Reads 4 temperature sensors every 5 seconds
- Logs data locally with hourly file rotation
- Uploads hourly data files to Google Drive
- Web interface to view historical data (24h, 48h, 1 week)

## Hardware Requirements

- Raspberry Pi Zero
- 4 x DS18B20 1-wire temperature sensors
- Appropriate wiring and pull-up resistors

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Configure Google Drive API credentials
3. Run the monitoring service: `python sensor_monitor.py`
4. Start the web interface: `python web_app.py`

## File Structure

- `sensor_monitor.py` - Main monitoring service
- `web_app.py` - Flask web interface
- `google_drive_uploader.py` - Google Drive integration
- `config.py` - Configuration settings
- `data/` - Local data storage directory
