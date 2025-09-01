#!/bin/bash

# Database Restore Script
# This script restores the database from a backup file

set -e

BACKUP_DIR="/app/backups"

# Function to display usage
usage() {
    echo "Usage: $0 <backup_filename>"
    echo "Available backups:"
    ls -la "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
}

# Check if backup filename is provided
if [ $# -ne 1 ]; then
    usage
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_DIR/$BACKUP_FILE"
    usage
fi

echo "Restoring database from backup..."
echo "Backup file: $BACKUP_FILE"
echo "Database: ${POSTGRES_DB:-sistema}"

# Confirm restoration
read -p "This will replace the current database. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restoration cancelled"
    exit 0
fi

# Run restore using Python script
cd /app
python backup_manager.py restore "$BACKUP_FILE"

echo "Database restored successfully from $BACKUP_FILE"

# Restart services to ensure clean state
echo "Restarting services..."
if [ -f /.dockerenv ]; then
    echo "Please restart the container to ensure all services use the restored database"
else
    echo "Run 'docker-compose restart backend' to restart the services"
fi