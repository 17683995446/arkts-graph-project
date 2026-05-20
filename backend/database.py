import sqlite3
import hashlib
import os
import threading
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

# Default database path
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'knowledge_graph.db')
# Global custom database path (for testing)
_custom_db_path: Optional[str] = None

# Thread lock for concurrent access
_db_lock = threading.Lock()

def set_custom_db_path(path: Optional[str]):
    """Set a custom database path (for testing)."""
    global _custom_db_path
    _custom_db_path = path

def get_db_path() -> str:
    """Get the current database path."""
    return _custom_db_path or DATABASE_PATH

@contextmanager
def get_db_connection():
    # Acquire lock for thread safety
    with _db_lock:
        conn = sqlite3.connect(get_db_path(), timeout=30.0)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

def init_database(db_path: str = None):
    if db_path:
        # Set custom path temporarily
        original = _custom_db_path
        set_custom_db_path(db_path)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    hash BLOB NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    file_id INTEGER NOT NULL,
                    flags INTEGER DEFAULT 0,
                    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS methods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    class_id INTEGER NOT NULL,
                    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS calls (
                    caller_id INTEGER NOT NULL,
                    callee_id INTEGER NOT NULL,
                    PRIMARY KEY (caller_id, callee_id),
                    FOREIGN KEY (caller_id) REFERENCES methods(id) ON DELETE CASCADE,
                    FOREIGN KEY (callee_id) REFERENCES methods(id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS components (
                    parent_id INTEGER NOT NULL,
                    child_id INTEGER NOT NULL,
                    PRIMARY KEY (parent_id, child_id),
                    FOREIGN KEY (parent_id) REFERENCES classes(id) ON DELETE CASCADE,
                    FOREIGN KEY (child_id) REFERENCES classes(id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_classes_file_id ON classes(file_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_methods_class_id ON methods(class_id)')
    finally:
        if db_path:
            # Restore original path
            set_custom_db_path(original)

# Alias for backward compatibility
init_db = init_database

def compute_file_hash(file_path: str) -> str:
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_all_files() -> List[Dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM files')
        return [dict(row) for row in cursor.fetchall()]

def get_file_by_path(path: str) -> Optional[Dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM files WHERE path = ?', (path,))
        row = cursor.fetchone()
        return dict(row) if row else None

def delete_file_data(file_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get all class ids first, as they're needed to delete methods/calls/components
        cursor.execute('SELECT id FROM classes WHERE file_id = ?', (file_id,))
        class_ids = [row['id'] for row in cursor.fetchall()]
        
        if class_ids:
            # Get all method ids to delete calls first
            placeholders = ','.join(['?'] * len(class_ids))
            cursor.execute(f'SELECT id FROM methods WHERE class_id IN ({placeholders})', class_ids)
            method_ids = [row['id'] for row in cursor.fetchall()]
            
            if method_ids:
                # Delete calls
                method_placeholders = ','.join(['?'] * len(method_ids))
                cursor.execute(f'DELETE FROM calls WHERE caller_id IN ({method_placeholders}) OR callee_id IN ({method_placeholders})', method_ids * 2)
                
                # Delete methods
                cursor.execute(f'DELETE FROM methods WHERE class_id IN ({placeholders})', class_ids)
            
            # Delete components
            cursor.execute(f'DELETE FROM components WHERE parent_id IN ({placeholders}) OR child_id IN ({placeholders})', class_ids * 2)
            
            # Delete classes
            cursor.execute(f'DELETE FROM classes WHERE file_id = ?', (file_id,))
        
        # Finally delete the file itself
        cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))

def insert_file(path: str, file_hash: str) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO files (path, hash, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)',
            (path, file_hash)
        )
        if cursor.lastrowid:
            return cursor.lastrowid
        cursor.execute('SELECT id FROM files WHERE path = ?', (path,))
        return cursor.fetchone()['id']

def update_file(file_id: int, path: str, file_hash: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE files SET path = ?, hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (path, file_hash, file_id)
        )

def sync_file(file_path: str):
    import arkts_analyzer
    arkts_analyzer.update_file_knowledge_graph(file_path)

def sync_directory(dir_path: str):
    import arkts_analyzer
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.ets') or file.endswith('.ts'):
                full_path = os.path.join(root, file)
                sync_file(full_path)

def insert_class(name: str, file_id: int, flags: int = 0) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO classes (name, file_id, flags) VALUES (?, ?, ?)',
            (name, file_id, flags)
        )
        return cursor.lastrowid

def insert_method(name: str, class_id: int) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO methods (name, class_id) VALUES (?, ?)',
            (name, class_id)
        )
        return cursor.lastrowid

def insert_call(caller_id: int, callee_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR IGNORE INTO calls (caller_id, callee_id) VALUES (?, ?)',
            (caller_id, callee_id)
        )

def insert_component(parent_id: int, child_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR IGNORE INTO components (parent_id, child_id) VALUES (?, ?)',
            (parent_id, child_id)
        )

def get_all_classes() -> List[Dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM classes')
        return [dict(row) for row in cursor.fetchall()]

def get_all_methods() -> List[Dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM methods')
        return [dict(row) for row in cursor.fetchall()]

def get_all_calls() -> List[Dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM calls')
        return [dict(row) for row in cursor.fetchall()]

def get_all_components() -> List[Dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM components')
        return [dict(row) for row in cursor.fetchall()]

def execute_custom_query(sql: str) -> List[Dict]:
    """
    Execute a custom SQL query with validation.
    Only SELECT queries are allowed for security.
    """
    # Preserve original case for execution
    original_sql = sql.strip()
    upper_sql = original_sql.upper()
    
    # Only allow SELECT queries to prevent SQL injection
    if not upper_sql.startswith('SELECT'):
        raise ValueError("Only SELECT queries are allowed")
    
    # Block dangerous SQL keywords
    dangerous_keywords = [
        'DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER',
        'TRUNCATE', 'EXEC', 'EXECUTE', 'GRANT', 'REVOKE', 'UNION'
    ]
    
    for keyword in dangerous_keywords:
        if keyword in upper_sql:
            raise ValueError(f"Dangerous SQL keyword '{keyword}' is not allowed")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Execute the original query (already validated)
        cursor.execute(original_sql)
        return [dict(row) for row in cursor.fetchall()]
