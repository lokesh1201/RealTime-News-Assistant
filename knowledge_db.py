import sqlite3
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define constants
DB_FILE = "knowledge.db"

def init_db(db_file=DB_FILE):
    """
    Initialize the SQLite database and create the 'knowledge' table if it doesn't exist.
    """
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT UNIQUE NOT NULL,
                    answer TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
        logging.info(f"Database initialized: {db_file}")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")

def load_knowledge(limit=10, db_file=DB_FILE):
    """
    Load the latest knowledge entries from the database.
    """
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT query, answer, timestamp FROM knowledge ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
        return [{"Query": r[0], "Answer": r[1], "Timestamp": r[2]} for r in rows]
    except Exception as e:
        logging.error(f"Error loading knowledge base: {e}")
        return []

def save_knowledge(query, answer, db_file=DB_FILE):
    """
    Save a new query-answer pair to the database.
    """
    # Validate input
    if not query or not answer:
        logging.warning("Cannot save empty query or answer.")
        return

    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO knowledge (query, answer, timestamp)
                VALUES (?, ?, ?)
            """, (query, answer, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        logging.info(f"Saved entry: Query='{query}'")
    except sqlite3.IntegrityError:
        logging.warning(f"Duplicate query skipped: '{query}'")
    except Exception as e:
        logging.error(f"Error saving to knowledge base: {e}")