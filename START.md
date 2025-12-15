# ⚡ Быстрый старт проекта

## 🚀 Запуск в 3 терминалах

### Терминал 1️⃣ - Backend
```bash
venv\Scripts\activate
cd backend
python main.py
```

### Терминал 2️⃣ - ngrok
```bash
ngrok http 8000
```
**Скопируйте URL вида:** `https://abc123.ngrok-free.app`

### Терминал 3️⃣ - Frontend
```bash
npm run dev
```

---

## 📝 После получения ngrok URL

### 1. Обновите Apple Developer Console
- Перейдите: https://developer.apple.com/account
- Services ID → Configure
- **Domains**: `abc123.ngrok-free.app`
- **Return URLs**: `https://abc123.ngrok-free.app/auth/apple/callback`

### 2. Обновите backend/config.py
```python
APPLE_REDIRECT_URI: str = "https://abc123.ngrok-free.app/auth/apple/callback"
BACKEND_URL: str = "https://abc123.ngrok-free.app"
```

### 3. Обновите app/page.tsx
```typescript
const BACKEND_URL = 'https://abc123.ngrok-free.app';
```

### 4. Перезапустите backend (Терминал 1)
`Ctrl+C` → `python main.py`

---

## ✅ Готово!

Откройте: http://localhost:3000

---

## 📖 Подробная инструкция

См. **NGROK_SETUP.md**

