import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.getenv("EVAL_DB_PATH", "eval_platform.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

@contextmanager
def get_cursor():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER,
                name TEXT NOT NULL,
                prompt_template TEXT NOT NULL,
                model_name TEXT NOT NULL,
                temperature REAL DEFAULT 0.7,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experiment_id) REFERENCES experiments (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER,
                input_data TEXT NOT NULL,
                expected_output TEXT,
                context TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                variant_id INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (variant_id) REFERENCES variants (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                test_case_id INTEGER,
                metric_name TEXT NOT NULL,
                score REAL NOT NULL,
                rationale TEXT,
                evaluator_type TEXT,
                FOREIGN KEY (run_id) REFERENCES evaluation_runs (id),
                FOREIGN KEY (test_case_id) REFERENCES test_cases (id)
            )
        ''')

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
