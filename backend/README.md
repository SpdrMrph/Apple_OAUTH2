# Backend - Apple OAuth2 Server

FastAPI backend для авторизации через Apple OAuth2.

## Запуск

### Вариант 1: Через main.py
```bash
cd backend
python main.py
```

### Вариант 2: Через uvicorn
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Вариант 3: Из корня проекта
```bash
npm run dev:backend
```

## Endpoints

- `GET /` - Информация об API
- `GET /auth/apple/login` - Инициация OAuth flow
- `POST /auth/apple/callback` - Обработка callback от Apple
- `GET /auth/user?session_id=XXX` - Получение данных пользователя
- `POST /auth/logout?session_id=XXX` - Выход
- `GET /auth/test-config` - Тест конфигурации
- `GET /auth/test-jwt` - Тест генерации JWT

## Конфигурация

Заполните константы в `config.py`:
- `APPLE_TEAM_ID` - Team ID из Apple Developer
- `APPLE_CLIENT_ID` - Services ID
- `APPLE_KEY_ID` - Key ID
- `APPLE_PRIVATE_KEY` - Содержимое .p8 файла

Подробная инструкция в `../APPLE_SETUP.md`

## Документация API

После запуска откройте:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


