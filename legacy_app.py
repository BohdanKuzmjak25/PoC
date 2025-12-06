"""
Legacy Task Management System
=============================
УВАГА: Це ПОГАНИЙ код для демонстрації!
Містить типові проблеми Legacy-систем.

Проблеми:
- SQL Injection вразливості
- Висока цикломатична складність
- Відсутність тестів
- Жорстка зв'язність (tight coupling)
- Дублювання коду
- Порушення SOLID принципів
- Відсутність обробки помилок
"""

import sqlite3
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_PATH = 'tasks.db'

# ❌ ПРОБЛЕМА: Глобальне з'єднання з БД
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# ❌ ПРОБЛЕМА: Ініціалізація БД в основному коді
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT,
        email TEXT,
        role TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        title TEXT,
        description TEXT,
        status TEXT,
        priority TEXT,
        user_id INTEGER,
        created_at TEXT,
        due_date TEXT
    )
''')
conn.commit()


# ❌ ПРОБЛЕМА: Монстр-функція з Cyclomatic Complexity = 28
@app.route('/api/tasks', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_tasks():
    """
    Одна функція обробляє все - класичний God Object anti-pattern
    Complexity: 28 (критично високий!)
    Lines of Code: 180+
    """
    
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        status = request.args.get('status')
        priority = request.args.get('priority')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by')
        
        # ❌ ПРОБЛЕМА: SQL Injection через конкатенацію
        query = "SELECT * FROM tasks WHERE 1=1"
        
        if user_id:
            if user_id.isdigit():
                query += f" AND user_id = {user_id}"  # SQL INJECTION!
            else:
                return jsonify({'error': 'Invalid user_id'}), 400
        
        if status:
            if status in ['pending', 'in_progress', 'completed', 'cancelled']:
                query += f" AND status = '{status}'"  # SQL INJECTION!
            else:
                return jsonify({'error': 'Invalid status'}), 400
        
        if priority:
            if priority in ['low', 'medium', 'high', 'critical']:
                query += f" AND priority = '{priority}'"  # SQL INJECTION!
            else:
                return jsonify({'error': 'Invalid priority'}), 400
        
        if search:
            # ❌ ПРОБЛЕМА: Критична SQL Injection
            query += f" AND (title LIKE '%{search}%' OR description LIKE '%{search}%')"
        
        if sort_by:
            if sort_by == 'date':
                query += " ORDER BY created_at DESC"
            elif sort_by == 'priority':
                query += " ORDER BY CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END"
            elif sort_by == 'status':
                query += " ORDER BY status"
            else:
                return jsonify({'error': 'Invalid sort_by'}), 400
        
        cursor.execute(query)
        tasks = cursor.fetchall()
        
        # ❌ ПРОБЛЕМА: Дублювання коду для форматування
        result = []
        for task in tasks:
            result.append({
                'id': task[0],
                'title': task[1],
                'description': task[2],
                'status': task[3],
                'priority': task[4],
                'user_id': task[5],
                'created_at': task[6],
                'due_date': task[7]
            })
        
        return jsonify(result), 200
    
    elif request.method == 'POST':
        data = request.json
        
        # ❌ ПРОБЛЕМА: Довгий ланцюг if-else для валідації
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        if len(data['title']) < 3:
            return jsonify({'error': 'Title too short'}), 400
        
        if len(data['title']) > 200:
            return jsonify({'error': 'Title too long'}), 400
        
        if 'user_id' not in data:
            return jsonify({'error': 'User ID is required'}), 400
        
        if not str(data['user_id']).isdigit():
            return jsonify({'error': 'Invalid user_id'}), 400
        
        # Перевірка чи існує користувач
        # ❌ ПРОБЛЕМА: SQL Injection
        user_check = f"SELECT * FROM users WHERE id = {data['user_id']}"
        cursor.execute(user_check)
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Перевірка ролі користувача
        if user[4] == 'guest':
            # Гості можуть створювати лише 5 задач
            count_query = f"SELECT COUNT(*) FROM tasks WHERE user_id = {data['user_id']}"
            cursor.execute(count_query)
            count = cursor.fetchone()[0]
            
            if count >= 5:
                return jsonify({'error': 'Guest users cannot create more than 5 tasks'}), 403
        
        status = data.get('status', 'pending')
        if status not in ['pending', 'in_progress', 'completed', 'cancelled']:
            return jsonify({'error': 'Invalid status'}), 400
        
        priority = data.get('priority', 'medium')
        if priority not in ['low', 'medium', 'high', 'critical']:
            return jsonify({'error': 'Invalid priority'}), 400
        
        description = data.get('description', '')
        due_date = data.get('due_date')
        
        if due_date:
            try:
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
                if due_date_obj < datetime.now():
                    return jsonify({'error': 'Due date cannot be in the past'}), 400
            except:
                return jsonify({'error': 'Invalid date format'}), 400
        
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # ❌ ПРОБЛЕМА: Критична SQL Injection
        insert_query = f"""
            INSERT INTO tasks (title, description, status, priority, user_id, created_at, due_date)
            VALUES ('{data['title']}', '{description}', '{status}', '{priority}', 
                    {data['user_id']}, '{created_at}', '{due_date}')
        """
        
        try:
            cursor.execute(insert_query)
            conn.commit()
            task_id = cursor.lastrowid
            
            # ❌ ПРОБЛЕМА: Дублювання коду
            return jsonify({
                'id': task_id,
                'title': data['title'],
                'description': description,
                'status': status,
                'priority': priority,
                'user_id': data['user_id'],
                'created_at': created_at,
                'due_date': due_date
            }), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        data = request.json
        
        if not data or 'id' not in data:
            return jsonify({'error': 'Task ID is required'}), 400
        
        task_id = data['id']
        
        # ❌ ПРОБЛЕМА: SQL Injection
        check_query = f"SELECT * FROM tasks WHERE id = {task_id}"
        cursor.execute(check_query)
        task = cursor.fetchone()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Формування UPDATE запиту
        updates = []
        
        if 'title' in data:
            if len(data['title']) < 3:
                return jsonify({'error': 'Title too short'}), 400
            updates.append(f"title = '{data['title']}'")  # SQL INJECTION!
        
        if 'description' in data:
            updates.append(f"description = '{data['description']}'")  # SQL INJECTION!
        
        if 'status' in data:
            if data['status'] not in ['pending', 'in_progress', 'completed', 'cancelled']:
                return jsonify({'error': 'Invalid status'}), 400
            updates.append(f"status = '{data['status']}'")
        
        if 'priority' in data:
            if data['priority'] not in ['low', 'medium', 'high', 'critical']:
                return jsonify({'error': 'Invalid priority'}), 400
            updates.append(f"priority = '{data['priority']}'")
        
        if not updates:
            return jsonify({'error': 'No fields to update'}), 400
        
        # ❌ ПРОБЛЕМА: SQL Injection
        update_query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = {task_id}"
        
        try:
            cursor.execute(update_query)
            conn.commit()
            
            # Отримати оновлену задачу
            cursor.execute(f"SELECT * FROM tasks WHERE id = {task_id}")
            updated_task = cursor.fetchone()
            
            return jsonify({
                'id': updated_task[0],
                'title': updated_task[1],
                'description': updated_task[2],
                'status': updated_task[3],
                'priority': updated_task[4],
                'user_id': updated_task[5],
                'created_at': updated_task[6],
                'due_date': updated_task[7]
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        task_id = request.args.get('id')
        
        if not task_id:
            return jsonify({'error': 'Task ID is required'}), 400
        
        # ❌ ПРОБЛЕМА: SQL Injection
        delete_query = f"DELETE FROM tasks WHERE id = {task_id}"
        
        try:
            cursor.execute(delete_query)
            conn.commit()
            
            if cursor.rowcount == 0:
                return jsonify({'error': 'Task not found'}), 404
            
            return jsonify({'message': 'Task deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500


# ❌ ПРОБЛЕМА: Ще одна монстр-функція
@app.route('/api/users', methods=['GET', 'POST'])
def handle_users():
    """
    Complexity: 15
    Проблеми: SQL Injection, відсутність хешування паролів
    """
    
    if request.method == 'GET':
        user_id = request.args.get('id')
        username = request.args.get('username')
        role = request.args.get('role')
        
        query = "SELECT id, username, email, role FROM users WHERE 1=1"
        
        if user_id:
            query += f" AND id = {user_id}"  # SQL INJECTION!
        
        if username:
            query += f" AND username = '{username}'"  # SQL INJECTION!
        
        if role:
            if role not in ['admin', 'user', 'guest']:
                return jsonify({'error': 'Invalid role'}), 400
            query += f" AND role = '{role}'"
        
        cursor.execute(query)
        users = cursor.fetchall()
        
        result = []
        for user in users:
            result.append({
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[3]
            })
        
        return jsonify(result), 200
    
    elif request.method == 'POST':
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # ❌ ПРОБЛЕМА: Слабке хешування MD5
        password_hash = hashlib.md5(data['password'].encode()).hexdigest()
        
        email = data.get('email', '')
        role = data.get('role', 'user')
        
        if role not in ['admin', 'user', 'guest']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # ❌ ПРОБЛЕМА: SQL Injection
        insert_query = f"""
            INSERT INTO users (username, password, email, role)
            VALUES ('{data['username']}', '{password_hash}', '{email}', '{role}')
        """
        
        try:
            cursor.execute(insert_query)
            conn.commit()
            
            return jsonify({
                'id': cursor.lastrowid,
                'username': data['username'],
                'email': email,
                'role': role
            }), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500


# ❌ ПРОБЛЕМА: Аутентифікація без JWT/Session
@app.route('/api/login', methods=['POST'])
def login():
    """Небезпечна аутентифікація"""
    data = request.json
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password required'}), 400
    
    # ❌ ПРОБЛЕМА: SQL Injection
    password_hash = hashlib.md5(data['password'].encode()).hexdigest()
    query = f"SELECT * FROM users WHERE username = '{data['username']}' AND password = '{password_hash}'"
    
    cursor.execute(query)
    user = cursor.fetchone()
    
    if user:
        return jsonify({
            'message': 'Login successful',
            'user_id': user[0],
            'username': user[1],
            'role': user[4]
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


# ❌ ПРОБЛЕМА: Статистика з N+1 запитами
@app.route('/api/statistics', methods=['GET'])
def statistics():
    """
    Complexity: 12
    Проблема: N+1 queries, неефективні запити
    """
    
    # Кількість задач по статусах
    stats = {}
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
    stats['pending'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'in_progress'")
    stats['in_progress'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
    stats['completed'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'cancelled'")
    stats['cancelled'] = cursor.fetchone()[0]
    
    # Кількість задач по пріоритетах
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE priority = 'low'")
    stats['priority_low'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE priority = 'medium'")
    stats['priority_medium'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE priority = 'high'")
    stats['priority_high'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE priority = 'critical'")
    stats['priority_critical'] = cursor.fetchone()[0]
    
    # Топ користувачів
    cursor.execute("SELECT user_id, COUNT(*) as count FROM tasks GROUP BY user_id ORDER BY count DESC LIMIT 5")
    top_users = cursor.fetchall()
    
    stats['top_users'] = []
    for user_data in top_users:
        # ❌ ПРОБЛЕМА: N+1 query
        cursor.execute(f"SELECT username FROM users WHERE id = {user_data[0]}")
        username = cursor.fetchone()
        
        stats['top_users'].append({
            'user_id': user_data[0],
            'username': username[0] if username else 'Unknown',
            'task_count': user_data[1]
        })
    
    return jsonify(stats), 200


if __name__ == '__main__':
    # ❌ ПРОБЛЕМА: Debug mode у production, небезпечний host
    app.run(debug=True, host='0.0.0.0', port=5000)
