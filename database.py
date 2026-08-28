import sqlite3

DB_NAME = "news.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='articles'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        cursor.execute("PRAGMA table_info(articles)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        required_columns = ["id", "title", "url", "content", "image_url", "category", "hashtags", "created_at"]
        
        if set(existing_columns) != set(required_columns):
            cursor.execute("DROP TABLE articles")
            conn.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT UNIQUE,
            content TEXT,
            image_url TEXT,
            category TEXT,
            hashtags TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_article(title, url, content, image_url, category, hashtags, created_at):
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO articles (title, url, content, image_url, category, hashtags, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                title=excluded.title,
                content=excluded.content,
                image_url=excluded.image_url,
                category=excluded.category,
                hashtags=excluded.hashtags,
                created_at=excluded.created_at
        ''', (title, url, content, image_url, category, hashtags, created_at))
        conn.commit()
    except Exception as e:
        print(f"⚠️ Errore salvataggio DB: {e}")
    finally:
        conn.close()

def get_all_articles():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, url, content, image_url, category, hashtags, created_at FROM articles ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows