FROM python:3.12-slim

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Копируем весь backend код
COPY backend/ backend/

# Открываем порт
EXPOSE 8000

# Запускаем uvicorn
CMD cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT

