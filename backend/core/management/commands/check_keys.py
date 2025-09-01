import os
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Verifica e gera chaves de criptografia se necessário'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-new',
            action='store_true',
            help='Força a geração de novas chaves',
        )

    def handle(self, *args, **options):
        keys_dir = '/app/keys'
        encryption_key_path = os.path.join(keys_dir, 'encryption.key')
        signing_key_path = os.path.join(keys_dir, 'signing.key')
        metadata_path = os.path.join(keys_dir, 'key_metadata.json')
        
        # Garantir que o diretório existe
        os.makedirs(keys_dir, exist_ok=True)
        os.chmod(keys_dir, 0o700)

        force_new = options['force_new']
        
        # Verificar se precisamos gerar novas chaves
        need_new_keys = force_new
        
        if not force_new:
            # Verificar se as chaves existem e são válidas
            encryption_valid = self.validate_encryption_key(encryption_key_path)
            signing_valid = self.validate_signing_key(signing_key_path)
            metadata_valid = self.validate_metadata(metadata_path)
            
            if not (encryption_valid and signing_valid and metadata_valid):
                need_new_keys = True
                self.stdout.write(
                    self.style.WARNING('Chaves inválidas ou expiradas, gerando novas...')
                )
        
        if need_new_keys:
            self.generate_keys(encryption_key_path, signing_key_path, metadata_path)
        else:
            self.stdout.write(
                self.style.SUCCESS('Todas as chaves são válidas e dentro do período de validade')
            )

    def validate_encryption_key(self, path):
        if not os.path.exists(path):
            return False
        try:
            with open(path, 'rb') as f:
                key = f.read()
            Fernet(key)  # Testa se a chave é válida
            return True
        except Exception:
            return False

    def validate_signing_key(self, path):
        if not os.path.exists(path):
            return False
        try:
            with open(path, 'rb') as f:
                key_data = f.read()
            serialization.load_pem_private_key(key_data, password=None)
            return True
        except Exception:
            return False

    def validate_metadata(self, path):
        if not os.path.exists(path):
            return False
        try:
            with open(path, 'r') as f:
                metadata = json.load(f)
            
            created_at = datetime.fromisoformat(metadata['created_at'])
            expiry_date = created_at + timedelta(days=730)  # 2 anos
            
            if datetime.now() > expiry_date:
                self.stdout.write(
                    self.style.WARNING('Chaves expiraram, gerando novas...')
                )
                return False
            
            return True
        except Exception:
            return False

    def generate_keys(self, encryption_path, signing_path, metadata_path):
        self.stdout.write('🔐 Gerando novas chaves de criptografia...')
        
        # Gerar chave Fernet para criptografia
        encryption_key = Fernet.generate_key()
        with open(encryption_path, 'wb') as f:
            f.write(encryption_key)
        os.chmod(encryption_path, 0o600)
        
        # Gerar chave RSA para assinatura
        signing_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        with open(signing_path, 'wb') as f:
            f.write(
                signing_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
        os.chmod(signing_path, 0o600)
        
        # Gerar chave pública
        public_key = signing_key.public_key()
        public_key_path = signing_path.replace('.key', '_public.key')
        with open(public_key_path, 'wb') as f:
            f.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )
        
        # Criar metadata
        metadata = {
            'created_at': datetime.now().isoformat(),
            'encryption_key_size': len(encryption_key),
            'signing_key_size': 2048,
            'version': '1.0'
        }
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        os.chmod(metadata_path, 0o600)
        
        # Gerar SECRET_KEY para Django
        secret_key = encryption_key[:32].hex()
        secret_key_path = os.path.join(os.path.dirname(encryption_path), 'django_secret.key')
        with open(secret_key_path, 'w') as f:
            f.write(secret_key)
        os.chmod(secret_key_path, 0o600)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Chaves geradas com sucesso!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   📁 Localização: {os.path.dirname(encryption_path)}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   ⏰ Validade: 2 anos')
        )