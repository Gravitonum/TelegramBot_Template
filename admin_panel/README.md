# Административная панель WheelOfLifeBot

Веб-интерфейс для управления и мониторинга Telegram бота WheelOfLifeBot.

## Возможности

1. **Пользователи** - просмотр списка всех пользователей с датой последнего действия
2. **Колеса** - просмотр колес пользователей с возможностью фильтрации по пользователю
3. **Статистика** - аналитика за последние 30 дней:
   - Количество новых пользователей
   - Количество созданных колес
   - Количество неактивных пользователей

## Запуск через Docker

### Требования
- Docker Desktop (Windows)
- Docker Compose

### Запуск

```bash
docker-compose up -d
```

Админка будет доступна по адресу: http://localhost:3150

### Остановка

```bash
docker-compose down
```

## Локальный запуск (без Docker)

### Требования
- Python 3.12+
- Установленные зависимости из `requirements.txt`

### Установка зависимостей

```bash
pip install -r admin_panel/requirements.txt
```

### Запуск

```bash
cd admin_panel
python app.py
```

Админка будет доступна по адресу: http://localhost:3150

## Структура проекта

```
admin_panel/
├── app.py              # Flask приложение
├── templates/          # HTML шаблоны
│   └── index.html
├── static/             # Статические файлы
│   ├── style.css      # Стили
│   └── script.js      # JavaScript
├── requirements.txt    # Зависимости Python
├── Dockerfile         # Docker образ
└── README.md          # Документация
```

## API Endpoints

- `GET /` - Главная страница админки
- `GET /api/users` - Список всех пользователей
- `GET /api/users/<user_id>/wheels` - Колеса пользователя
- `GET /api/statistics` - Статистика за последние 30 дней

