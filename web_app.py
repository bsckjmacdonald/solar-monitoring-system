#!/usr/bin/env python3
"""
Web interface for solar water heater monitoring system
"""

import os
import json
import csv as csv_module
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

@app.route('/spectrogram')
@requires_auth
def spectrogram_page():
    """Acoustic spectrogram viewer page"""
    return render_template('spectrogram.html')


@app.route('/api/acoustic/files')
@requires_auth
def list_acoustic_files():
    """List available acoustic CSV files"""
    acoustic_dir = os.path.join(os.path.abspath(config.DATA_DIR), 'acoustic')
    os.makedirs(acoustic_dir, exist_ok=True)
    files = []
    for fname in sorted(os.listdir(acoustic_dir)):
        if fname.endswith('.csv'):
            fpath = os.path.join(acoustic_dir, fname)
            files.append({'name': fname, 'size': os.path.getsize(fpath)})
    return jsonify({'files': files})


@app.route('/api/acoustic/data/<path:filename>')
@requires_auth
def get_acoustic_data(filename):
    """Return raw samples from an acoustic CSV file"""
    # Prevent path traversal
    if '..' in filename or filename.startswith('/'):
        return jsonify({'error': 'Invalid filename'}), 400

    acoustic_dir = os.path.join(os.path.abspath(config.DATA_DIR), 'acoustic')
    filepath = os.path.join(acoustic_dir, filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    samples = []
    x_samples, y_samples, z_samples, timestamps = [], [], [], []
    sample_rate = None
    col_map = {}

    try:
        with open(filepath, 'r') as f:
            header_parsed = False
            is_multi = False
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Metadata comments: # sample_rate=8000 or # fs=8000
                if line.startswith('#'):
                    m = next(
                        (p for p in line[1:].split() if '=' in p and
                         p.split('=')[0].strip().lower() in ('sample_rate', 'fs', 'samplerate')),
                        None)
                    if m:
                        try:
                            sample_rate = int(m.split('=')[1])
                        except ValueError:
                            pass
                    continue
                cols = [c.strip() for c in line.split(',')]
                if not header_parsed:
                    header_parsed = True
                    try:
                        float(cols[0])
                        # First column is numeric — no header, use last column fallback
                    except ValueError:
                        # Header row — map column names
                        for i, name in enumerate(cols):
                            nl = name.lower()
                            if nl in ('t_s', 't', 'time', 'timestamp'):
                                col_map['t'] = i
                            elif nl in ('x_g', 'x', 'ax', 'accel_x', 'acc_x'):
                                col_map['x'] = i
                            elif nl in ('y_g', 'y', 'ay', 'accel_y', 'acc_y'):
                                col_map['y'] = i
                            elif nl in ('z_g', 'z', 'az', 'accel_z', 'acc_z'):
                                col_map['z'] = i
                        is_multi = ('x' in col_map and 'y' in col_map and 'z' in col_map)
                        continue
                try:
                    if is_multi:
                        x_samples.append(float(cols[col_map['x']]))
                        y_samples.append(float(cols[col_map['y']]))
                        z_samples.append(float(cols[col_map['z']]))
                        if 't' in col_map and col_map['t'] < len(cols):
                            timestamps.append(float(cols[col_map['t']]))
                    else:
                        samples.append(float(cols[-1]))
                except (ValueError, IndexError):
                    pass
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Derive sample rate from timestamps when not in metadata
    if not sample_rate and len(timestamps) >= 2:
        dt = (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1)
        if dt > 0:
            sample_rate = round(1.0 / dt)

    if x_samples:
        return jsonify({
            'filename': filename,
            'axes': {'x': x_samples, 'y': y_samples, 'z': z_samples},
            'num_samples': len(x_samples),
            'sample_rate': sample_rate,
        })

    return jsonify({
        'filename': filename,
        'samples': samples,
        'num_samples': len(samples),
        'sample_rate': sample_rate,
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
