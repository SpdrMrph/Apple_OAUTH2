"""
Конфигурация для Apple OAuth2
Все значения нужно получить из Apple Developer Console

Поддерживает:
- Локальная разработка (значения по умолчанию в коде)
- Production через переменные окружения (Railway, Render, и др.)
"""
import os
from pydantic_settings import BaseSettings

class AppleOAuthConfig(BaseSettings):
    """
    Конфигурация Apple OAuth2
    
    Для локальной разработки: заполните значения ниже
    Для production: установите переменные окружения на хостинге
    
    Как получить эти значения - смотри APPLE_SETUP.md
    """
    
    # ===== ЗАПОЛНИТЕ ЭТИ КОНСТАНТЫ =====
    
    # Team ID - Идентификатор вашей команды разработчиков
    # Найти: Apple Developer > Membership > Team ID
    APPLE_TEAM_ID: str = "YOUR_TEAM_ID_HERE"
    
    # Client ID (Services ID) - Идентификатор сервиса
    # Создается: Apple Developer > Certificates, IDs & Profiles > Identifiers > Services IDs
    APPLE_CLIENT_ID: str = "com.yourcompany.yourapp.service"
    
    # Key ID - Идентификатор ключа для Sign in with Apple
    # Найти: Apple Developer > Keys > Ваш ключ > Key ID
    APPLE_KEY_ID: str = "YOUR_KEY_ID_HERE"
    
    # Private Key - Содержимое файла .p8 (закрытый ключ)
    # Скачивается один раз при создании ключа в Apple Developer
    # Вставьте весь текст из файла .p8, включая BEGIN/END строки
    APPLE_PRIVATE_KEY: str = """-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_CONTENT_HERE
-----END PRIVATE KEY-----"""
    
    # Redirect URI - URL куда Apple будет редиректить после авторизации
    # Должен совпадать с тем, что настроено в Apple Developer Console
    # Для production установите через переменные окружения!
    APPLE_REDIRECT_URI: str = "http://localhost:8000/auth/apple/callback"
    
    # ===== КОНСТАНТЫ APPLE (НЕ МЕНЯТЬ) =====
    APPLE_AUTH_URL: str = "https://appleid.apple.com/auth/authorize"
    APPLE_TOKEN_URL: str = "https://appleid.apple.com/auth/token"
    APPLE_PUBLIC_KEY_URL: str = "https://appleid.apple.com/auth/keys"
    
    # ===== НАСТРОЙКИ ПРИЛОЖЕНИЯ =====
    # Для production установите через переменные окружения!
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Переменные окружения имеют приоритет над значениями по умолчанию
        env_file_encoding = 'utf-8'

# Создаем глобальный экземпляр конфигурации
config = AppleOAuthConfig()

# Автоматическое определение URL для Railway/Render/Heroku
# Эти платформы предоставляют переменную окружения с доменом
if os.getenv("RAILWAY_PUBLIC_DOMAIN"):
    # Railway
    domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
    config.BACKEND_URL = f"https://{domain}"
    if config.APPLE_REDIRECT_URI == "http://localhost:8000/auth/apple/callback":
        config.APPLE_REDIRECT_URI = f"https://{domain}/auth/apple/callback"
elif os.getenv("RENDER_EXTERNAL_URL"):
    # Render
    config.BACKEND_URL = os.getenv("RENDER_EXTERNAL_URL")
    if config.APPLE_REDIRECT_URI == "http://localhost:8000/auth/apple/callback":
        config.APPLE_REDIRECT_URI = f"{config.BACKEND_URL}/auth/apple/callback"


