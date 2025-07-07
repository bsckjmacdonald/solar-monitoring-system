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
    
    WEB_HOST = "0.0.0.0"
    WEB_PORT = 8080
    
    RETENTION_24H = 24
    RETENTION_48H = 48
    RETENTION_1W = 168  # 7 days * 24 hours
