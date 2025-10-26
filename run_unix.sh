#!/bin/bash

echo "========================================"
echo "   Запуск Telegram-бота (Mac/Linux)"
echo "========================================"

# Проверка наличия Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Ошибка: Python не установлен или не найден в PATH"
    echo "Установите Python с https://python.org"
    exit 1
fi

# Определение команды Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Проверка наличия файла .env
if [ ! -f ".env" ]; then
    echo "Ошибка: Файл .env не найден"
    echo "Скопируйте .env.example в .env и настройте переменные окружения"
    exit 1
fi

# Установка зависимостей (если requirements.txt существует)
if [ -f "requirements.txt" ]; then
    echo "Установка зависимостей..."
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Ошибка при установке зависимостей"
        exit 1
    fi
fi

# Запуск бота
echo "Запуск бота..."
$PYTHON_CMD -m app.main