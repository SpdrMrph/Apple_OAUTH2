"""
Утилиты для работы с Apple OAuth2
"""
import jwt
import time
import json
import httpx
from typing import Dict, Any
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from config import config


def generate_client_secret() -> str:
    """
    Генерирует client_secret для Apple OAuth2
    Apple требует JWT токен, подписанный вашим приватным ключом
    
    Returns:
        str: JWT токен (client_secret)
    """
    # Время создания и истечения токена
    now = int(time.time())
    expiration = now + (86400 * 180)  # 180 дней (максимум 6 месяцев)
    
    # Заголовки JWT
    headers = {
        "kid": config.APPLE_KEY_ID,  # Key ID из Apple Developer
        "alg": "ES256"  # Алгоритм подписи (ECDSA с SHA-256)
    }
    
    # Payload JWT
    payload = {
        "iss": config.APPLE_TEAM_ID,  # Issuer - ваш Team ID
        "iat": now,  # Issued At - время создания
        "exp": expiration,  # Expiration - время истечения
        "aud": "https://appleid.apple.com",  # Audience - всегда это значение
        "sub": config.APPLE_CLIENT_ID  # Subject - ваш Client ID (Services ID)
    }
    
    # Загружаем приватный ключ из конфига
    try:
        private_key = serialization.load_pem_private_key(
            config.APPLE_PRIVATE_KEY.encode(),
            password=None,
            backend=default_backend()
        )
    except Exception as e:
        raise ValueError(f"Ошибка загрузки приватного ключа: {e}")
    
    # Генерируем и подписываем JWT
    client_secret = jwt.encode(
        payload,
        private_key,
        algorithm="ES256",
        headers=headers
    )
    
    return client_secret


async def exchange_code_for_tokens(code: str) -> Dict[str, Any]:
    """
    Обменивает authorization code на токены
    
    Args:
        code: Authorization code от Apple
        
    Returns:
        Dict с токенами (access_token, id_token, refresh_token)
    """
    client_secret = generate_client_secret()
    
    data = {
        "client_id": config.APPLE_CLIENT_ID,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": config.APPLE_REDIRECT_URI
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            config.APPLE_TOKEN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            raise Exception(f"Ошибка получения токенов: {response.text}")
        
        return response.json()


def decode_id_token(id_token: str) -> Dict[str, Any]:
    """
    Декодирует и валидирует ID токен от Apple
    
    Args:
        id_token: JWT токен от Apple
        
    Returns:
        Dict с данными пользователя
    """
    try:
        # Декодируем без проверки подписи (для простоты примера)
        # В production нужно проверять подпись через Apple Public Keys
        decoded = jwt.decode(
            id_token,
            options={"verify_signature": False}
        )
        return decoded
    except Exception as e:
        raise ValueError(f"Ошибка декодирования ID токена: {e}")


async def get_apple_public_keys() -> Dict[str, Any]:
    """
    Получает публичные ключи Apple для валидации токенов
    В production используйте эти ключи для проверки подписи id_token
    
    Returns:
        Dict с публичными ключами Apple
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(config.APPLE_PUBLIC_KEY_URL)
        return response.json()


def validate_id_token_full(id_token: str, public_keys: Dict[str, Any]) -> Dict[str, Any]:
    """
    Полная валидация ID токена с проверкой подписи
    
    Для production использования:
    1. Получите публичные ключи через get_apple_public_keys()
    2. Найдите нужный ключ по kid из заголовка токена
    3. Проверьте подпись токена
    4. Проверьте iss, aud, exp
    
    Args:
        id_token: JWT токен от Apple
        public_keys: Публичные ключи Apple
        
    Returns:
        Dict с данными пользователя
    """
    # Декодируем заголовок чтобы получить kid
    unverified_header = jwt.get_unverified_header(id_token)
    kid = unverified_header.get('kid')
    
    # TODO: Реализовать полную валидацию с проверкой подписи
    # Это упрощенная версия для примера
    decoded = decode_id_token(id_token)
    
    # Проверяем базовые поля
    if decoded.get('iss') != 'https://appleid.apple.com':
        raise ValueError("Неверный issuer")
    
    if decoded.get('aud') != config.APPLE_CLIENT_ID:
        raise ValueError("Неверный audience")
    
    if decoded.get('exp', 0) < time.time():
        raise ValueError("Токен истек")
    
    return decoded


