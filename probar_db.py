from database import conectar

conexion = conectar()
cursor = conexion.cursor()

cursor.execute("""
INSERT INTO soldados (nombre, cedula, rango, foto, encoding)
VALUES (?, ?, ?, ?, ?)
""", ("Cristina", "12345678", "Capitán", "fotos/cristina.jpg", "[0.1, 0.2, 0.3]"))

conexion.commit()
conexion.close()

print("Datos insertados correctamente ✅")