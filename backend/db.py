import os
import hashlib
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "mysql"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER", "app_deportes"),
    "password": os.getenv("DB_PASSWORD", "app_deportes_2026"),
    "database": os.getenv("DB_NAME", "actividades_deportivas"),
    "charset":  "utf8mb4",
    "use_unicode": True,
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_all(query, params=None):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(query, params or ())
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def fetch_one(query, params=None):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(query, params or ())
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def execute(query, params=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params or ())
        conn.commit()
        return cur.lastrowid
    except Error:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def hashear(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
