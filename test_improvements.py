#!/usr/bin/env python3
"""
Test script to verify SD card wear fix and security enhancements
"""

import os
import json
import tempfile
import shutil
from datetime import datetime

def test_append_only_logging():
    """Test the new append-only logging system"""
    print("=== Testing Append-Only Logging ===")
    
    try:
        from sensor_monitor import SolarMonitor
        
        test_data_dir = tempfile.mkdtemp()
        
        original_data_dir = None
        try:
            from config import Config
            config = Config()
            original_data_dir = config.DATA_DIR
            config.DATA_DIR = test_data_dir
            
            monitor = SolarMonitor()
            
            reading = monitor.read_sensors()
            print(f"✅ Sensor reading successful: {len(reading['sensors'])} sensors")
            
            if monitor.current_log_file and monitor.current_log_file.endswith('.jsonl'):
                print(f"✅ Log file created with correct extension: {os.path.basename(monitor.current_log_file)}")
                
                if os.path.exists(monitor.current_log_file):
                    with open(monitor.current_log_file, 'r') as f:
                        content = f.read().strip()
                        if content:
                            print(f"✅ Log file contains data: {len(content)} characters")
                            try:
                                json.loads(content)
                                print("✅ Log file contains valid JSON")
                            except:
                                print("❌ Log file contains invalid JSON")
                        else:
                            print("❌ Log file is empty")
                else:
                    print("❌ Log file was not created")
            else:
                print("❌ Log file does not have .jsonl extension")
                
        finally:
            if original_data_dir:
                config.DATA_DIR = original_data_dir
            shutil.rmtree(test_data_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"❌ Append-only logging test failed: {e}")

def test_web_app_data_reading():
    """Test web app data reading with new format"""
    print("\n=== Testing Web App Data Reading ===")
    
    try:
        from web_app import DataReader
        
        test_data_dir = tempfile.mkdtemp()
        
        test_file = os.path.join(test_data_dir, "temp_log_test.jsonl")
        test_readings = [
            {"timestamp": "2025-01-07T10:00:00", "sensors": {"sensor1": 25.5, "sensor2": 30.2}},
            {"timestamp": "2025-01-07T10:00:05", "sensors": {"sensor1": 25.6, "sensor2": 30.1}}
        ]
        
        with open(test_file, 'w') as f:
            for reading in test_readings:
                f.write(json.dumps(reading) + '\n')
        
        reader = DataReader()
        original_data_dir = reader.config.DATA_DIR
        reader.config.DATA_DIR = test_data_dir
        
        try:
            data = reader.read_data_file(test_file)
            if len(data) == 2:
                print("✅ Successfully read JSONL file")
                print(f"✅ Read {len(data)} readings from JSONL file")
            else:
                print(f"❌ Expected 2 readings, got {len(data)}")
                
            files = reader.get_data_files()
            if len(files) > 0:
                print(f"✅ Found {len(files)} data files")
            else:
                print("❌ No data files found")
                
        finally:
            reader.config.DATA_DIR = original_data_dir
            shutil.rmtree(test_data_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"❌ Web app data reading test failed: {e}")

def test_security_config():
    """Test security configuration"""
    print("\n=== Testing Security Configuration ===")
    
    try:
        from config import Config
        config = Config()
        
        print(f"Debug mode: {config.WEB_DEBUG}")
        print(f"Username: {config.WEB_USERNAME}")
        print(f"Password configured: {'Yes' if config.WEB_PASSWORD else 'No'}")
        
        if not config.WEB_DEBUG:
            print("✅ Debug mode is disabled by default")
        else:
            print("⚠️ Debug mode is enabled")
            
        if config.WEB_USERNAME and config.WEB_PASSWORD:
            print("✅ Authentication credentials are configured")
        else:
            print("❌ Authentication credentials not properly configured")
            
    except Exception as e:
        print(f"❌ Security configuration test failed: {e}")

def test_migration_script():
    """Test the migration script"""
    print("\n=== Testing Migration Script ===")
    
    try:
        test_data_dir = tempfile.mkdtemp()
        test_json_file = os.path.join(test_data_dir, "temp_log_test.json")
        
        test_data = [
            {"timestamp": "2025-01-07T10:00:00", "sensors": {"sensor1": 25.5}},
            {"timestamp": "2025-01-07T10:00:05", "sensors": {"sensor1": 25.6}}
        ]
        
        with open(test_json_file, 'w') as f:
            json.dump(test_data, f)
        
        import sys
        sys.path.append('.')
        from migrate_data_format import migrate_json_to_jsonl
        
        jsonl_file = migrate_json_to_jsonl(test_json_file)
        
        if jsonl_file and os.path.exists(jsonl_file):
            print("✅ Migration script successfully converted JSON to JSONL")
            
            with open(jsonl_file, 'r') as f:
                lines = f.readlines()
                if len(lines) == 2:
                    print("✅ Converted file has correct number of lines")
                    
                    for i, line in enumerate(lines):
                        try:
                            json.loads(line.strip())
                            print(f"✅ Line {i+1} is valid JSON")
                        except:
                            print(f"❌ Line {i+1} is invalid JSON")
                else:
                    print(f"❌ Expected 2 lines, got {len(lines)}")
        else:
            print("❌ Migration script failed to create JSONL file")
            
        shutil.rmtree(test_data_dir, ignore_errors=True)
        
    except Exception as e:
        print(f"❌ Migration script test failed: {e}")

if __name__ == "__main__":
    print("Testing Solar Monitor Improvements")
    print("=" * 50)
    
    test_append_only_logging()
    test_web_app_data_reading()
    test_security_config()
    test_migration_script()
    
    print("\n" + "=" * 50)
    print("Testing completed!")
