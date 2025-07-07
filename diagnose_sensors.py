#!/usr/bin/env python3
"""
Comprehensive DS18B20 sensor diagnostic script
"""

import os
import glob
import subprocess

def check_1wire_interface():
    print("=== 1-Wire Interface Check ===")
    base_dir = '/sys/bus/w1/devices/'
    if os.path.exists(base_dir):
        devices = os.listdir(base_dir)
        print(f"1-wire devices found: {devices}")
        
        ds18b20_devices = [d for d in devices if d.startswith('28-')]
        print(f"DS18B20 sensors found: {ds18b20_devices}")
        
        return ds18b20_devices
    else:
        print("1-wire interface not available at /sys/bus/w1/devices/")
        return []

def check_kernel_modules():
    print("\n=== Kernel Modules Check ===")
    try:
        result = subprocess.run(['lsmod'], capture_output=True, text=True)
        w1_modules = [line for line in result.stdout.split('\n') if 'w1' in line]
        if w1_modules:
            print("W1 modules loaded:")
            for module in w1_modules:
                print(f"  {module}")
        else:
            print("No W1 modules found. Try loading them:")
            print("  sudo modprobe w1-gpio")
            print("  sudo modprobe w1-therm")
    except Exception as e:
        print(f"Error checking kernel modules: {e}")

def test_w1thermsensor_library():
    print("\n=== W1ThermSensor Library Test ===")
    try:
        from w1thermsensor import W1ThermSensor
        sensors = W1ThermSensor.get_available_sensors()
        print(f"w1thermsensor library found {len(sensors)} sensors:")
        for sensor in sensors:
            print(f"  Sensor ID: {sensor.id}, Type: {sensor.type}")
            try:
                temp = sensor.get_temperature()
                print(f"    Temperature: {temp:.2f}°C")
            except Exception as e:
                print(f"    Error reading: {e}")
        return sensors
    except ImportError:
        print("w1thermsensor library not installed")
        return []
    except Exception as e:
        print(f"Error with w1thermsensor library: {e}")
        return []

def test_direct_sensor_reading():
    print("\n=== Direct Sensor Reading Test ===")
    try:
        sensor_files = glob.glob('/sys/bus/w1/devices/28-*/w1_slave')
        print(f"Found {len(sensor_files)} sensor files:")
        
        for sensor_file in sensor_files:
            sensor_id = sensor_file.split('/')[-2]
            print(f"\nReading sensor {sensor_id}:")
            try:
                with open(sensor_file, 'r') as f:
                    content = f.read()
                    print(f"  Raw content: {content.strip()}")
                    
                    lines = content.strip().split('\n')
                    if len(lines) >= 2 and lines[0].endswith('YES'):
                        temp_line = lines[1]
                        temp_pos = temp_line.find('t=')
                        if temp_pos != -1:
                            temp_string = temp_line[temp_pos + 2:]
                            temp_c = float(temp_string) / 1000.0
                            print(f"  Temperature: {temp_c:.2f}°C")
                    else:
                        print("  Error: Invalid sensor reading")
                        
            except Exception as e:
                print(f"  Error reading {sensor_file}: {e}")
                
    except Exception as e:
        print(f"Error in direct sensor reading: {e}")

if __name__ == "__main__":
    print("DS18B20 Sensor Diagnostic Tool")
    print("=" * 40)
    
    ds18b20_devices = check_1wire_interface()
    check_kernel_modules()
    library_sensors = test_w1thermsensor_library()
    test_direct_sensor_reading()
    
    print("\n=== Summary ===")
    print(f"Filesystem detection: {len(ds18b20_devices)} sensors")
    print(f"Library detection: {len(library_sensors)} sensors")
    
    if not ds18b20_devices and not library_sensors:
        print("\nNo sensors detected. Check:")
        print("1. Hardware wiring (VDD->3.3V, GND->GND, DATA->GPIO4)")
        print("2. 4.7kΩ pull-up resistor between VDD and DATA")
        print("3. 1-wire enabled in /boot/config.txt: dtoverlay=w1-gpio")
        print("4. Kernel modules loaded: sudo modprobe w1-gpio w1-therm")
    else:
        print(f"\nSensors detected successfully!")
