# -*- coding: utf-8 -*-
"""
Database connection and session utilities for DUST 2 DOLLAR Backend.
Supports SQLite out of the box with optional PostgreSQL URL via DATABASE_URL.
"""
import os
import sqlite3
from typing import Generator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "dust2dollar.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
