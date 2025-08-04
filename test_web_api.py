#!/usr/bin/env python3
"""
Test script to verify web API endpoints work correctly
"""

import requests
import time
import subprocess
import signal
import os
import sys

def start_web_app():
    """Start the web app in background"""
    print("Starting web app...")
    process = subprocess.Popen([sys.executable, "web_app.py"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    time.sleep(3)  # Give it time to start
    return process

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:8080"
    auth = ("admin", "solar123")
    
    endpoints = [
        "/api/current",
        "/api/data/24h", 
        "/api/data/48h",
        "/api/data/1w",
        "/api/summary/24h",
        "/api/summary/48h", 
        "/api/summary/1w"
    ]
    
    print("\n=== Testing API Endpoints ===")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", auth=auth, timeout=5)
            print(f"{endpoint}: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    print(f"  Data points: {len(data['data'])}")
                elif 'summary' in data:
                    print(f"  Summary sensors: {len(data['summary'])}")
                elif 'sensors' in data:
                    print(f"  Current sensors: {len(data['sensors'])}")
                else:
                    print(f"  Response keys: {list(data.keys())}")
            else:
                print(f"  Error: {response.text}")
                
        except Exception as e:
            print(f"{endpoint}: Error - {e}")

def main():
    """Main test function"""
    print("Testing web API functionality...")
    
    web_process = start_web_app()
    
    try:
        test_api_endpoints()
        
    finally:
        print("\nStopping web app...")
        web_process.terminate()
        web_process.wait()

if __name__ == "__main__":
    main()
