@echo off
echo ========================================
echo   Запуск Telegram-бота (Windows)
echo ========================================

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Ошибка: Python не установлен или не найден в PATH
    echo Установите Python с https://python.org
    pause
    exit /b 1
)

REM Проверка наличия файла .env
if not exist .env (
    echo Ошибка: Файл .env не найден
    echo Скопируйте .env.example в .env и настройте переменные окружения
    pause
    exit /b 1
)

REM Установка зависимостей (если requirements.txt существует)
if exist requirements.txt (
    echo Установка зависимостей...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Ошибка при установке зависимостей
        pause
        exit /b 1
    )
)

REM Запуск бота
echo Запуск бота...
python -m app.main

pause