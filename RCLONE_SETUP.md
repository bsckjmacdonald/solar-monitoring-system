# rclone Google Drive Setup Guide

This guide will help you set up rclone for Google Drive uploads, which is simpler and more reliable than the Google Drive API.

## Why rclone?

- ✅ **Simpler setup** - No OAuth credentials or service accounts needed
- ✅ **More reliable** - No quota issues or authentication complexity
- ✅ **Better error handling** - Clear error messages and retry logic
- ✅ **Widely supported** - Standard tool for cloud storage operations

## Quick Setup

### 1. Install rclone
```bash
sudo apt update
sudo apt install rclone
```

### 2. Run Setup Script
```bash
python setup_rclone.py
```

This script will:
- Check if rclone is installed
- Guide you through Google Drive configuration
- Create the solar-monitor-data folder
- Test the connection

### 3. Manual Configuration (if needed)

If the setup script doesn't work, configure manually:

```bash
rclone config
```

Follow these steps:
1. Choose `n` for new remote
2. Name: `gdrive`
3. Storage type: `drive` (Google Drive)
4. Client ID: (leave blank)
5. Client Secret: (leave blank)
6. Scope: `drive` (full access)
7. Root folder ID: (leave blank)
8. Service account file: (leave blank)
9. Advanced config: `No`
10. Auto config: `Yes` (opens browser)
11. Sign in to your Google account
12. Configure as team drive: `No`
13. Confirm configuration

### 4. Test Configuration

```bash
# List Google Drive folders
rclone lsd gdrive:

# Create solar monitor folder
rclone mkdir gdrive:solar-monitor-data

# Test upload
echo "test" > test.txt
rclone copy test.txt gdrive:solar-monitor-data/
rm test.txt

# Verify upload
rclone ls gdrive:solar-monitor-data/
```

## Environment Configuration

Update your `.env` file:
```bash
# rclone Configuration (Recommended)
RCLONE_REMOTE=gdrive
RCLONE_FOLDER=solar-monitor-data
```

## Troubleshooting

### "command not found: rclone"
```bash
sudo apt update
sudo apt install rclone
```

### "Failed to configure token"
- Make sure you have a web browser available
- Try running `rclone config` manually
- Check your internet connection

### "403 Forbidden" errors
- Re-run `rclone config` to refresh authentication
- Make sure you granted full Drive access during setup

### "No such remote" errors
- Check that your remote is named `gdrive`
- Run `rclone listremotes` to see configured remotes

## Verification

After setup, run the diagnostic:
```bash
python diagnose_google_drive.py
```

You should see:
- ✅ rclone is installed
- ✅ rclone Google Drive connection successful
- ✅ Found files in solar-monitor-data folder

## Migration from API Method

If you were previously using the Google Drive API:

1. Your existing data will continue to work
2. New uploads will use rclone automatically
3. You can remove the Google API dependencies:
   ```bash
   pip uninstall google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```
4. Remove `credentials.json` and `token.json` files (optional)

The system will automatically fall back to rclone if the API libraries are not available.
