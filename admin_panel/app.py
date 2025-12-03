"""
Flask приложение для административной панели WheelOfLifeBot
"""
import os
import sys
from flask import Flask, render_template, jsonify
from pathlib import Path

# Добавляем путь к telegram_wheel_bot для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

# Устанавливаем DATABASE_URL перед импортом модулей БД
db_path = os.getenv('DATABASE_URL')
if not db_path:
    # Если не указан в переменных окружения, определяем автоматически
    # В Docker контейнере БД будет в /app/data/wheel_of_life.db
    docker_db_path = '/app/data/wheel_of_life.db'
    if os.path.exists(docker_db_path):
        db_path = f'sqlite:///{docker_db_path}'
    else:
        # Проверяем старый путь для обратной совместимости
        old_docker_path = '/app/wheel_of_life.db'
        if os.path.exists(old_docker_path):
            db_path = f'sqlite:///{old_docker_path}'
        else:
            # Локально используем путь относительно корня проекта
            db_path = f'sqlite:///{Path(__file__).parent.parent / "wheel_of_life.db"}'

os.environ['DATABASE_URL'] = db_path

from telegram_wheel_bot.database.repository import (
    get_all_users_with_last_action,
    get_user_wheels,
    get_statistics_30_days,
    get_new_users_30_days,
    get_users_with_wheels_30_days,
    get_inactive_users
)

app = Flask(__name__)


@app.route('/')
def index():
    """Главная страница админки."""
    return render_template('index.html')


@app.route('/api/users')
def api_users():
    """API endpoint для получения списка всех пользователей."""
    try:
        users = get_all_users_with_last_action()
        return jsonify({'success': True, 'data': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/users/<int:user_id>/wheels')
def api_user_wheels(user_id):
    """API endpoint для получения колес пользователя."""
    try:
        wheels = get_user_wheels(user_id)
        return jsonify({'success': True, 'data': wheels})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/statistics')
def api_statistics():
    """API endpoint для получения статистики за последние 30 дней."""
    try:
        stats = get_statistics_30_days()
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/statistics/new-users')
def api_new_users():
    """API endpoint для получения списка новых пользователей за последние 30 дней."""
    try:
        users = get_new_users_30_days()
        return jsonify({'success': True, 'data': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/statistics/users-with-wheels')
def api_users_with_wheels():
    """API endpoint для получения списка пользователей, создавших колеса за последние 30 дней."""
    try:
        users = get_users_with_wheels_30_days()
        return jsonify({'success': True, 'data': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/statistics/inactive-users')
def api_inactive_users():
    """API endpoint для получения списка неактивных пользователей."""
    try:
        users = get_inactive_users()
        return jsonify({'success': True, 'data': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('ADMIN_PORT', 3150))
    app.run(host='0.0.0.0', port=port, debug=True)

