#!/usr/bin/env python3
"""
Setup script for rclone Google Drive integration
"""

import subprocess
import sys
import os

def check_rclone_installed():
    """Check if rclone is installed"""
    try:
        result = subprocess.run(["rclone", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ rclone is installed")
            print(f"Version: {result.stdout.split()[1]}")
            return True
        else:
            print("❌ rclone is not working properly")
            return False
    except FileNotFoundError:
        print("❌ rclone is not installed")
        return False

def install_rclone():
    """Install rclone"""
    print("Installing rclone...")
    try:
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "rclone"], check=True)
        print("✅ rclone installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install rclone: {e}")
        return False

def configure_rclone():
    """Guide user through rclone configuration"""
    print("\n=== rclone Google Drive Configuration ===")
    print("Follow these steps to configure rclone for Google Drive:")
    print()
    print("1. Run: rclone config")
    print("2. Choose 'n' for new remote")
    print("3. Name: gdrive")
    print("4. Storage type: drive (Google Drive)")
    print("5. Client ID: (leave blank for default)")
    print("6. Client Secret: (leave blank for default)")
    print("7. Scope: drive (full access)")
    print("8. Root folder ID: (leave blank)")
    print("9. Service account file: (leave blank)")
    print("10. Advanced config: No")
    print("11. Auto config: Yes (will open browser)")
    print("12. Configure as team drive: No")
    print("13. Confirm configuration")
    print()
    print("After configuration, test with: rclone lsd gdrive:")
    print()

def test_rclone_config():
    """Test rclone configuration"""
    print("Testing rclone Google Drive connection...")
    try:
        result = subprocess.run(["rclone", "lsd", "gdrive:"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ rclone Google Drive connection successful")
            print("Available folders:")
            print(result.stdout)
            return True
        else:
            print("❌ rclone Google Drive connection failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing rclone: {e}")
        return False

def create_solar_folder():
    """Create solar monitor data folder"""
    print("Creating solar-monitor-data folder...")
    try:
        result = subprocess.run(
            ["rclone", "mkdir", "gdrive:solar-monitor-data"], 
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✅ Created solar-monitor-data folder in Google Drive")
            return True
        else:
            print(f"❌ Failed to create folder: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error creating folder: {e}")
        return False

def main():
    """Main setup function"""
    print("Solar Monitor - rclone Google Drive Setup")
    print("=" * 50)
    
    if not check_rclone_installed():
        if input("Install rclone? (y/n): ").lower() == 'y':
            if not install_rclone():
                sys.exit(1)
        else:
            print("rclone is required for Google Drive uploads")
            sys.exit(1)
    
    if not test_rclone_config():
        print("\nrclone needs to be configured for Google Drive")
        configure_rclone()
        
        input("Press Enter after completing rclone configuration...")
        
        if not test_rclone_config():
            print("❌ rclone configuration failed")
            sys.exit(1)
    
    create_solar_folder()
    
    print("\n" + "=" * 50)
    print("✅ rclone setup complete!")
    print()
    print("Your solar monitoring system will now use rclone for Google Drive uploads.")
    print("Files will be uploaded to: gdrive:solar-monitor-data/")
    print()
    print("To test uploads manually:")
    print("  rclone copy /path/to/file gdrive:solar-monitor-data/")
    print()
    print("To view uploaded files:")
    print("  rclone ls gdrive:solar-monitor-data/")

if __name__ == "__main__":
    main()
