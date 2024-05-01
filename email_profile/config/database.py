"""
Database Module
"""

import sqlite3


def engine_sqlite3():
    return sqlite3.connect("sql_app.db")
