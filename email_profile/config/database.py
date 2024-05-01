"""
Database Module
"""

import logging
import sqlite3

from peewee import SqliteDatabase


def engine_sqlite3():
    return sqlite3.connect("sql_app.db")


def engine_sqlite_database():
    try:
        return SqliteDatabase('sql_app.db')
    except Exception as error:
        logging.error(error)
