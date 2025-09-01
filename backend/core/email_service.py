import redis
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

class EmailRateLimiter:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=1,  # DB separado para rate limiting
            decode_responses=True
        )
    
    def can_send_email(self, email_type, identifier, max_attempts=3, window_hours=1):
        """Verifica se pode enviar email baseado no rate limiting."""
        key = f"email_rate_limit:{email_type}:{identifier}"
        current_attempts = self.redis_client.get(key)
        
        if current_attempts is None:
            return True
        
        return int(current_attempts) < max_attempts
    
    def record_email_attempt(self, email_type, identifier, window_hours=1):
        """Registra uma tentativa de envio de email."""
        key = f"email_rate_limit:{email_type}:{identifier}"
        self.redis_client.incr(key)
        self.redis_client.expire(key, window_hours * 3600)
    
    def get_remaining_time(self, email_type, identifier):
        """Retorna o tempo restante para poder enviar novo email."""
        key = f"email_rate_limit:{email_type}:{identifier}"
        ttl = self.redis_client.ttl(key)
        return max(0, ttl)


class EmailService:
    def __init__(self):
        self.rate_limiter = EmailRateLimiter()
    
    def send_verification_email(self, user, verification_token):
        """Envia email de verificação com rate limiting."""
        if not self.rate_limiter.can_send_email('verification', user.email):
            remaining_time = self.rate_limiter.get_remaining_time('verification', user.email)
            raise Exception(f"Muitas tentativas. Tente novamente em {remaining_time} segundos.")
        
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token}"
        
        subject = "Verifique seu email - Sistema"
        html_message = render_to_string('emails/verification.html', {
            'user': user,
            'verification_url': verification_url,
            'expires_in': 24  # horas
        })
        
        try:
            send_mail(
                subject=subject,
                message="",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            self.rate_limiter.record_email_attempt('verification', user.email)
            logger.info(f"Email de verificação enviado para {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de verificação: {str(e)}")
            raise e
    
    def send_password_reset_email(self, user, reset_token):
        """Envia email de recuperação de senha com rate limiting."""
        if not self.rate_limiter.can_send_email('password_reset', user.email):
            remaining_time = self.rate_limiter.get_remaining_time('password_reset', user.email)
            raise Exception(f"Muitas tentativas. Tente novamente em {remaining_time} segundos.")
        
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token}"
        
        subject = "Recuperação de senha - Sistema"
        html_message = render_to_string('emails/password_reset.html', {
            'user': user,
            'reset_url': reset_url,
            'expires_in': 1  # hora
        })
        
        try:
            send_mail(
                subject=subject,
                message="",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            self.rate_limiter.record_email_attempt('password_reset', user.email)
            logger.info(f"Email de recuperação enviado para {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de recuperação: {str(e)}")
            raise e
    
    def send_welcome_email(self, user):
        """Envia email de boas-vindas após verificação."""
        subject = "Bem-vindo ao Sistema!"
        html_message = render_to_string('emails/welcome.html', {
            'user': user
        })
        
        try:
            send_mail(
                subject=subject,
                message="",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Email de boas-vindas enviado para {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de boas-vindas: {str(e)}")
            raise e