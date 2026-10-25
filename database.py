import sqlite3

DB_NAME = "projects.db"

def init_db():
    """Создает таблицу, если её еще нет"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        link TEXT
    )""")
    conn.commit()
    conn.close()

def add_project(name, description, link):
    """Добавляет проект в базу"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (name, description, link) VALUES (?, ?, ?)", (name, description, link))
    conn.commit()
    conn.close()

def get_projects():
    """Возвращает список всех проектов"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, link FROM projects")
    projects = cursor.fetchall()
    conn.close()
    return projects