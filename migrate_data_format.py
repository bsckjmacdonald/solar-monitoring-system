#!/usr/bin/env python3
"""
Migration script to convert existing JSON data files to append-only JSONL format
This reduces SD card wear by eliminating the need to rewrite entire files
"""

import os
import json
import glob
import shutil
from datetime import datetime
from config import Config

def migrate_json_to_jsonl(json_file_path: str) -> str:
    """Convert a JSON file to JSONL format"""
    jsonl_file_path = json_file_path.replace('.json', '.jsonl')
    
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        with open(jsonl_file_path, 'w') as f:
            for reading in data:
                f.write(json.dumps(reading) + '\n')
        
        print(f"Migrated: {json_file_path} -> {jsonl_file_path}")
        return jsonl_file_path
        
    except Exception as e:
        print(f"Error migrating {json_file_path}: {e}")
        return None

def main():
    """Main migration function"""
    config = Config()
    
    if not os.path.exists(config.DATA_DIR):
        print(f"Data directory {config.DATA_DIR} does not exist")
        return
    
    json_files = glob.glob(os.path.join(config.DATA_DIR, f"{config.LOG_FILE_PREFIX}_*.json"))
    
    if not json_files:
        print("No JSON data files found to migrate")
        return
    
    print(f"Found {len(json_files)} JSON files to migrate")
    
    backup_dir = os.path.join(config.DATA_DIR, 'backup_json_files')
    os.makedirs(backup_dir, exist_ok=True)
    
    migrated_count = 0
    
    for json_file in json_files:
        jsonl_file = migrate_json_to_jsonl(json_file)
        
        if jsonl_file:
            backup_path = os.path.join(backup_dir, os.path.basename(json_file))
            shutil.move(json_file, backup_path)
            print(f"Backed up original: {json_file} -> {backup_path}")
            migrated_count += 1
    
    print(f"\nMigration complete!")
    print(f"- Migrated {migrated_count} files to JSONL format")
    print(f"- Original JSON files backed up to: {backup_dir}")
    print(f"- New JSONL files use append-only logging to reduce SD card wear")
    print(f"\nYou can safely delete the backup directory after verifying the migration worked correctly.")

if __name__ == "__main__":
    main()
