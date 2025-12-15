FROM python:3.12-slim

WORKDIR /app/backend

# Копируем requirements и устанавливаем зависимости
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь backend код
COPY backend/ .

# Открываем порт
EXPOSE 8000

# Запускаем uvicorn
CMD uvicorn main:app --host 0.0.0.0 --port $PORT

