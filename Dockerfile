FROM python:3.12-slim

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
COPY telegram_wheel_bot/requirements.txt ./telegram_wheel_bot/
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r telegram_wheel_bot/requirements.txt

# Копируем код приложения
COPY app/ ./app/
COPY telegram_wheel_bot/ ./telegram_wheel_bot/

# Создаем директории для данных
RUN mkdir -p /app/data /app/wheels

# Запускаем бота
CMD ["python", "-m", "app.main"]

