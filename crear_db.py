"""
MILFACE - Creador de Base de Datos 
Ejecuta este archivo UNA SOLA VEZ para crear toda la base de datos
desde cero antes de iniciar el sistema por primera vez.

Uso:
    python crear_db.py
"""

import sqlite3
import os

# Nombre del archivo de base de datos
DB_PATH = "milfaces.db"

def crear_base_de_datos():
    print("=" * 50)
    print("  MILFACE - Inicializando Base de Datos")
    print("=" * 50)

    # Conectar (crea el archivo si no existe)
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    
    # TABLA: soldados
    # Almacena la información de cada militar registrado 
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS soldados (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre          TEXT NOT NULL,
        apellidos       TEXT,
        cedula          TEXT NOT NULL UNIQUE,
        rango           TEXT NOT NULL,
        sexo            TEXT DEFAULT 'No especificado',
        tipo_sangre     TEXT DEFAULT 'O+',
        foto_frente     TEXT,
        foto_derecha    TEXT,
        foto_izquierda  TEXT,
        estado          TEXT
    )
    """)
    print("[OK] Tabla 'soldados' lista.")

    
    # TABLA: asistencia
    # Registra las entradas y salidas de cada soldado
   
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asistencia (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        cedula          TEXT,
        id_soldado      INTEGER,
        fecha           TEXT,
        hora_entrada    TEXT,
        hora_salida     TEXT,
        FOREIGN KEY (id_soldado) REFERENCES soldados(id)
    )
    """)
    print("[OK] Tabla 'asistencia' lista.")

    
    # TABLA: configuraciones
    # Guarda ajustes del sistema (tema visual, saludos, etc.)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS configuraciones (
        clave   TEXT PRIMARY KEY,
        valor   TEXT
    )
    """)
    # Valores por defecto
    cursor.execute("INSERT OR IGNORE INTO configuraciones (clave, valor) VALUES ('tema_visual', 'dark')")
    cursor.execute("INSERT OR IGNORE INTO configuraciones (clave, valor) VALUES ('saludo_ia', 'Acceso Concedido. Bienvenido Comandante al Sistema de Inteligencia Milface.')")
    print("[OK] Tabla 'configuraciones' lista.")

   
    # TABLA: auditoria_bajas
    # Registra el historial de bajas militares con razón
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auditoria_bajas (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        cedula  TEXT,
        razon   TEXT,
        fecha   TEXT
    )
    """)
    print("[OK] Tabla 'auditoria_bajas' lista.")

    # Crear carpeta de fotos si no existe
    if not os.path.exists("fotos"):
        os.makedirs("fotos")
        print("[OK] Carpeta 'fotos/' creada.")
    else:
        print("[OK] Carpeta 'fotos/' ya existe.")

    conexion.commit()
    conexion.close()

    print()
    print("=" * 50)
    print(f"  Base de datos '{DB_PATH}' creada exitosamente.")
    print("  Ahora puedes ejecutar: python app.py")
    print("=" * 50)


if __name__ == "__main__":
    crear_base_de_datos()