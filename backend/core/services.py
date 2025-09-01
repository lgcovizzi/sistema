import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import RefreshToken, BlacklistedToken

User = get_user_model()


class JWTService:
    @staticmethod
    def generate_tokens(user):
        """Gera access e refresh tokens para o usuário."""
        access_payload = {
            'user_id': str(user.id),
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(minutes=15),  # 15 minutos
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        refresh_payload = {
            'user_id': str(user.id),
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(days=366),  # 366 dias
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
        
        # Armazena o refresh token no banco
        RefreshToken.objects.create(
            user=user,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=366)
        )
        
        return {
            'access': access_token,
            'refresh': refresh_token
        }
    
    @staticmethod
    def verify_token(token, token_type='access'):
        """Verifica e decodifica um token JWT."""
        try:
            # Verifica se está na blacklist
            if BlacklistedToken.objects.filter(token=token).exists():
                return None, 'Token blacklisted'
            
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            if payload.get('type') != token_type:
                return None, f'Invalid token type, expected {token_type}'
            
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, 'Token expired'
        except jwt.InvalidTokenError:
            return None, 'Invalid token'
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """Gera um novo access token usando o refresh token."""
        payload, error = JWTService.verify_token(refresh_token, 'refresh')
        if error:
            return None, error
        
        # Verifica se o refresh token existe e não foi revogado
        try:
            refresh_obj = RefreshToken.objects.get(token=refresh_token, is_revoked=False)
            if refresh_obj.expires_at < datetime.utcnow():
                return None, 'Refresh token expired'
        except RefreshToken.DoesNotExist:
            return None, 'Invalid refresh token'
        
        # Gera novo access token
        user = User.objects.get(id=payload['user_id'])
        access_payload = {
            'user_id': str(user.id),
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(minutes=15),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
        return {'access': access_token}, None
    
    @staticmethod
    def blacklist_token(token):
        """Adiciona um token à blacklist."""
        payload, error = JWTService.verify_token(token)
        if error:
            return False, error
        
        BlacklistedToken.objects.create(
            token=token,
            expires_at=datetime.fromtimestamp(payload['exp'])
        )
        
        # Se for refresh token, marca como revogado
        if payload.get('type') == 'refresh':
            RefreshToken.objects.filter(token=token).update(is_revoked=True)
        
        return True, None
    
    @staticmethod
    def get_user_from_token(token):
        """Obtém o usuário a partir de um token válido."""
        payload, error = JWTService.verify_token(token)
        if error:
            return None, error
        
        try:
            user = User.objects.get(id=payload['user_id'])
            return user, None
        except User.DoesNotExist:
            return None, 'User not found'