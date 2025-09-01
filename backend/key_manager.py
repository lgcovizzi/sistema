#!/usr/bin/env python3
"""
Key Management System for Django Application
Handles encryption keys, signing keys, and secret key generation with 2-year lifecycle
"""

import os
import json
import base64
import hashlib
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


class KeyManager:
    def __init__(self, keys_dir=None):
        self.keys_dir = keys_dir or os.path.join(os.path.dirname(__file__), 'keys')
        self.metadata_file = os.path.join(self.keys_dir, 'key_metadata.json')
        self.encryption_key_file = os.path.join(self.keys_dir, 'encryption.key')
        self.signing_key_file = os.path.join(self.keys_dir, 'signing.key')
        
    def generate_encryption_key(self):
        """Generate a new Fernet encryption key"""
        return Fernet.generate_key()
    
    def generate_signing_key(self):
        """Generate a new RSA signing key"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    
    def generate_secret_key(self, encryption_key):
        """Generate Django secret key from encryption key"""
        return base64.urlsafe_b64encode(encryption_key[:32]).decode()
    
    def calculate_hash(self, data):
        """Calculate SHA256 hash of data"""
        return hashlib.sha256(data).hexdigest()
    
    def check_key_validity(self):
        """Check if keys are still valid (not expired)"""
        if not os.path.exists(self.metadata_file):
            return False
            
        try:
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
            
            expires_at = datetime.fromisoformat(metadata['expires_at'].replace('Z', '+00:00'))
            return datetime.now().replace(tzinfo=expires_at.tzinfo) < expires_at
            
        except (json.JSONDecodeError, KeyError, ValueError):
            return False
    
    def verify_key_integrity(self):
        """Verify key files haven't been corrupted"""
        if not os.path.exists(self.metadata_file):
            return False
            
        try:
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Check encryption key
            if os.path.exists(self.encryption_key_file):
                with open(self.encryption_key_file, 'rb') as f:
                    encryption_key = f.read()
                if self.calculate_hash(encryption_key) != metadata.get('encryption_key_hash'):
                    return False
            
            # Check signing key
            if os.path.exists(self.signing_key_file):
                with open(self.signing_key_file, 'rb') as f:
                    signing_key = f.read()
                if self.calculate_hash(signing_key) != metadata.get('signing_key_hash'):
                    return False
            
            return True
            
        except (json.JSONDecodeError, KeyError, IOError):
            return False
    
    def generate_new_keys(self):
        """Generate new keys and save them with metadata"""
        os.makedirs(self.keys_dir, exist_ok=True)
        
        # Generate keys
        encryption_key = self.generate_encryption_key()
        signing_key = self.generate_signing_key()
        
        # Calculate hashes
        encryption_hash = self.calculate_hash(encryption_key)
        signing_hash = self.calculate_hash(signing_key)
        
        # Calculate expiration (2 years from now)
        created_at = datetime.now()
        expires_at = created_at + timedelta(days=730)
        
        # Save keys
        with open(self.encryption_key_file, 'wb') as f:
            f.write(encryption_key)
        
        with open(self.signing_key_file, 'wb') as f:
            f.write(signing_key)
        
        # Save metadata
        metadata = {
            'created_at': created_at.isoformat() + 'Z',
            'expires_at': expires_at.isoformat() + 'Z',
            'encryption_key_hash': encryption_hash,
            'signing_key_hash': signing_hash
        }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        # Set secure permissions
        os.chmod(self.encryption_key_file, 0o600)
        os.chmod(self.signing_key_file, 0o600)
        os.chmod(self.metadata_file, 0o600)
        
        return {
            'encryption_key': encryption_key,
            'signing_key': signing_key,
            'secret_key': self.generate_secret_key(encryption_key),
            'expires_at': expires_at
        }
    
    def get_keys(self):
        """Get current keys, generate new ones if needed"""
        if not self.check_key_validity() or not self.verify_key_integrity():
            return self.generate_new_keys()
        
        # Load existing keys
        with open(self.encryption_key_file, 'rb') as f:
            encryption_key = f.read()
        
        with open(self.signing_key_file, 'rb') as f:
            signing_key = f.read()
        
        with open(self.metadata_file, 'r') as f:
            metadata = json.load(f)
        
        return {
            'encryption_key': encryption_key,
            'signing_key': signing_key,
            'secret_key': self.generate_secret_key(encryption_key),
            'expires_at': datetime.fromisoformat(metadata['expires_at'].replace('Z', '+00:00'))
        }


def initialize_keys():
    """Initialize keys when Django starts"""
    key_manager = KeyManager()
    keys = key_manager.get_keys()
    
    # Set Django secret key
    os.environ.setdefault('DJANGO_SECRET_KEY', keys['secret_key'])
    
    return keys


if __name__ == '__main__':
    keys = initialize_keys()
    print("Keys initialized successfully")
    print(f"Secret key: {keys['secret_key'][:16]}...")
    print(f"Keys expire at: {keys['expires_at']}")