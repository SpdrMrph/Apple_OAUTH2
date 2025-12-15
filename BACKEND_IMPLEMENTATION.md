# 🔧 Backend Implementation Guide

Документация по реализации backend для Apple OAuth2.

---

## 📁 Структура backend

```
backend/
├── main.py           # FastAPI приложение с endpoints
├── config.py         # Конфигурация и переменные окружения
├── utils.py          # Утилиты: генерация JWT, обмен токенов
├── requirements.txt  # Python зависимости
└── README.md         # Краткое описание
```

---

## 🔄 OAuth2 Flow

### Диаграмма авторизации

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Frontend │     │ Backend  │     │  Apple   │     │  Apple   │
│          │     │          │     │   Auth   │     │  Token   │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ 1. Click       │                │                │
     │ "Sign in"      │                │                │
     │───────────────>│                │                │
     │                │                │                │
     │ 2. Return      │                │                │
     │ auth_url       │                │                │
     │<───────────────│                │                │
     │                │                │                │
     │ 3. Redirect to Apple            │                │
     │────────────────────────────────>│                │
     │                │                │                │
     │ 4. User logs in with Apple ID   │                │
     │                │                │                │
     │ 5. Apple redirects with code    │                │
     │                │<───────────────│                │
     │                │                │                │
     │                │ 6. Exchange code for tokens     │
     │                │───────────────────────────────>│
     │                │                │                │
     │                │ 7. Return tokens (id_token)    │
     │                │<───────────────────────────────│
     │                │                │                │
     │ 8. Redirect with session_id     │                │
     │<───────────────│                │                │
     │                │                │                │
     │ 9. Get user data                │                │
     │───────────────>│                │                │
     │                │                │                │
     │ 10. Return user info            │                │
     │<───────────────│                │                │
     │                │                │                │
```

---

## 📋 Endpoints

### 1. `GET /auth/apple/login`

**Назначение:** Инициирует OAuth flow

**Логика:**
1. Генерирует уникальный `state` токен (защита от CSRF)
2. Сохраняет `state` в хранилище
3. Формирует URL для Apple с параметрами:
   - `client_id` - ваш Services ID
   - `redirect_uri` - callback URL
   - `response_type` = "code"
   - `response_mode` = "form_post"
   - `state` - CSRF токен
   - `scope` = "name email"
4. Возвращает URL клиенту

**Код:**
```python
@app.get("/auth/apple/login")
async def apple_login():
    state = secrets.token_urlsafe(32)
    state_storage[state] = True
    
    params = {
        "client_id": config.APPLE_CLIENT_ID,
        "redirect_uri": config.APPLE_REDIRECT_URI,
        "response_type": "code",
        "response_mode": "form_post",
        "state": state,
        "scope": "name email",
    }
    
    auth_url = f"{config.APPLE_AUTH_URL}?{urlencode(params)}"
    return {"auth_url": auth_url}
```

---

### 2. `POST /auth/apple/callback`

**Назначение:** Обрабатывает callback от Apple после авторизации

**Входные данные от Apple (form-data):**
- `code` - authorization code
- `state` - CSRF токен
- `user` - JSON с данными пользователя (только первый раз!)
- `error` - ошибка (если есть)

**Логика:**
1. Проверяет `state` (защита от CSRF)
2. Удаляет использованный `state`
3. Вызывает `exchange_code_for_tokens(code)`:
   - Генерирует `client_secret` (JWT)
   - Отправляет POST на `https://appleid.apple.com/auth/token`
   - Получает `access_token`, `id_token`, `refresh_token`
4. Декодирует `id_token` для получения данных пользователя
5. Создаёт сессию с уникальным `session_id`
6. Редиректит на frontend с `session_id`

**Код:**
```python
@app.post("/auth/apple/callback")
async def apple_callback(request: Request):
    form_data = await request.form()
    code = form_data.get("code")
    state = form_data.get("state")
    
    # Проверка state
    if state not in state_storage:
        raise HTTPException(400, "Invalid state")
    del state_storage[state]
    
    # Обмен кода на токены
    tokens = await exchange_code_for_tokens(code)
    
    # Декодирование id_token
    user_info = decode_id_token(tokens["id_token"])
    
    # Создание сессии
    session_id = secrets.token_urlsafe(32)
    user_sessions[session_id] = {
        "user_id": user_info["sub"],
        "email": user_info.get("email"),
        ...
    }
    
    return RedirectResponse(f"{FRONTEND_URL}/callback?session_id={session_id}")
```

---

### 3. `GET /auth/user`

**Назначение:** Возвращает данные пользователя

**Параметры:**
- `session_id` (query) - ID сессии

**Логика:**
1. Проверяет существование сессии
2. Возвращает данные пользователя (без токенов)

**Код:**
```python
@app.get("/auth/user")
async def get_user(session_id: str):
    if session_id not in user_sessions:
        raise HTTPException(401, "Invalid session")
    
    user = user_sessions[session_id]
    return {
        "user_id": user["user_id"],
        "email": user.get("email"),
        "email_verified": user.get("email_verified"),
        "is_private_email": user.get("is_private_email"),
    }
```

---

### 4. `POST /auth/logout`

**Назначение:** Удаляет сессию пользователя

**Параметры:**
- `session_id` (query) - ID сессии

**Логика:**
1. Удаляет сессию из хранилища

---

## 🔐 Генерация Client Secret (JWT)

Apple требует JWT токен в качестве `client_secret` для обмена кода на токены.

### Структура JWT

**Header:**
```json
{
  "kid": "APPLE_KEY_ID",
  "alg": "ES256"
}
```

**Payload:**
```json
{
  "iss": "APPLE_TEAM_ID",
  "iat": 1234567890,
  "exp": 1234567890,
  "aud": "https://appleid.apple.com",
  "sub": "APPLE_CLIENT_ID"
}
```

### Код генерации

```python
def generate_client_secret() -> str:
    now = int(time.time())
    expiration = now + (86400 * 180)  # 180 дней
    
    headers = {
        "kid": config.APPLE_KEY_ID,
        "alg": "ES256"
    }
    
    payload = {
        "iss": config.APPLE_TEAM_ID,
        "iat": now,
        "exp": expiration,
        "aud": "https://appleid.apple.com",
        "sub": config.APPLE_CLIENT_ID
    }
    
    # Загружаем приватный ключ
    private_key_str = config.APPLE_PRIVATE_KEY.replace('\\n', '\n')
    private_key = serialization.load_pem_private_key(
        private_key_str.encode(),
        password=None
    )
    
    # Генерируем JWT
    return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
```

---

## 🔄 Обмен кода на токены

### Запрос к Apple Token API

**URL:** `POST https://appleid.apple.com/auth/token`

**Content-Type:** `application/x-www-form-urlencoded`

**Параметры:**
| Параметр | Значение |
|----------|----------|
| `client_id` | Ваш Services ID |
| `client_secret` | JWT токен (см. выше) |
| `code` | Authorization code от Apple |
| `grant_type` | `authorization_code` |
| `redirect_uri` | Ваш callback URL |

### Ответ от Apple

```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "...",
  "id_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

### Код обмена

```python
async def exchange_code_for_tokens(code: str) -> Dict[str, Any]:
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
            "https://appleid.apple.com/auth/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()
```

---

## 🎫 Структура ID Token

ID Token от Apple - это JWT с данными пользователя.

### Claims в id_token

| Claim | Описание |
|-------|----------|
| `iss` | Issuer - всегда `https://appleid.apple.com` |
| `sub` | Subject - уникальный ID пользователя (стабильный) |
| `aud` | Audience - ваш client_id |
| `iat` | Issued At - время создания |
| `exp` | Expiration - время истечения |
| `email` | Email пользователя (может отсутствовать) |
| `email_verified` | Подтверждён ли email |
| `is_private_email` | Использует ли приватный relay email |
| `auth_time` | Время аутентификации |

### Пример декодированного id_token

```json
{
  "iss": "https://appleid.apple.com",
  "aud": "com.example.app.service",
  "exp": 1234567890,
  "iat": 1234567890,
  "sub": "001234.abcdef1234567890abcdef.1234",
  "email": "user@privaterelay.appleid.com",
  "email_verified": true,
  "is_private_email": true,
  "auth_time": 1234567890
}
```

---

## ⚙️ Конфигурация

### Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `APPLE_TEAM_ID` | ID команды разработчиков | `AB12CD34EF` |
| `APPLE_CLIENT_ID` | Services ID | `com.example.app.service` |
| `APPLE_KEY_ID` | ID ключа Sign in with Apple | `XY98ZW76VU` |
| `APPLE_PRIVATE_KEY` | Содержимое .p8 файла | `-----BEGIN PRIVATE KEY-----\n...` |
| `APPLE_REDIRECT_URI` | Callback URL | `https://example.com/auth/apple/callback` |
| `FRONTEND_URL` | URL фронтенда | `http://localhost:3000` |

### Пример config.py

```python
from pydantic_settings import BaseSettings

class AppleOAuthConfig(BaseSettings):
    APPLE_TEAM_ID: str = "YOUR_TEAM_ID"
    APPLE_CLIENT_ID: str = "com.example.app.service"
    APPLE_KEY_ID: str = "YOUR_KEY_ID"
    APPLE_PRIVATE_KEY: str = "-----BEGIN PRIVATE KEY-----..."
    APPLE_REDIRECT_URI: str = "http://localhost:8000/auth/apple/callback"
    
    APPLE_AUTH_URL: str = "https://appleid.apple.com/auth/authorize"
    APPLE_TOKEN_URL: str = "https://appleid.apple.com/auth/token"
    
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
```

---

## 🚀 Реализация на другом языке

### Основные шаги для любого языка:

1. **Endpoint `/auth/apple/login`:**
   - Сгенерировать random state
   - Сохранить state в хранилище
   - Сформировать URL с параметрами
   - Вернуть URL клиенту

2. **Endpoint `/auth/apple/callback`:**
   - Получить `code` и `state` из POST body
   - Проверить state
   - Сгенерировать JWT client_secret
   - POST запрос на `https://appleid.apple.com/auth/token`
   - Декодировать id_token
   - Создать сессию
   - Редирект на frontend

3. **Генерация JWT client_secret:**
   - Algorithm: ES256 (ECDSA with SHA-256)
   - Подписать приватным ключом .p8
   - Header: `{"kid": KEY_ID, "alg": "ES256"}`
   - Payload: `{"iss": TEAM_ID, "sub": CLIENT_ID, "aud": "https://appleid.apple.com", ...}`

### Библиотеки по языкам

| Язык | JWT | HTTP Client |
|------|-----|-------------|
| Python | `PyJWT`, `python-jose` | `httpx`, `requests` |
| Node.js | `jsonwebtoken` | `axios`, `node-fetch` |
| Go | `github.com/golang-jwt/jwt` | `net/http` |
| Java | `io.jsonwebtoken:jjwt` | `OkHttp`, `HttpClient` |
| PHP | `firebase/php-jwt` | `Guzzle` |
| Ruby | `jwt` gem | `faraday`, `httparty` |
| C# | `System.IdentityModel.Tokens.Jwt` | `HttpClient` |

---

## ⚠️ Важные особенности Apple OAuth

### 1. Email и имя только при первой авторизации

Apple передаёт `email` и `user` (имя) **только при первой авторизации** пользователя в вашем приложении.

При повторных входах эти данные **не передаются**!

**Решение:** Сохраняйте данные пользователя в БД при первой авторизации.

### 2. Private Email Relay

Пользователь может выбрать "Скрыть мой email". В этом случае:
- `email` будет вида `abc123@privaterelay.appleid.com`
- `is_private_email` = `true`

Письма на этот адрес пересылаются на реальный email пользователя.

### 3. User ID (sub) стабилен

`sub` claim в id_token - стабильный идентификатор пользователя для вашего приложения.

Используйте его как primary key для пользователя.

### 4. response_mode = form_post

Apple отправляет данные в callback как POST form-data, не как query параметры.

### 5. HTTPS обязателен в production

Apple не позволяет использовать HTTP redirect_uri в production.

---

## 📚 Ссылки

- [Sign in with Apple Documentation](https://developer.apple.com/documentation/sign_in_with_apple)
- [REST API Reference](https://developer.apple.com/documentation/sign_in_with_apple/sign_in_with_apple_rest_api)
- [Generate and Validate Tokens](https://developer.apple.com/documentation/sign_in_with_apple/generate_and_validate_tokens)
- [Authenticating Users with Sign in with Apple](https://developer.apple.com/documentation/sign_in_with_apple/sign_in_with_apple_js/authenticating_users_with_sign_in_with_apple)

