"""
FastAPI Backend для Apple OAuth2
Референсная реализация для интеграции Sign in with Apple
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlencode
import secrets
from typing import Dict, Any
from config import config
from utils import (
    generate_client_secret,
    exchange_code_for_tokens,
    decode_id_token,
    get_apple_public_keys
)

app = FastAPI(
    title="Apple OAuth2 Backend",
    description="Референсная реализация авторизации через Apple",
    version="1.0.0"
)

# CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Хранилище для state (в production используйте Redis)
state_storage: Dict[str, bool] = {}

# Хранилище для пользовательских сессий (в production используйте БД)
user_sessions: Dict[str, Dict[str, Any]] = {}


@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "message": "Apple OAuth2 Backend API",
        "version": "1.0.0",
        "endpoints": {
            "login": "/auth/apple/login",
            "callback": "/auth/apple/callback",
            "user": "/auth/user",
            "logout": "/auth/logout"
        }
    }


@app.get("/auth/apple/login")
async def apple_login():
    """
    Шаг 1: Инициация OAuth flow
    Редиректит пользователя на страницу авторизации Apple
    
    Returns:
        RedirectResponse на Apple authorization endpoint
    """
    # Генерируем уникальный state для защиты от CSRF
    state = secrets.token_urlsafe(32)
    state_storage[state] = True
    
    # Параметры для Apple OAuth
    params = {
        "client_id": config.APPLE_CLIENT_ID,
        "redirect_uri": config.APPLE_REDIRECT_URI,
        "response_type": "code",  # Authorization Code Flow
        "response_mode": "form_post",  # Apple отправит POST запрос
        "state": state,
        "scope": "name email",  # Запрашиваем имя и email
    }
    
    # Строим URL для редиректа
    auth_url = f"{config.APPLE_AUTH_URL}?{urlencode(params)}"
    
    return {
        "auth_url": auth_url,
        "message": "Перейдите по auth_url для авторизации"
    }


@app.post("/auth/apple/callback")
@app.get("/auth/apple/callback")
async def apple_callback(request: Request):
    """
    Шаг 2: Обработка callback от Apple
    Apple редиректит сюда после успешной авторизации
    
    Принимает:
        - code: Authorization code
        - state: CSRF токен
        - user: Данные пользователя (только при первой авторизации, в JSON)
        
    Returns:
        Редирект на фронтенд с session_id
    """
    # Apple может отправить POST или GET запрос
    if request.method == "POST":
        form_data = await request.form()
        code = form_data.get("code")
        state = form_data.get("state")
        user_data = form_data.get("user")  # JSON строка с данными (только в первый раз)
        error = form_data.get("error")
    else:
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        user_data = request.query_params.get("user")
        error = request.query_params.get("error")
    
    # Проверяем на ошибки
    if error:
        return RedirectResponse(
            url=f"{config.FRONTEND_URL}/callback?error={error}"
        )
    
    # Проверяем state (защита от CSRF)
    if not state or state not in state_storage:
        raise HTTPException(status_code=400, detail="Неверный state параметр")
    
    # Удаляем использованный state
    del state_storage[state]
    
    if not code:
        raise HTTPException(status_code=400, detail="Отсутствует authorization code")
    
    try:
        # Обмениваем code на токены
        tokens = await exchange_code_for_tokens(code)
        
        # Декодируем ID токен для получения данных пользователя
        id_token = tokens.get("id_token")
        if not id_token:
            raise HTTPException(status_code=400, detail="Отсутствует id_token")
        
        user_info = decode_id_token(id_token)
        
        # Создаем сессию для пользователя
        session_id = secrets.token_urlsafe(32)
        user_sessions[session_id] = {
            "user_id": user_info.get("sub"),  # Уникальный ID пользователя от Apple
            "email": user_info.get("email"),
            "email_verified": user_info.get("email_verified"),
            "is_private_email": user_info.get("is_private_email"),
            "tokens": tokens,
            "user_data": user_data  # Может быть None при повторных входах
        }
        
        # Редиректим на фронтенд с session_id
        redirect_url = f"{config.FRONTEND_URL}/callback?session_id={session_id}"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        print(f"Ошибка при обработке callback: {e}")
        return RedirectResponse(
            url=f"{config.FRONTEND_URL}/callback?error=authentication_failed"
        )


@app.get("/auth/user")
async def get_user(session_id: str):
    """
    Получение данных пользователя по session_id
    
    Args:
        session_id: ID сессии пользователя
        
    Returns:
        JSON с данными пользователя
    """
    if session_id not in user_sessions:
        raise HTTPException(status_code=401, detail="Неверная или истекшая сессия")
    
    user_data = user_sessions[session_id]
    
    return {
        "user_id": user_data.get("user_id"),
        "email": user_data.get("email"),
        "email_verified": user_data.get("email_verified"),
        "is_private_email": user_data.get("is_private_email"),
        # Не возвращаем токены в обычном запросе (безопасность)
    }


@app.post("/auth/logout")
async def logout(session_id: str):
    """
    Выход из системы (удаление сессии)
    
    Args:
        session_id: ID сессии пользователя
        
    Returns:
        Статус успешного выхода
    """
    if session_id in user_sessions:
        del user_sessions[session_id]
    
    return {"message": "Успешный выход из системы"}


@app.get("/auth/test-config")
async def test_config():
    """
    Тестовый endpoint для проверки конфигурации (без приватного ключа)
    Используйте для проверки что все константы заполнены
    """
    return {
        "team_id": config.APPLE_TEAM_ID,
        "client_id": config.APPLE_CLIENT_ID,
        "key_id": config.APPLE_KEY_ID,
        "redirect_uri": config.APPLE_REDIRECT_URI,
        "private_key_loaded": "YES" if config.APPLE_PRIVATE_KEY else "NO",
        "private_key_starts_with": config.APPLE_PRIVATE_KEY[:50] + "..." if config.APPLE_PRIVATE_KEY else "NOT_SET"
    }


@app.get("/auth/test-jwt")
async def test_jwt():
    """
    Тестовый endpoint для проверки генерации JWT client_secret
    """
    try:
        client_secret = generate_client_secret()
        return {
            "status": "success",
            "client_secret": client_secret,
            "message": "JWT успешно сгенерирован"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации JWT: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Запуск Apple OAuth2 Backend...")
    print(f"📍 Backend URL: {config.BACKEND_URL}")
    print(f"📍 Frontend URL: {config.FRONTEND_URL}")
    print(f"📍 Redirect URI: {config.APPLE_REDIRECT_URI}")
    print("\n⚠️  Не забудьте заполнить константы в backend/config.py")
    print("📖 Инструкция: см. APPLE_SETUP.md\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


