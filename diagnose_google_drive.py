#!/usr/bin/env python3
"""
Google Drive Backup Diagnostic Tool
Helps troubleshoot Google Drive upload issues in the solar monitoring system
"""

import os
import json
import logging
from datetime import datetime
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_configuration():
    """Check Google Drive configuration"""
    print("=== Google Drive Configuration Check ===")
    
    config = Config()
    
    if os.path.exists('.env'):
        print("✅ .env file exists")
        with open('.env', 'r') as f:
            env_content = f.read()
            if 'GOOGLE_DRIVE_FOLDER_ID' in env_content:
                print("✅ GOOGLE_DRIVE_FOLDER_ID found in .env")
            else:
                print("❌ GOOGLE_DRIVE_FOLDER_ID missing from .env")
    else:
        print("❌ .env file does not exist")
        print("   Create .env file from env.example template")
    
    folder_id = config.GOOGLE_DRIVE_FOLDER_ID
    if folder_id:
        print(f"✅ Google Drive Folder ID configured: {folder_id}")
        if folder_id.startswith('http'):
            print("⚠️  WARNING: Folder ID looks like a URL, should be just the ID part")
            print("   Example: '1ABC123xyz' not 'https://drive.google.com/drive/folders/1ABC123xyz'")
    else:
        print("❌ Google Drive Folder ID not configured")
    
    creds_file = config.GOOGLE_CREDENTIALS_FILE
    if os.path.exists(creds_file):
        print(f"✅ Credentials file exists: {creds_file}")
        try:
            with open(creds_file, 'r') as f:
                creds_data = json.load(f)
                if 'type' in creds_data:
                    if creds_data['type'] == 'service_account':
                        print("✅ Service account credentials detected")
                    else:
                        print("✅ OAuth client credentials detected")
                else:
                    print("⚠️  Credentials file format unclear")
        except json.JSONDecodeError:
            print("❌ Credentials file is not valid JSON")
        except Exception as e:
            print(f"❌ Error reading credentials file: {e}")
    else:
        print(f"❌ Credentials file not found: {creds_file}")

def test_google_drive_connection():
    """Test Google Drive connection (both rclone and API)"""
    print("\n=== Google Drive Connection Test ===")
    
    print("Testing rclone connection...")
    try:
        import subprocess
        result = subprocess.run(["rclone", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ rclone is installed")
            
            result = subprocess.run(["rclone", "lsd", "gdrive:"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ rclone Google Drive connection successful")
                
                result = subprocess.run(["rclone", "ls", "gdrive:solar-monitor-data/"], capture_output=True, text=True)
                if result.returncode == 0:
                    files = [line.strip().split(None, 1)[1] for line in result.stdout.strip().split('\n') if line.strip()]
                    print(f"✅ Found {len(files)} files in solar-monitor-data folder")
                    if files:
                        print("   Recent files:")
                        for file in files[-5:]:
                            print(f"     - {file}")
                else:
                    print("⚠️  solar-monitor-data folder not found or empty")
                    print("   Run: python setup_rclone.py to create it")
            else:
                print("❌ rclone Google Drive connection failed")
                print(f"   Error: {result.stderr}")
                print("   Run: rclone config to set up Google Drive")
        else:
            print("❌ rclone not found")
            print("   Install with: sudo apt install rclone")
    except FileNotFoundError:
        print("❌ rclone not installed")
        print("   Install with: sudo apt install rclone")
    except Exception as e:
        print(f"❌ Error testing rclone: {e}")
    
    print("\nTesting legacy Google Drive API...")
    try:
        from google_drive_uploader import GoogleDriveUploader
        
        uploader = GoogleDriveUploader()
        files = uploader.list_files()
        print(f"✅ rclone-based uploader working, found {len(files)} files")
        
    except ImportError as e:
        print(f"⚠️  Legacy API libraries not available: {e}")
        print("   This is OK - using rclone instead")
    except Exception as e:
        print(f"⚠️  Legacy API test failed: {e}")
        print("   This is OK - using rclone instead")

def check_data_files():
    """Check for data files that should be uploaded"""
    print("\n=== Data Files Check ===")
    
    config = Config()
    data_dir = config.DATA_DIR
    
    if os.path.exists(data_dir):
        print(f"✅ Data directory exists: {data_dir}")
        
        import glob
        json_files = glob.glob(os.path.join(data_dir, f"{config.LOG_FILE_PREFIX}_*.json"))
        jsonl_files = glob.glob(os.path.join(data_dir, f"{config.LOG_FILE_PREFIX}_*.jsonl"))
        
        all_files = json_files + jsonl_files
        
        if all_files:
            print(f"✅ Found {len(all_files)} data files")
            print("   Recent files:")
            for file_path in sorted(all_files)[-5:]:
                filename = os.path.basename(file_path)
                size = os.path.getsize(file_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"     - {filename} ({size} bytes, modified: {mtime})")
        else:
            print("❌ No data files found")
            print("   Start the monitoring system to generate data files")
    else:
        print(f"❌ Data directory does not exist: {data_dir}")

def check_upload_schedule():
    """Check upload scheduling"""
    print("\n=== Upload Schedule Check ===")
    
    current_time = datetime.now()
    current_minute = current_time.minute
    
    print(f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Files are uploaded every hour at :00 minutes")
    
    if current_minute == 0:
        print("✅ Upload should happen now (if monitoring is running)")
    else:
        minutes_until_upload = 60 - current_minute
        print(f"⏰ Next upload in {minutes_until_upload} minutes")
    
    print("\nTo trigger immediate upload for testing:")
    print("1. Stop the monitoring system")
    print("2. In Python shell:")
    print("   from sensor_monitor import SolarMonitor")
    print("   monitor = SolarMonitor()")
    print("   monitor.close_current_log()  # This triggers upload")

def extract_folder_id_from_url(url):
    """Extract folder ID from Google Drive URL"""
    if '/folders/' in url:
        return url.split('/folders/')[1].split('?')[0].split('/')[0]
    return None

def main():
    """Run all diagnostic checks"""
    print("Google Drive Backup Diagnostic Tool")
    print("=" * 50)
    
    check_configuration()
    test_google_drive_connection()
    check_data_files()
    check_upload_schedule()
    
    print("\n" + "=" * 50)
    print("Diagnostic completed!")
    
    print("\n=== Quick Fix for Folder ID ===")
    print("If you have a Google Drive folder URL like:")
    print("https://drive.google.com/drive/folders/1ABC123xyz")
    print("The folder ID is: 1ABC123xyz")
    print("\nAdd this to your .env file:")
    print("GOOGLE_DRIVE_FOLDER_ID=1ABC123xyz")

if __name__ == "__main__":
    main()
