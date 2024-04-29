"""
Database Module
"""


import sqlite3

engine = sqlite3.connect("sql_app.db")
session = engine.cursor()
