#!/usr/bin/env python3
"""
Web interface for solar water heater monitoring system
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from flask import Flask, render_template, jsonify, request
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
config = Config()

class DataReader:
    """Read and process temperature data files"""
    
    def __init__(self):
        self.config = Config()
    
    def get_data_files(self) -> List[str]:
        """Get list of available data files"""
        if not os.path.exists(self.config.DATA_DIR):
            return []
        
        files = []
        for filename in os.listdir(self.config.DATA_DIR):
            if filename.startswith(self.config.LOG_FILE_PREFIX) and filename.endswith('.json'):
                files.append(os.path.join(self.config.DATA_DIR, filename))
        
        return sorted(files)
    
    def read_data_file(self, filepath: str) -> List[Dict]:
        """Read data from a single file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
            return []
    
    def get_data_for_period(self, hours: int) -> List[Dict]:
        """Get temperature data for specified number of hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        all_data = []
        
        files = self.get_data_files()
        for filepath in files:
            data = self.read_data_file(filepath)
            for reading in data:
                try:
                    timestamp = datetime.fromisoformat(reading['timestamp'])
                    if timestamp >= cutoff_time:
                        all_data.append(reading)
                except Exception as e:
                    logger.error(f"Error parsing timestamp: {e}")
                    continue
        
        all_data.sort(key=lambda x: x['timestamp'])
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
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/current')
def get_current_data():
    """Get current temperature readings"""
    latest = data_reader.get_latest_reading()
    if latest:
        return jsonify(latest)
    else:
        return jsonify({"error": "No data available"}), 404

@app.route('/api/data/<period>')
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
    
    app.run(
        host=config.WEB_HOST,
        port=config.WEB_PORT,
        debug=True
    )
