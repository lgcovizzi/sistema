"""
Celery tasks for the Django application
Includes backup, health check, and maintenance tasks
"""

import os
import json
import logging
from datetime import datetime, timedelta
from django.core.management import call_command
from django.db import connection
from django.core.cache import cache
from celery import shared_task

from backup_manager import BackupManager
from key_manager import KeyManager

logger = logging.getLogger(__name__)


@shared_task
def daily_backup():
    """Create daily database backup"""
    try:
        logger.info("Starting daily backup task")
        
        manager = BackupManager()
        result = manager.create_backup()
        
        if result['success']:
            logger.info(f"Daily backup completed: {result['backup_path']}")
            return {
                'status': 'success',
                'backup_path': result['backup_path'],
                'timestamp': datetime.now().isoformat()
            }
        else:
            logger.error(f"Daily backup failed: {result['error']}")
            return {
                'status': 'error',
                'error': result['error'],
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Unexpected error in daily backup: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@shared_task
def cleanup_backups():
    """Clean up old backup files"""
    try:
        logger.info("Starting backup cleanup task")
        
        manager = BackupManager()
        manager.clean_old_backups(days_to_keep=7)
        
        logger.info("Backup cleanup completed")
        return {
            'status': 'success',
            'message': 'Old backups cleaned up',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in backup cleanup: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@shared_task
def health_check():
    """Comprehensive health check of the system"""
    try:
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'database': check_database_health(),
            'redis': check_redis_health(),
            'disk_space': check_disk_space(),
            'memory': check_memory_usage(),
            'overall': 'healthy'
        }
        
        # Check if any component is unhealthy
        for component, status in health_status.items():
            if isinstance(status, dict) and status.get('status') == 'unhealthy':
                health_status['overall'] = 'unhealthy'
                break
        
        # Cache the health status for 5 minutes
        cache.set('health_status', health_status, 300)
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def check_database_health():
    """Check database connectivity and performance"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Check database size
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_database_size(current_database())")
            db_size = cursor.fetchone()[0]
        
        return {
            'status': 'healthy',
            'response_time': 'ok',
            'database_size': db_size
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


def check_redis_health():
    """Check Redis connectivity"""
    try:
        cache.set('health_check', 'ok', 10)
        value = cache.get('health_check')
        
        if value == 'ok':
            return {'status': 'healthy'}
        else:
            return {'status': 'unhealthy', 'error': 'Redis read/write failed'}
            
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


def check_disk_space():
    """Check disk space usage"""
    try:
        import shutil
        total, used, free = shutil.disk_usage('/')
        usage_percent = (used / total) * 100
        
        return {
            'status': 'healthy' if usage_percent < 90 else 'warning',
            'total_gb': total // (1024**3),
            'used_gb': used // (1024**3),
            'free_gb': free // (1024**3),
            'usage_percent': round(usage_percent, 2)
        }
        
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


def check_memory_usage():
    """Check memory usage"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        
        return {
            'status': 'healthy' if memory.percent < 90 else 'warning',
            'total_gb': round(memory.total / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'usage_percent': memory.percent
        }
        
    except ImportError:
        return {'status': 'unknown', 'error': 'psutil not available'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


@shared_task
def check_key_rotation():
    """Check if keys need rotation and generate new ones if necessary"""
    try:
        manager = KeyManager()
        
        if not manager.check_key_validity() or not manager.verify_key_integrity():
            logger.warning("Keys are invalid or corrupted, generating new ones...")
            keys = manager.generate_new_keys()
            
            return {
                'status': 'keys_regenerated',
                'expires_at': keys['expires_at'].isoformat(),
                'timestamp': datetime.now().isoformat()
            }
        else:
            keys = manager.get_keys()
            days_until_expiry = (keys['expires_at'] - datetime.now()).days
            
            if days_until_expiry <= 30:
                logger.warning(f"Keys will expire in {days_until_expiry} days")
                return {
                    'status': 'expiring_soon',
                    'days_until_expiry': days_until_expiry,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'valid',
                    'days_until_expiry': days_until_expiry,
                    'timestamp': datetime.now().isoformat()
                }
                
    except Exception as e:
        logger.error(f"Error in key rotation check: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@shared_task
def send_test_email():
    """Send a test email to verify email configuration"""
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        send_mail(
            subject='Test Email - Sistema Django',
            message='This is a test email from the Django application.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMINS[0][1] if settings.ADMINS else 'admin@example.com'],
            fail_silently=False,
        )
        
        return {
            'status': 'success',
            'message': 'Test email sent successfully',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@shared_task
def clear_expired_sessions():
    """Clear expired Django sessions"""
    try:
        call_command('clearsessions')
        logger.info("Expired sessions cleared")
        
        return {
            'status': 'success',
            'message': 'Expired sessions cleared',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clearing sessions: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }