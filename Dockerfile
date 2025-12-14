# Базовый образ
FROM python:3.11-slim

# Переменные окружения
ENV PORT=50051 \
    MODEL_PATH=/app/models/model.pkl \
    MODEL_VERSION=v1.0.0

# Рабочая директория
WORKDIR /app

# Копирование зависимостей и установка
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Открываем порт для FastAPI
EXPOSE 8080
CMD ["uvicorn", "app.main:api", "--host", "0.0.0.0", "--port", "8080"]