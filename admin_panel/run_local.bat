@echo off
echo Установка зависимостей для админ-панели...
pip install -r requirements.txt

echo.
echo Запуск админ-панели...
echo Админка будет доступна по адресу: http://localhost:3150
echo.
python app.py

