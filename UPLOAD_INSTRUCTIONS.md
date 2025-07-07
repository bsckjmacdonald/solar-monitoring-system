# File Upload Instructions

Please upload your solar monitoring system files according to this structure. Create the directories as needed and place your files in the appropriate locations.

## Required Files to Upload

### 1. Core Python Scripts
Place in `src/` directory:
- **Main monitoring script** (suggested name: `main.py` or `monitor.py`)
- **Sensor reading module** (if separate from main script)
- **Data storage/management module** (if separate)
- **Google Drive backup module** (if separate)

### 2. Web Interface Files
Place in `src/web_interface/` directory:
- **Web server script** (Flask/Django app or simple HTTP server)
- **HTML templates** → `src/web_interface/templates/`
- **CSS stylesheets** → `src/web_interface/static/css/`
- **JavaScript files** → `src/web_interface/static/js/`
- **Images/icons** → `src/web_interface/static/images/`

### 3. Configuration Files
Place in `config/` directory:
- **Main configuration file** (remove any passwords/API keys)
- **Sensor configuration/mapping**
- **Any other config files**

### 4. Dependencies & Setup
- **requirements.txt** (root directory) - List all Python packages needed
- **setup.py or install script** (if you have one)

### 5. Documentation (Optional but Helpful)
Place in `docs/` directory:
- **Installation instructions**
- **Configuration guide** 
- **Usage notes**
- **Troubleshooting tips**

## Security Note
⚠️ **Important**: Do not upload files containing:
- Google Drive API credentials
- Passwords or API keys
- Personal data or sensor readings

Instead, create template/example config files showing the required structure.

## Upload Methods

### Option 1: GitHub Web Interface
1. Navigate to https://github.com/bsckjmacdonald/solar-monitoring-system
2. Click "Add file" → "Upload files"
3. Drag and drop your files or click "choose your files"
4. Create folders by typing `foldername/filename.py` in the name field
5. Commit the changes

### Option 2: Git Command Line (if you have git installed)
```bash
git clone https://github.com/bsckjmacdonald/solar-monitoring-system.git
cd solar-monitoring-system
# Copy your files into the appropriate directories
git add .
git commit -m "Upload solar monitoring system code"
git push
```

## After Upload
Once you've uploaded the files, let me know and I'll:
1. Review the code structure and functionality
2. Analyze the system for potential improvements
3. Provide specific recommendations for optimization
4. Suggest additional features or enhancements
5. Help implement any improvements you'd like to make

## Questions?
If you're unsure about where to place any files or need help with the upload process, just ask!
