# Базовый образ
FROM python:3.11-slim

# Переменные окружения
ENV MODEL_PATH=/app/models/model.pkl \
    PORT=8080

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