import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SENSOR_READ_INTERVAL = 5  # seconds
    SENSORS_COUNT = 4
    
    DATA_DIR = "data"
    LOG_FILE_PREFIX = "temp_log"
    
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    
    RCLONE_REMOTE = os.getenv('RCLONE_REMOTE', 'gdrive')
    RCLONE_FOLDER = os.getenv('RCLONE_FOLDER', 'solar-monitor-data')
    
    WEB_HOST = "0.0.0.0"
    WEB_PORT = 8080
    
    WEB_DEBUG = os.getenv('WEB_DEBUG', 'False').lower() == 'true'
    WEB_USERNAME = os.getenv('WEB_USERNAME', 'admin')
    WEB_PASSWORD = os.getenv('WEB_PASSWORD', 'solar123')  # Default password - should be changed
    
    RETENTION_24H = 24
    RETENTION_48H = 48
    RETENTION_1W = 168  # 7 days * 24 hours
