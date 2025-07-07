#!/usr/bin/env python3
"""
Google Drive uploader for temperature log files
"""

import os
import logging
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import Config

logger = logging.getLogger(__name__)

class GoogleDriveUploader:
    """Handle Google Drive file uploads"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self):
        self.config = Config()
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API"""
        if not os.path.exists(self.config.GOOGLE_CREDENTIALS_FILE):
            logger.warning("Google credentials file not found. Upload will be skipped.")
            return
        
        try:
            creds = ServiceAccountCredentials.from_service_account_file(
                self.config.GOOGLE_CREDENTIALS_FILE, scopes=self.SCOPES)
            logger.info("Using service account authentication")
            
        except Exception as service_account_error:
            logger.info("Service account authentication failed, trying OAuth flow...")
            
            creds = None
            
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.config.GOOGLE_CREDENTIALS_FILE, self.SCOPES)
                        creds = flow.run_local_server(port=0)
                        
                        with open('token.json', 'w') as token:
                            token.write(creds.to_json())
                    except Exception as oauth_error:
                        logger.error(f"Both service account and OAuth authentication failed:")
                        logger.error(f"Service account error: {service_account_error}")
                        logger.error(f"OAuth error: {oauth_error}")
                        return
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Google Drive authentication successful")
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Drive: {e}")
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """Upload a file to Google Drive"""
        if not self.service:
            logger.warning("Google Drive service not available. Skipping upload.")
            return None
        
        try:
            filename = os.path.basename(file_path)
            
            file_metadata = {
                'name': filename,
            }
            
            if self.config.GOOGLE_DRIVE_FOLDER_ID:
                file_metadata['parents'] = [self.config.GOOGLE_DRIVE_FOLDER_ID]
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            logger.info(f"Successfully uploaded {filename} to Google Drive (ID: {file_id})")
            return file_id
            
        except Exception as e:
            logger.error(f"Failed to upload {file_path} to Google Drive: {e}")
            return None
    
    def list_files(self, folder_id: Optional[str] = None) -> list:
        """List files in Google Drive folder"""
        if not self.service:
            return []
        
        try:
            query = "mimeType != 'application/vnd.google-apps.folder'"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, createdTime)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            logger.error(f"Failed to list Google Drive files: {e}")
            return []
