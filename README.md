# Шаблон Telegram-бота для новичков

Этот проект представляет собой простой шаблон для создания Telegram-ботов на Python с использованием библиотеки `python-telegram-bot`. Шаблон разработан специально для новичков и включает в себя базовую структуру, меню с кнопками и логирование.

## Особенности

- ✅ Простое меню с inline-кнопками
- ✅ Команды `/start` и `/about` по умолчанию
- ✅ Логирование всех действий пользователей
- ✅ Шаблон для добавления новых команд и кнопок
- ✅ Четкая структура кода для легкого расширения

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта и добавьте ваш токен бота:

```
TELEGRAM_BOT_TOKEN=ваш_токен_бота_здесь
LOG_LEVEL=INFO
```

### 3. Запуск бота

```bash
python -m app.main
```

## Структура проекта

```
TelegramBot_Template/
├── app/
│   ├── __init__.py
│   ├── main.py          # Основной файл бота
├── requirements.txt     # Зависимости Python
├── .env.example         # Пример файла с переменными окружения
└── README.md           # Этот файл
```

## Адаптация шаблона под свой проект

### Добавление новой команды

1. **Создайте функцию-обработчик** в `app/main.py`:

```python
async def your_command_function(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик вашей новой команды."""
    logger.info(f"Пользователь {update.effective_user.id} запустил команду /your_command")

    # Ваш код здесь
    await update.message.reply_text("Ваше сообщение пользователю")
```

2. **Добавьте команду в меню бота** в функции `setup_bot_commands()`:

```python
commands = [
    ("start", "Начать работу с ботом"),
    ("about", "О боте"),
    ("your_command", "Описание вашей команды"),  # Добавьте эту строку
]
```

3. **Зарегистрируйте обработчик** в функции `main()`:

```python
application.add_handler(CommandHandler("your_command", your_command_function))
```

### Добавление новой кнопки в меню

1. **Добавьте кнопку в клавиатуру** в функции `start()`:

```python
keyboard = [
    [InlineKeyboardButton("О боте", callback_data="about")],
    [InlineKeyboardButton("Ваша кнопка", callback_data="your_button")],  # Добавьте эту строку
]
```

2. **Добавьте обработчик кнопки** в функции `button_handler()`:

```python
if callback_data == "about":
    await about(query, context)
elif callback_data == "your_button":  # Добавьте этот блок
    await your_button_function(query, context)
```

3. **Создайте функцию для обработки кнопки**:

```python
async def your_button_function(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатия на вашу кнопку."""
    logger.info(f"Пользователь {update.effective_user.id} нажал кнопку: your_button")

    # Ваш код здесь
    await update.callback_query.message.reply_text("Ваше сообщение пользователю")
```

### Логирование

Все действия пользователей автоматически логируются. Уровень логирования можно настроить в переменной окружения `LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR).

Примеры логов:
- Запуск команд: `Пользователь 123456789 запустил команду /start`
- Нажатие кнопок: `Пользователь 123456789 нажал кнопку: about`

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `TELEGRAM_BOT_TOKEN` | Токен вашего Telegram-бота | Обязательно указать |
| `LOG_LEVEL` | Уровень логирования | INFO |

## Получение токена бота

1. Напишите [@BotFather](https://t.me/botfather) в Telegram
2. Используйте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в файл `.env`

## Развертывание

### Локально

```bash
# Установка зависимостей
pip install -r requirements.txt

# Копирование примера переменных окружения
cp .env.example .env

# Редактирование .env файла с вашим токеном
nano .env

# Запуск бота
python -m app.main
```

### На сервере (пример с Docker)

Проект включает базовую поддержку Docker. Для продакшена рекомендуется настроить вебхуки вместо long polling.

## Поддержка

Если у вас возникли вопросы или проблемы:
1. Проверьте логи бота
2. Убедитесь, что токен бота корректный
3. Проверьте установку всех зависимостей

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле LICENSE.