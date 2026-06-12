import cv2
import sqlite3
import os

def registrar_soldado():
    nombres = input("Nombres: ")
    apellidos = input("Apellidos: ")
    cedula = input("Cedula: ")
    rango = input("Rango: ")

    conexion = sqlite3.connect("milfaces.db")
    cursor = conexion.cursor()

    cap = cv2.VideoCapture(0)

    fotos = {
        "frente": None,
        "derecha": None,
        "izquierda": None
    }

    for tipo in fotos:
        while True:
            ret, frame = cap.read()

            cv2.putText(frame, f"Tomar foto: {tipo}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            cv2.putText(frame, "Presiona F para tomar la foto", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

            cv2.imshow("Registro de Soldado", frame)

            if cv2.waitKey(1) & 0xFF == ord('f'):
                nombre_archivo = f"{cedula}_{tipo}.jpg"
                ruta = os.path.join("fotos", nombre_archivo)
                cv2.imwrite(ruta, frame)
                fotos[tipo] = ruta
                print(f"Foto {tipo} guardada")
                break

    cap.release()
    cv2.destroyAllWindows()

    cursor.execute("""
    INSERT INTO soldados (nombre, apellidos, cedula, rango, foto_frente, foto_derecha, foto_izquierda, encoding)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nombres, apellidos, cedula, rango,
          fotos["frente"], fotos["derecha"], fotos["izquierda"], "pendiente"))

    conexion.commit()
    conexion.close()

    print("Soldado registrado correctamente")

registrar_soldado()