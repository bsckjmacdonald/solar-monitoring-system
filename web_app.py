#!/usr/bin/env python3
"""
Web interface for solar water heater monitoring system
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from functools import wraps
from flask import Flask, render_template, jsonify, request, Response
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
config = Config()

def check_auth(username, password):
    """Check if username/password combination is valid"""
    return username == config.WEB_USERNAME and password == config.WEB_PASSWORD

def authenticate():
    """Send 401 response that enables basic auth"""
    return Response(
        'Authentication required\n'
        'Please provide valid credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Solar Monitor"'})

def requires_auth(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

class DataReader:
    """Read and process temperature data files"""
    
    def __init__(self):
        self.config = Config()
    
    def get_data_files(self) -> List[str]:
        """Get list of available data files"""
        data_dir = os.path.abspath(self.config.DATA_DIR)
        logger.info(f"Looking for data files in: {data_dir}")
        
        if not os.path.exists(data_dir):
            logger.warning(f"Data directory does not exist: {data_dir}")
            return []
        
        files = []
        for filename in os.listdir(data_dir):
            if filename.startswith(self.config.LOG_FILE_PREFIX) and (filename.endswith('.json') or filename.endswith('.jsonl')):
                files.append(os.path.join(data_dir, filename))
        
        logger.info(f"Found {len(files)} data files")
        return sorted(files)
    
    def read_data_file(self, filepath: str) -> List[Dict]:
        """Read data from a single file (supports both JSON and JSONL formats)"""
        try:
            with open(filepath, 'r') as f:
                if filepath.endswith('.jsonl'):
                    data = []
                    for line in f:
                        line = line.strip()
                        if line:
                            data.append(json.loads(line))
                    return data
                else:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
            return []
    
    def get_data_for_period(self, hours: int) -> List[Dict]:
        """Get temperature data for specified number of hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        all_data = []
        
        files = self.get_data_files()
        logger.info(f"Processing {len(files)} files for {hours}h period (cutoff: {cutoff_time})")
        
        for filepath in files:
            data = self.read_data_file(filepath)
            readings_added = 0
            for reading in data:
                try:
                    timestamp = datetime.fromisoformat(reading['timestamp'])
                    if timestamp >= cutoff_time:
                        all_data.append(reading)
                        readings_added += 1
                except Exception as e:
                    logger.error(f"Error parsing timestamp in {filepath}: {e}")
                    continue
            
            if readings_added > 0:
                logger.debug(f"Added {readings_added} readings from {os.path.basename(filepath)}")
        
        all_data.sort(key=lambda x: x['timestamp'])
        logger.info(f"Returning {len(all_data)} total readings for {hours}h period")
        return all_data
    
    def get_latest_reading(self) -> Optional[Dict]:
        """Get the most recent temperature reading"""
        files = self.get_data_files()
        if not files:
            return None
        
        latest_file = files[-1]
        data = self.read_data_file(latest_file)
        
        if data:
            return data[-1]  # Last reading in the file
        
        return None

data_reader = DataReader()

@app.route('/')
@requires_auth
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/current')
@requires_auth
def get_current_data():
    """Get current temperature readings"""
    latest = data_reader.get_latest_reading()
    if latest:
        return jsonify(latest)
    else:
        return jsonify({"error": "No data available"}), 404

@app.route('/api/data/<period>')
@requires_auth
def get_historical_data(period):
    """Get historical temperature data"""
    period_hours = {
        '24h': 24,
        '48h': 48,
        '1w': 168
    }
    
    if period not in period_hours:
        return jsonify({"error": "Invalid period"}), 400
    
    hours = period_hours[period]
    data = data_reader.get_data_for_period(hours)
    
    return jsonify({
        "period": period,
        "data": data,
        "count": len(data)
    })

@app.route('/api/summary/<period>')
@requires_auth
def get_summary_data(period):
    """Get summary statistics for a period"""
    period_hours = {
        '24h': 24,
        '48h': 48,
        '1w': 168
    }
    
    if period not in period_hours:
        return jsonify({"error": "Invalid period"}), 400
    
    hours = period_hours[period]
    data = data_reader.get_data_for_period(hours)
    
    if not data:
        return jsonify({"error": "No data available"}), 404
    
    summary = {}
    
    all_sensor_names = set()
    for reading in data:
        if 'sensors' in reading:
            all_sensor_names.update(reading['sensors'].keys())
    
    for sensor in all_sensor_names:
        temps = []
        for reading in data:
            if sensor in reading.get('sensors', {}) and reading['sensors'][sensor] is not None:
                temps.append(reading['sensors'][sensor])
        
        if temps:
            summary[sensor] = {
                'min': min(temps),
                'max': max(temps),
                'avg': sum(temps) / len(temps),
                'current': temps[-1] if temps else None
            }
    
    return jsonify({
        "period": period,
        "summary": summary,
        "data_points": len(data)
    })

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    
    debug_mode = config.WEB_DEBUG
    if debug_mode:
        logger.warning("DEBUG MODE ENABLED - This should not be used in production!")
    
    logger.info(f"Starting web server on {config.WEB_HOST}:{config.WEB_PORT}")
    logger.info(f"Authentication enabled - Username: {config.WEB_USERNAME}")
    
    app.run(
        host=config.WEB_HOST,
        port=config.WEB_PORT,
        debug=debug_mode
    )
