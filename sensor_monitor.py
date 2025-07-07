#!/usr/bin/env python3
"""
Solar Water Heater Temperature Monitor
Reads 4 1-wire temperature sensors every 5 seconds and logs data locally.
"""

import time
import json
import os
import glob
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import schedule
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DS18B20Sensor:
    """Real DS18B20 1-wire temperature sensor"""
    
    def __init__(self, sensor_id: str, device_path: str):
        self.sensor_id = sensor_id
        self.device_path = device_path
        
    def get_temperature(self) -> Optional[float]:
        """Get temperature reading from DS18B20 sensor"""
        try:
            with open(self.device_path, 'r') as f:
                lines = f.readlines()
            
            if len(lines) >= 2:
                if lines[0].strip().endswith('YES'):
                    temp_line = lines[1]
                    temp_pos = temp_line.find('t=')
                    if temp_pos != -1:
                        temp_string = temp_line[temp_pos + 2:]
                        temp_c = float(temp_string) / 1000.0
                        return temp_c
            return None
        except Exception as e:
            logger.error(f"Error reading DS18B20 sensor {self.sensor_id}: {e}")
            return None

class SimulatedSensor:
    """Simulated temperature sensor for development/testing"""
    
    def __init__(self, sensor_id: str, base_temp: float = 25.0):
        self.sensor_id = sensor_id
        self.base_temp = base_temp
        
    def get_temperature(self) -> Optional[float]:
        """Get temperature reading from sensor"""
        try:
            import random
            variation = random.uniform(-2.0, 2.0)
            return self.base_temp + variation
        except Exception as e:
            logger.error(f"Error reading sensor {self.sensor_id}: {e}")
            return None

class SolarMonitor:
    """Main monitoring class"""
    
    def __init__(self):
        self.config = Config()
        self.sensors = self._initialize_sensors()
        self.current_log_file = None
        self.current_log_data = []
        
        os.makedirs(self.config.DATA_DIR, exist_ok=True)
        
        self._create_new_log_file()
        
    def _scan_for_real_sensors(self) -> List[str]:
        """Scan for connected DS18B20 1-wire sensors using multiple methods"""
        sensor_paths = []
        
        try:
            from w1thermsensor import W1ThermSensor
            library_sensors = W1ThermSensor.get_available_sensors()
            logger.info(f"w1thermsensor library found {len(library_sensors)} sensors")
            
            for sensor in library_sensors:
                device_path = f"/sys/bus/w1/devices/{sensor.id}/w1_slave"
                if os.path.exists(device_path):
                    sensor_paths.append(device_path)
                    logger.info(f"Added sensor via library: {sensor.id}")
            
            if sensor_paths:
                logger.info(f"Found {len(sensor_paths)} real DS18B20 sensors via w1thermsensor library")
                return sensor_paths
                
        except ImportError:
            logger.info("w1thermsensor library not available, falling back to filesystem scan")
        except Exception as e:
            logger.warning(f"w1thermsensor library error: {e}, falling back to filesystem scan")
        
        try:
            base_dir = '/sys/bus/w1/devices/'
            if not os.path.exists(base_dir):
                logger.info("1-wire interface not available")
                return []
            
            device_folders = glob.glob(base_dir + '28-*')
            logger.info(f"Filesystem scan found {len(device_folders)} potential DS18B20 devices")
            
            for folder in device_folders:
                w1_slave_path = os.path.join(folder, 'w1_slave')
                if os.path.exists(w1_slave_path):
                    sensor_paths.append(w1_slave_path)
                    sensor_id = os.path.basename(folder)
                    logger.info(f"Added sensor via filesystem: {sensor_id}")
                    
            logger.info(f"Found {len(sensor_paths)} real DS18B20 sensors via filesystem scan")
            return sensor_paths
            
        except Exception as e:
            logger.error(f"Error scanning for real sensors: {e}")
            return []
    
    def _initialize_sensors(self) -> List:
        """Initialize temperature sensors (mix of real and simulated)"""
        sensors = []
        
        logger.info("Starting sensor initialization...")
        real_sensor_paths = self._scan_for_real_sensors()
        logger.info(f"Sensor scan completed. Found {len(real_sensor_paths)} real sensors")
        
        preferred_names = ["inlet", "collector", "tank_bottom", "tank_top"]
        
        for i, sensor_path in enumerate(real_sensor_paths[:self.config.SENSORS_COUNT]):
            if i < len(preferred_names):
                sensor_name = preferred_names[i]
            else:
                sensor_name = f"sensor_{i+1}"
            sensors.append(DS18B20Sensor(sensor_name, sensor_path))
            logger.info(f"Initialized real sensor: {sensor_name} at {sensor_path}")
        
        remaining_slots = self.config.SENSORS_COUNT - len(sensors)
        logger.info(f"Need to create {remaining_slots} simulated sensors")
        
        for i in range(remaining_slots):
            sensor_name = f"simulated{i + 1}"
            base_temp = 25.0
            
            sensors.append(SimulatedSensor(sensor_name, base_temp))
            logger.info(f"Initialized simulated sensor: {sensor_name}")
            
        logger.info(f"Sensor initialization complete: {len(real_sensor_paths)} real, {remaining_slots} simulated")
        return sensors
    
    def _create_new_log_file(self):
        """Create a new hourly log file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H")
        filename = f"{self.config.LOG_FILE_PREFIX}_{timestamp}.jsonl"  # .jsonl for line-delimited JSON
        self.current_log_file = os.path.join(self.config.DATA_DIR, filename)
        self.current_log_data = []
        
        if not os.path.exists(self.current_log_file):
            with open(self.current_log_file, 'w') as f:
                pass  # Create empty file
        
        logger.info(f"Created new log file: {self.current_log_file}")
    
    def read_sensors(self) -> Dict:
        """Read all temperature sensors"""
        timestamp = datetime.now().isoformat()
        readings = {
            "timestamp": timestamp,
            "sensors": {}
        }
        
        for sensor in self.sensors:
            temp = sensor.get_temperature()
            readings["sensors"][sensor.sensor_id] = temp
            
        return readings
    
    def log_reading(self, reading: Dict):
        """Log a temperature reading using append-only method to reduce SD card wear"""
        self.current_log_data.append(reading)
        
        try:
            with open(self.current_log_file, 'a') as f:
                f.write(json.dumps(reading) + '\n')
        except Exception as e:
            logger.error(f"Error writing to log file: {e}")
    
    def close_current_log(self):
        """Close current log file and prepare for upload"""
        if self.current_log_file and os.path.exists(self.current_log_file):
            logger.info(f"Closing log file: {self.current_log_file}")
            
            try:
                from google_drive_uploader import GoogleDriveUploader
                uploader = GoogleDriveUploader()
                uploader.upload_file(self.current_log_file)
                logger.info(f"Uploaded {self.current_log_file} to Google Drive")
            except Exception as e:
                logger.error(f"Failed to upload to Google Drive: {e}")
            
            self._cleanup_old_files()
            self._create_new_log_file()
    
    def _cleanup_old_files(self):
        """Remove data files older than 90 days to save SD card space"""
        try:
            cutoff_date = datetime.now() - timedelta(days=90)
            data_files = glob.glob(os.path.join(self.config.DATA_DIR, f"{self.config.LOG_FILE_PREFIX}_*.json*"))  # Match both .json and .jsonl
            
            deleted_count = 0
            for file_path in data_files:
                try:
                    filename = os.path.basename(file_path)
                    date_part = filename.replace(f"{self.config.LOG_FILE_PREFIX}_", "").replace(".json", "").replace(".jsonl", "")
                    
                    if len(date_part) >= 11:
                        date_str = date_part[:8]
                        file_date = datetime.strptime(date_str, "%Y%m%d")
                        
                        if file_date < cutoff_date:
                            os.remove(file_path)
                            deleted_count += 1
                            logger.info(f"Deleted old data file: {filename}")
                            
                except Exception as e:
                    logger.warning(f"Error processing file {file_path} for cleanup: {e}")
            
            if deleted_count > 0:
                logger.info(f"Cleanup completed: removed {deleted_count} files older than 90 days")
                
        except Exception as e:
            logger.error(f"Error during file cleanup: {e}")
    
    def run_monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Starting temperature monitoring...")
        logger.info("Data uploads to Google Drive every hour at :00 minutes")
        logger.info("Local data files are retained for 90 days then automatically deleted")
        
        schedule.every().hour.at(":00").do(self.close_current_log)
        
        try:
            while True:
                reading = self.read_sensors()
                
                self.log_reading(reading)
                
                sensor_temps = [f"{k}: {v:.1f}°C" for k, v in reading["sensors"].items() if v is not None]
                logger.info(f"Readings - {', '.join(sensor_temps)}")
                
                schedule.run_pending()
                
                time.sleep(self.config.SENSOR_READ_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
        finally:
            self.close_current_log()

def main():
    """Main entry point"""
    monitor = SolarMonitor()
    monitor.run_monitoring_loop()

if __name__ == "__main__":
    main()
