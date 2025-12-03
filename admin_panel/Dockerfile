FROM python:3.12-slim

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY admin_panel/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY admin_panel/app.py .
COPY admin_panel/templates/ ./templates/
COPY admin_panel/static/ ./static/

# Копируем telegram_wheel_bot для доступа к модулям БД
COPY telegram_wheel_bot/ ./telegram_wheel_bot/

# Открываем порт
EXPOSE 3150

# Запускаем приложение
CMD ["python", "app.py"]

