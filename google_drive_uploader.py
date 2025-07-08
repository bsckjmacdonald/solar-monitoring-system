#!/usr/bin/env python3
"""
Google Drive uploader for temperature log files using rclone
"""

import os
import subprocess
import logging
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)

class GoogleDriveUploader:
    """Handle Google Drive file uploads using rclone"""
    
    def __init__(self):
        self.config = Config()
        self.gdrive_remote = "gdrive"  # Default rclone remote name for Google Drive
        self.gdrive_folder = "solar-monitor-data"  # Folder name in Google Drive
        self._check_rclone()
    
    def _check_rclone(self):
        """Check if rclone is installed and configured"""
        try:
            result = subprocess.run(["rclone", "version"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("rclone is available")
                self._ensure_folder()
            else:
                logger.warning("rclone is not installed. Install with: sudo apt install rclone")
        except FileNotFoundError:
            logger.warning("rclone is not installed. Install with: sudo apt install rclone")
        except Exception as e:
            logger.error(f"Error checking rclone: {e}")
    
    def _ensure_folder(self):
        """Ensure Google Drive folder exists"""
        try:
            result = subprocess.run(
                ["rclone", "lsd", f"{self.gdrive_remote}:"], 
                capture_output=True, text=True
            )
            if result.returncode == 0:
                if self.gdrive_folder not in result.stdout:
                    subprocess.run(["rclone", "mkdir", f"{self.gdrive_remote}:{self.gdrive_folder}"])
                    logger.info(f"Created Google Drive folder: {self.gdrive_folder}")
                return True
            else:
                logger.warning(f"Could not access Google Drive remote '{self.gdrive_remote}'. Configure with: rclone config")
                return False
        except Exception as e:
            logger.error(f"Error ensuring Google Drive folder: {e}")
            return False
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """Upload a file to Google Drive using rclone"""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
        
        try:
            filename = os.path.basename(file_path)
            
            result = subprocess.run(
                ["rclone", "copy", file_path, f"{self.gdrive_remote}:{self.gdrive_folder}/"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully uploaded {filename} to Google Drive")
                return filename
            else:
                logger.error(f"Failed to upload {filename}: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error during upload of {file_path}: {e}")
            return None
    
    def list_files(self, folder_id: Optional[str] = None) -> list:
        """List files in Google Drive folder using rclone"""
        try:
            result = subprocess.run(
                ["rclone", "ls", f"{self.gdrive_remote}:{self.gdrive_folder}/"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                files = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.strip().split(None, 1)
                        if len(parts) == 2:
                            size, name = parts
                            files.append({
                                'name': name,
                                'size': size,
                                'id': name  # Use filename as ID for compatibility
                            })
                return files
            else:
                logger.warning(f"Could not list files: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def sync_pending_files(self, data_dir: str):
        """Upload any pending files to Google Drive"""
        try:
            import glob
            
            json_files = glob.glob(os.path.join(data_dir, "temp_log_*.json"))
            jsonl_files = glob.glob(os.path.join(data_dir, "temp_log_*.jsonl"))
            
            all_files = json_files + jsonl_files
            
            for file_path in all_files:
                if not file_path.endswith('_current.json') and not file_path.endswith('_current.jsonl'):
                    self.upload_file(file_path)
                    
        except Exception as e:
            logger.error(f"Error syncing pending files: {e}")
