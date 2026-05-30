import sqlite3
from datetime import datetime

def registrar_asistencia(cedula):
    conexion = sqlite3.connect("milfaces.db")
    cursor = conexion.cursor()

    fecha_hoy = datetime.now().date()
    hora_actual = datetime.now().strftime("%H:%M:%S")

    # Buscar si ya hay registro hoy
    cursor.execute("""
        SELECT id, hora_entrada, hora_salida 
        FROM asistencia 
        WHERE cedula = ? AND fecha = ?
    """, (cedula, fecha_hoy))

    resultado = cursor.fetchone()

    if resultado is None:
        # No hay registro → registrar entrada
        cursor.execute("""
            INSERT INTO asistencia (cedula, fecha, hora_entrada)
            VALUES (?, ?, ?)
        """, (cedula, fecha_hoy, hora_actual))

        conexion.commit()
        conexion.close()

        print("Entrada registrada")
        return "entrada"   # <-- AGREGADO

    else:
        id_registro, hora_entrada, hora_salida = resultado

        if hora_salida is None:
            # Ya tiene entrada → registrar salida
            cursor.execute("""
                UPDATE asistencia
                SET hora_salida = ?
                WHERE id = ?
            """, (hora_actual, id_registro))

            conexion.commit()
            conexion.close()

            print("Salida registrada")
            return "salida"   # <-- AGREGADO

        else:
            # Ya tiene entrada y salida → no hacer nada
            conexion.close()

            print("Ya tiene entrada y salida hoy")
            return "ya_registro"   # <-- AGREGADO