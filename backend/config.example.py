"""
ПРИМЕР заполненной конфигурации для Apple OAuth2
Скопируйте значения в config.py после получения ключей
"""
from pydantic_settings import BaseSettings

class AppleOAuthConfig(BaseSettings):
    """
    Пример правильно заполненной конфигурации
    """
    
    # ===== ПРИМЕР ЗАПОЛНЕННЫХ ЗНАЧЕНИЙ =====
    
    # Team ID - 10 символов, находится в Apple Developer > Membership
    APPLE_TEAM_ID: str = "AB12CD34EF"
    
    # Client ID (Services ID) - обычно в формате reverse domain
    APPLE_CLIENT_ID: str = "com.testmycompany.myapp.service"
    
    # Key ID - 10 символов, получаете при создании ключа
    APPLE_KEY_ID: str = "XY98ZW76VU"
    
    # Private Key - весь текст из .p8 файла
    # ВАЖНО: включите BEGIN/END строки!
    APPLE_PRIVATE_KEY: str = """-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg1234567890abcdef
1234567890abcdef1234567890abcdef1234567890aboAoGCCqGSM49AwEHoUQD
QgAE1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab
cdef1234567890abcdef1234567890abcdef1234567890abcdef==
-----END PRIVATE KEY-----"""
    
    # ===== ВАЖНО: После получения ngrok URL обновите эти значения! =====
    
    # Redirect URI - замените на ваш ngrok URL
    # Формат: https://ваш-ngrok-id.ngrok-free.app/auth/apple/callback
    APPLE_REDIRECT_URI: str = "https://abc123def456.ngrok-free.app/auth/apple/callback"
    
    # ===== КОНСТАНТЫ APPLE (НЕ МЕНЯТЬ) =====
    APPLE_AUTH_URL: str = "https://appleid.apple.com/auth/authorize"
    APPLE_TOKEN_URL: str = "https://appleid.apple.com/auth/token"
    APPLE_PUBLIC_KEY_URL: str = "https://appleid.apple.com/auth/keys"
    
    # ===== НАСТРОЙКИ ПРИЛОЖЕНИЯ =====
    # Обновите BACKEND_URL на ваш ngrok URL
    BACKEND_URL: str = "https://abc123def456.ngrok-free.app"
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Пример использования
config = AppleOAuthConfig()

