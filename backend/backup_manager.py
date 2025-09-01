#!/usr/bin/env python3
"""
Database Backup and Restore Manager
Handles automated daily backups and restoration capabilities
"""

import os
import subprocess
import datetime
import json
import gzip
import shutil
from pathlib import Path


class BackupManager:
    def __init__(self):
        self.backup_dir = Path('/app/backups')
        self.backup_dir.mkdir(exist_ok=True)
        
        # Database configuration
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'postgres'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'name': os.getenv('POSTGRES_DB', 'sistema'),
        }
        
    def create_backup(self):
        """Create a compressed backup of the database"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_{self.db_config['name']}_{timestamp}.sql.gz"
        backup_path = self.backup_dir / backup_filename
        
        # Set environment variable for password
        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_config['password']
        
        # Build pg_dump command
        cmd = [
            'pg_dump',
            '-h', self.db_config['host'],
            '-p', self.db_config['port'],
            '-U', self.db_config['user'],
            '-d', self.db_config['name'],
            '--verbose',
            '--clean',
            '--if-exists'
        ]
        
        try:
            # Create backup and compress
            with gzip.open(backup_path, 'wb') as backup_file:
                result = subprocess.run(
                    cmd,
                    env=env,
                    stdout=backup_file,
                    stderr=subprocess.PIPE,
                    check=True
                )
            
            # Create metadata file
            metadata = {
                'timestamp': timestamp,
                'database': self.db_config['name'],
                'filename': backup_filename,
                'size': backup_path.stat().st_size
            }
            
            metadata_path = backup_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Clean old backups (keep last 7 days)
            self.clean_old_backups()
            
            return {
                'success': True,
                'backup_path': str(backup_path),
                'metadata': metadata
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr.decode() if e.stderr else str(e)
            }
    
    def restore_backup(self, backup_filename):
        """Restore database from backup file"""
        backup_path = self.backup_dir / backup_filename
        
        if not backup_path.exists():
            return {
                'success': False,
                'error': f'Backup file not found: {backup_filename}'
            }
        
        # Set environment variable for password
        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_config['password']
        
        try:
            # Drop and recreate database
            drop_cmd = [
                'dropdb',
                '-h', self.db_config['host'],
                '-p', self.db_config['port'],
                '-U', self.db_config['user'],
                '--force',
                self.db_config['name']
            ]
            
            create_cmd = [
                'createdb',
                '-h', self.db_config['host'],
                '-p', self.db_config['port'],
                '-U', self.db_config['user'],
                self.db_config['name']
            ]
            
            # Execute drop and create
            subprocess.run(drop_cmd, env=env, check=True)
            subprocess.run(create_cmd, env=env, check=True)
            
            # Restore from backup
            restore_cmd = [
                'psql',
                '-h', self.db_config['host'],
                '-p', self.db_config['port'],
                '-U', self.db_config['user'],
                '-d', self.db_config['name'],
                '-f', '-'  # Read from stdin
            ]
            
            # Decompress and restore
            if backup_path.suffix == '.gz':
                with gzip.open(backup_path, 'rb') as backup_file:
                    subprocess.run(
                        restore_cmd,
                        env=env,
                        input=backup_file.read(),
                        check=True
                    )
            else:
                with open(backup_path, 'rb') as backup_file:
                    subprocess.run(
                        restore_cmd,
                        env=env,
                        input=backup_file.read(),
                        check=True
                    )
            
            return {
                'success': True,
                'message': f'Database restored successfully from {backup_filename}'
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr.decode() if e.stderr else str(e)
            }
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        for file in self.backup_dir.glob('backup_*.sql.gz'):
            metadata_file = file.with_suffix('.json')
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                backups.append(metadata)
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def clean_old_backups(self, days_to_keep=7):
        """Clean backups older than specified days"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
        
        for file in self.backup_dir.glob('backup_*.sql.gz'):
            file_date = datetime.datetime.fromtimestamp(file.stat().st_mtime)
            if file_date < cutoff_date:
                file.unlink()
                metadata_file = file.with_suffix('.json')
                if metadata_file.exists():
                    metadata_file.unlink()


def create_daily_backup():
    """Celery task to create daily backup"""
    from celery import shared_task
    
    @shared_task
    def backup_database():
        manager = BackupManager()
        result = manager.create_backup()
        
        if result['success']:
            print(f"Daily backup created: {result['backup_path']}")
        else:
            print(f"Backup failed: {result['error']}")
            
        return result
    
    return backup_database


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Backup and Restore Manager')
    parser.add_argument('action', choices=['backup', 'restore', 'list'], help='Action to perform')
    parser.add_argument('--filename', help='Backup filename for restore')
    
    args = parser.parse_args()
    
    manager = BackupManager()
    
    if args.action == 'backup':
        result = manager.create_backup()
        print(json.dumps(result, indent=2))
    elif args.action == 'restore':
        if not args.filename:
            print("Error: --filename required for restore")
            exit(1)
        result = manager.restore_backup(args.filename)
        print(json.dumps(result, indent=2))
    elif args.action == 'list':
        backups = manager.list_backups()
        print(json.dumps(backups, indent=2))