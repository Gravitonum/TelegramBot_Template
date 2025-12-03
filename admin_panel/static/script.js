// Управление вкладками
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');

            // Убираем активный класс у всех кнопок и контента
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Добавляем активный класс к выбранной кнопке и контенту
            button.classList.add('active');
            document.getElementById(`${targetTab}-tab`).classList.add('active');

            // Загружаем данные для активной вкладки
            if (targetTab === 'users') {
                loadUsers();
            } else if (targetTab === 'wheels') {
                loadUsersForWheels();
            } else if (targetTab === 'statistics') {
                loadStatistics();
            }
        });
    });

    // Загружаем данные для первой вкладки
    loadUsers();
});

// Загрузка списка пользователей
async function loadUsers() {
    const tbody = document.getElementById('users-tbody');
    tbody.innerHTML = '<tr><td colspan="6" class="loading">Загрузка...</td></tr>';

    try {
        const response = await fetch('/api/users');
        const result = await response.json();

        if (result.success) {
            if (result.data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="empty-state">Пользователи не найдены</td></tr>';
                return;
            }

            tbody.innerHTML = result.data.map(user => `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.telegram_id}</td>
                    <td>${user.first_name || '—'}</td>
                    <td>${user.username ? '@' + user.username : '—'}</td>
                    <td>${formatDate(user.created_at)}</td>
                    <td>${user.last_action_date ? formatDate(user.last_action_date) : 'Нет действий'}</td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = `<tr><td colspan="6" class="empty-state">Ошибка: ${result.error}</td></tr>`;
        }
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-state">Ошибка загрузки: ${error.message}</td></tr>`;
    }
}

// Загрузка пользователей для вкладки "Колеса"
let selectedUserId = null;

async function loadUsersForWheels() {
    const usersList = document.getElementById('users-list');
    usersList.innerHTML = '<div class="loading">Загрузка...</div>';

    try {
        const response = await fetch('/api/users');
        const result = await response.json();

        if (result.success) {
            if (result.data.length === 0) {
                usersList.innerHTML = '<div class="empty-state">Пользователи не найдены</div>';
                return;
            }

            usersList.innerHTML = result.data.map(user => `
                <div class="user-item" data-user-id="${user.id}" onclick="selectUser(${user.id}, '${escapeHtml(user.first_name || 'Пользователь')}', this)">
                    <div class="user-item-name">${escapeHtml(user.first_name || 'Пользователь')}</div>
                    <div class="user-item-id">ID: ${user.id} | Telegram: ${user.telegram_id}</div>
                </div>
            `).join('');

            // Выбираем первого пользователя по умолчанию
            if (result.data.length > 0 && !selectedUserId) {
                const firstUser = result.data[0];
                const firstUserElement = document.querySelector(`[data-user-id="${firstUser.id}"]`);
                selectUser(firstUser.id, firstUser.first_name || 'Пользователь', firstUserElement);
            }
        } else {
            usersList.innerHTML = `<div class="empty-state">Ошибка: ${result.error}</div>`;
        }
    } catch (error) {
        usersList.innerHTML = `<div class="empty-state">Ошибка загрузки: ${error.message}</div>`;
    }
}

// Выбор пользователя
async function selectUser(userId, userName, element) {
    selectedUserId = userId;
    
    // Обновляем активный элемент в списке
    document.querySelectorAll('.user-item').forEach(item => {
        item.classList.remove('active');
    });
    
    if (element) {
        element.classList.add('active');
    } else {
        // Если элемент не передан, находим его по data-user-id
        const userItem = document.querySelector(`[data-user-id="${userId}"]`);
        if (userItem) {
            userItem.classList.add('active');
        }
    }

    // Обновляем заголовок
    document.getElementById('selected-user-name').textContent = `Колеса пользователя: ${userName}`;

    // Загружаем колеса пользователя
    await loadUserWheels(userId);
}

// Загрузка колес пользователя
async function loadUserWheels(userId) {
    const wheelsList = document.getElementById('wheels-list');
    wheelsList.innerHTML = '<div class="loading">Загрузка...</div>';

    try {
        const response = await fetch(`/api/users/${userId}/wheels`);
        const result = await response.json();

        if (result.success) {
            if (result.data.length === 0) {
                wheelsList.innerHTML = '<div class="empty-state">У пользователя нет колес</div>';
                return;
            }

            wheelsList.innerHTML = result.data.map(wheel => `
                <div class="wheel-item">
                    <div class="wheel-header">
                        <div class="wheel-name">${escapeHtml(wheel.name)}</div>
                        <div class="wheel-date">${formatDate(wheel.created_at)}</div>
                    </div>
                    ${wheel.has_analysis ? '<span class="wheel-badge">✓ Есть анализ</span>' : ''}
                </div>
            `).join('');
        } else {
            wheelsList.innerHTML = `<div class="empty-state">Ошибка: ${result.error}</div>`;
        }
    } catch (error) {
        wheelsList.innerHTML = `<div class="empty-state">Ошибка загрузки: ${error.message}</div>`;
    }
}

// Загрузка статистики
async function loadStatistics() {
    const statsContent = document.getElementById('statistics-content');
    statsContent.innerHTML = '<div class="loading">Загрузка...</div>';

    try {
        const response = await fetch('/api/statistics');
        const result = await response.json();

        if (result.success) {
            const stats = result.data;
            statsContent.innerHTML = `
                <div class="stat-card clickable" onclick="showNewUsers()">
                    <h3>Новые пользователи</h3>
                    <div class="value">${stats.new_users}</div>
                    <div class="description">Подключились за последние 30 дней</div>
                    <div class="click-hint">Нажмите для просмотра списка</div>
                </div>
                <div class="stat-card clickable" onclick="showUsersWithWheels()">
                    <h3>Создано колес</h3>
                    <div class="value">${stats.wheels_created}</div>
                    <div class="description">За последние 30 дней</div>
                    <div class="click-hint">Нажмите для просмотра списка</div>
                </div>
                <div class="stat-card clickable" onclick="showInactiveUsers()">
                    <h3>Неактивные пользователи</h3>
                    <div class="value">${stats.inactive_users}</div>
                    <div class="description">Были активны в прошлом месяце, но не активны сейчас</div>
                    <div class="click-hint">Нажмите для просмотра списка</div>
                </div>
            `;
        } else {
            statsContent.innerHTML = `<div class="empty-state">Ошибка: ${result.error}</div>`;
        }
    } catch (error) {
        statsContent.innerHTML = `<div class="empty-state">Ошибка загрузки: ${error.message}</div>`;
    }
}

// Вспомогательные функции
function formatDate(dateString) {
    if (!dateString) return '—';
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Модальное окно
function openModal(title) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('detail-modal').style.display = 'block';
    document.getElementById('modal-loading').style.display = 'block';
    document.getElementById('modal-data').innerHTML = '';
}

function closeModal() {
    document.getElementById('detail-modal').style.display = 'none';
}

// Закрытие модального окна при клике вне его
window.onclick = function(event) {
    const modal = document.getElementById('detail-modal');
    if (event.target === modal) {
        closeModal();
    }
}

// Показать новых пользователей
async function showNewUsers() {
    openModal('Новые пользователи за последние 30 дней');
    
    try {
        const response = await fetch('/api/statistics/new-users');
        const result = await response.json();
        
        document.getElementById('modal-loading').style.display = 'none';
        
        if (result.success) {
            if (result.data.length === 0) {
                document.getElementById('modal-data').innerHTML = '<div class="empty-state">Новых пользователей не найдено</div>';
                return;
            }
            
            const table = `
                <table class="detail-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Telegram ID</th>
                            <th>Имя</th>
                            <th>Username</th>
                            <th>Дата регистрации</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${result.data.map(user => `
                            <tr>
                                <td>${user.id}</td>
                                <td>${user.telegram_id}</td>
                                <td>${escapeHtml(user.first_name || '—')}</td>
                                <td>${user.username ? '@' + escapeHtml(user.username) : '—'}</td>
                                <td>${formatDate(user.created_at)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            document.getElementById('modal-data').innerHTML = table;
        } else {
            document.getElementById('modal-data').innerHTML = `<div class="empty-state">Ошибка: ${result.error}</div>`;
        }
    } catch (error) {
        document.getElementById('modal-loading').style.display = 'none';
        document.getElementById('modal-data').innerHTML = `<div class="empty-state">Ошибка загрузки: ${error.message}</div>`;
    }
}

// Показать пользователей с колесами
async function showUsersWithWheels() {
    openModal('Пользователи, создавшие колеса за последние 30 дней');
    
    try {
        const response = await fetch('/api/statistics/users-with-wheels');
        const result = await response.json();
        
        document.getElementById('modal-loading').style.display = 'none';
        
        if (result.success) {
            if (result.data.length === 0) {
                document.getElementById('modal-data').innerHTML = '<div class="empty-state">Пользователей не найдено</div>';
                return;
            }
            
            const table = `
                <table class="detail-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Telegram ID</th>
                            <th>Имя</th>
                            <th>Username</th>
                            <th>Колес создано</th>
                            <th>Последнее колесо</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${result.data.map(user => `
                            <tr>
                                <td>${user.id}</td>
                                <td>${user.telegram_id}</td>
                                <td>${escapeHtml(user.first_name || '—')}</td>
                                <td>${user.username ? '@' + escapeHtml(user.username) : '—'}</td>
                                <td><strong>${user.wheels_count}</strong></td>
                                <td>${formatDate(user.last_wheel_date)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            document.getElementById('modal-data').innerHTML = table;
        } else {
            document.getElementById('modal-data').innerHTML = `<div class="empty-state">Ошибка: ${result.error}</div>`;
        }
    } catch (error) {
        document.getElementById('modal-loading').style.display = 'none';
        document.getElementById('modal-data').innerHTML = `<div class="empty-state">Ошибка загрузки: ${error.message}</div>`;
    }
}

// Показать неактивных пользователей
async function showInactiveUsers() {
    openModal('Неактивные пользователи');
    
    try {
        const response = await fetch('/api/statistics/inactive-users');
        const result = await response.json();
        
        document.getElementById('modal-loading').style.display = 'none';
        
        if (result.success) {
            if (result.data.length === 0) {
                document.getElementById('modal-data').innerHTML = '<div class="empty-state">Неактивных пользователей не найдено</div>';
                return;
            }
            
            const table = `
                <table class="detail-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Telegram ID</th>
                            <th>Имя</th>
                            <th>Username</th>
                            <th>Последнее колесо</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${result.data.map(user => `
                            <tr>
                                <td>${user.id}</td>
                                <td>${user.telegram_id}</td>
                                <td>${escapeHtml(user.first_name || '—')}</td>
                                <td>${user.username ? '@' + escapeHtml(user.username) : '—'}</td>
                                <td>${formatDate(user.last_wheel_date)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            document.getElementById('modal-data').innerHTML = table;
        } else {
            document.getElementById('modal-data').innerHTML = `<div class="empty-state">Ошибка: ${result.error}</div>`;
        }
    } catch (error) {
        document.getElementById('modal-loading').style.display = 'none';
        document.getElementById('modal-data').innerHTML = `<div class="empty-state">Ошибка загрузки: ${error.message}</div>`;
    }
}

