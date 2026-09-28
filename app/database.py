import sqlite3
import os

DB_PATH = "notes.db"

def get_connection():
    # Return a dict-like cursor connection
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            token TEXT UNIQUE NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def seed_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Check if seeded
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [
            ("alice", "alice@example.com", "dev-token-user1"),
            ("bob", "bob@example.com", "dev-token-user2")
        ]
        c.executemany("INSERT INTO users (username, email, token) VALUES (?, ?, ?)", users)
        
        notes = [
            (1, "Alice's Secret", "This is a secret note for Alice only."),
            (1, "Groceries", "Apples, Bananas, Carrots"),
            (2, "Bob's Master Plan", "Take over the world."),
            (2, "Todo", "Learn MCP")
        ]
        c.executemany("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)", notes)
        
        conn.commit()
    conn.close()

def get_user_by_token(token: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE token = ?", (token,))
    user = c.fetchone()
    conn.close()
    return user
