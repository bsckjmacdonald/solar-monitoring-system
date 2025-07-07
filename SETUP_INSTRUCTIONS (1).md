# Solar Water Heater Monitor - Setup Instructions

## Overview
This system monitors solar water heater performance using 4 temperature sensors on a Raspberry Pi Zero, with local logging, Google Drive backup, and web interface.

## Hardware Requirements
- Raspberry Pi Zero (or any Raspberry Pi)
- 4 x DS18B20 1-wire temperature sensors
- 4.7kΩ pull-up resistor
- Breadboard and jumper wires
- MicroSD card (16GB+)

## Software Installation

### 1. Raspberry Pi Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install git -y
```

### 2. Enable 1-Wire Interface
```bash
# Edit boot config
sudo nano /boot/config.txt

# Add this line:
dtoverlay=w1-gpio

# Reboot
sudo reboot
```

### 3. Install Project
```bash
# Clone or copy project files to Pi
cd /home/pi
# (Copy all project files here)

# Create virtual environment
python3 -m venv solar-monitor-env
source solar-monitor-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Hardware Wiring
Connect DS18B20 sensors:
- VDD (red) → 3.3V
- GND (black) → Ground  
- DATA (yellow) → GPIO 4 (Pin 7)
- 4.7kΩ resistor between VDD and DATA

### 5. Google Drive Setup (Optional)
1. Go to Google Cloud Console
2. Create new project or select existing
3. Enable Google Drive API
4. Create service account credentials
5. Download credentials.json file
6. Copy to project directory
7. Create .env file:
```
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
GOOGLE_CREDENTIALS_FILE=credentials.json
```

## Running the System

### Manual Start
```bash
# Start monitoring service
python3 sensor_monitor.py

# In another terminal, start web interface
python3 web_app.py
```

### Automatic Start (Recommended)
```bash
# Use the combined runner
python3 run_monitor.py
```

### System Service (Auto-start on boot)
```bash
# Create service file
sudo nano /etc/systemd/system/solar-monitor.service

# Add content:
[Unit]
Description=Solar Water Heater Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/solar-monitor
ExecStart=/home/pi/solar-monitor-env/bin/python /home/pi/solar-monitor/run_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl enable solar-monitor.service
sudo systemctl start solar-monitor.service
```

## Accessing the Web Interface

1. Find Pi's IP address: `hostname -I`
2. Open browser to: `http://PI_IP_ADDRESS:8080`
3. View current readings and historical data

## File Structure
- `sensor_monitor.py` - Main monitoring service
- `web_app.py` - Web interface
- `google_drive_uploader.py` - Google Drive integration
- `config.py` - Configuration settings
- `data/` - Local temperature data files
- `templates/` - Web interface templates

## Troubleshooting

### No Sensor Data
- Check 1-wire is enabled: `ls /sys/bus/w1/devices/`
- Verify wiring connections
- Check sensor IDs in code

### Web Interface Not Loading
- Check if service is running: `sudo systemctl status solar-monitor`
- Verify port 8080 is not blocked
- Check logs: `journalctl -u solar-monitor -f`

### Google Drive Upload Fails
- Verify credentials.json exists
- Check internet connection
- Ensure Google Drive API is enabled
- Check folder permissions

## Data Format
Temperature readings are stored in JSON format:
```json
{
  "timestamp": "2025-07-03T19:27:53.643107",
  "sensors": {
    "inlet": 18.8,
    "collector": 43.8,
    "tank_bottom": 33.0,
    "tank_top": 39.9
  }
}
```

## Customization
- Modify sensor names in `sensor_monitor.py`
- Adjust reading interval in `config.py`
- Change web interface port in `config.py`
- Add more sensors by updating sensor initialization

## Maintenance
- Log files rotate hourly automatically
- Check disk space periodically
- Monitor system logs for errors
- Update software dependencies regularly
