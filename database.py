import sqlite3
from config import DATABASE

def conectar():
    conexion = sqlite3.connect(DATABASE)
    return conexion