#!/usr/bin/env python3
"""
Convenience script to run both the sensor monitor and web interface
"""

import subprocess
import threading
import time
import signal
import sys

def run_sensor_monitor():
    """Run the sensor monitoring service"""
    subprocess.run([sys.executable, "sensor_monitor.py"])

def run_web_app():
    """Run the web interface"""
    subprocess.run([sys.executable, "web_app.py"])

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down solar monitor...")
    sys.exit(0)

def main():
    """Main entry point"""
    print("Starting Solar Water Heater Monitor...")
    print("Press Ctrl+C to stop")
    
    signal.signal(signal.SIGINT, signal_handler)
    
    monitor_thread = threading.Thread(target=run_sensor_monitor, daemon=True)
    monitor_thread.start()
    
    time.sleep(2)
    
    try:
        run_web_app()
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()
