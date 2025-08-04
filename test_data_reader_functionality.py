#!/usr/bin/env python3
"""
Test script to verify DataReader functionality and identify reboot issue
"""

import os
import sys
from web_app import DataReader

def test_data_reader():
    print('=== DataReader Test ===')
    print('Current working directory:', os.getcwd())
    
    reader = DataReader()
    print('DATA_DIR config:', reader.config.DATA_DIR)
    print('Full DATA_DIR path:', os.path.abspath(reader.config.DATA_DIR))
    print('DATA_DIR exists:', os.path.exists(reader.config.DATA_DIR))
    
    files = reader.get_data_files()
    print('Found files:', files)
    
    for f in files:
        data = reader.read_data_file(f)
        print(f'File {f}: {len(data)} readings')
        if data:
            print(f'  First reading: {data[0]}')
            print(f'  Last reading: {data[-1]}')
    
    print('\n=== Testing get_data_for_period ===')
    for hours in [24, 48, 168]:
        data = reader.get_data_for_period(hours)
        print(f'{hours}h period: {len(data)} readings')
        if data:
            print(f'  Earliest: {data[0]["timestamp"]}')
            print(f'  Latest: {data[-1]["timestamp"]}')

def test_from_different_directory():
    print('\n=== Testing from different working directory ===')
    original_cwd = os.getcwd()
    os.chdir('/tmp')
    print('Changed to:', os.getcwd())
    
    reader = DataReader()
    print('DATA_DIR config:', reader.config.DATA_DIR)
    print('Full DATA_DIR path:', os.path.abspath(reader.config.DATA_DIR))
    print('DATA_DIR exists:', os.path.exists(reader.config.DATA_DIR))
    
    files = reader.get_data_files()
    print('Found files:', files)
    
    for hours in [24, 48]:
        data = reader.get_data_for_period(hours)
        print(f'{hours}h period from /tmp: {len(data)} readings')
    
    os.chdir(original_cwd)

if __name__ == "__main__":
    test_data_reader()
    test_from_different_directory()
