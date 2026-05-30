import cv2
import sqlite3
import time
from asistencia import registrar_asistencia
import numpy as np
import os

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
face_recognizer = cv2.face.LBPHFaceRecognizer_create()
soldados_info = {}
modelo_entrenado = False
ultima_cedula = None
ultimo_tiempo = 0

def procesar_rostro(img):
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gris = cv2.GaussianBlur(gris, (5, 5), 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gris = clahe.apply(gris)
    return gris

def entrenar_modelo():
    global modelo_entrenado
    conexion = sqlite3.connect("milfaces.db")
    cursor = conexion.cursor()
    
    cursor.execute("""
    SELECT id, cedula, nombre, apellidos, rango, sexo, foto_frente, foto_derecha, foto_izquierda, estado 
    FROM soldados
    """)
    soldados = cursor.fetchall()
    
    faces = []
    labels = []
    global soldados_info
    soldados_info.clear()

    for soldado in soldados:
        id_soldado, cedula, nombre, apellidos, rango, sexo, frente, derecha, izquierda, estado = soldado
        soldados_info[id_soldado] = (cedula, nombre, apellidos, rango, sexo, estado)
        
        fotos = [frente, derecha, izquierda]
        for ruta in fotos:
            if ruta and os.path.exists(ruta):
                try:
                    img_guardada = cv2.imread(ruta)
                    if img_guardada is not None:
                        img_procesada = procesar_rostro(img_guardada)
                        caras_guardadas = face_cascade.detectMultiScale(img_procesada, 1.3, 5)
                        
                        if len(caras_guardadas) > 0:
                            (x_g, y_g, w_g, h_g) = caras_guardadas[0]
                            rostro_recortado = img_procesada[y_g:y_g+h_g, x_g:x_g+w_g]
                            rostro_redimensionado = cv2.resize(rostro_recortado, (150, 150))
                            faces.append(rostro_redimensionado)
                            labels.append(id_soldado)
                        else:
                            rostro_redimensionado = cv2.resize(img_procesada, (150, 150))
                            faces.append(rostro_redimensionado)
                            labels.append(id_soldado)
                except Exception as e:
                    print(f"Error parseando foto: {e}")

    if len(faces) > 0:
        face_recognizer.train(faces, np.array(labels))
        modelo_entrenado = True
    else:
        modelo_entrenado = False
        
    conexion.close()

def reconocer_imagen(frame):
    global ultima_cedula, ultimo_tiempo
    
    if not modelo_entrenado:
        # Intentar entrenarlo rapido si no lo esta
        entrenar_modelo()
        if not modelo_entrenado:
            return {"status": "error", "mensaje": "No hay datos para entrenar"}
        
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    caras = face_cascade.detectMultiScale(gris, 1.3, 5)

    mejor_resultado = 999
    mejor_soldado = None

    for (x, y, w, h) in caras:
        rostro_color = frame[y:y+h, x:x+w]
        rostro_procesado = procesar_rostro(rostro_color)
        rostro_procesado = cv2.resize(rostro_procesado, (150, 150))
        
        try:
            label, confidencia = face_recognizer.predict(rostro_procesado)
            # Umbral de confidencia flexibilizado de 45 a 75 para permitir mayor éxito de reconocimiento en condiciones reales de iluminación
            if confidencia < 75: 
                if confidencia < mejor_resultado:
                    mejor_resultado = confidencia
                    mejor_soldado = soldados_info.get(label)
        except Exception:
            pass

    # Tomar la mejor coincidencia del frame (si hay multiples caras, la que tenga mas confidencia)
    if mejor_soldado is not None:
        cedula, nombre, apellidos, rango, sexo, estado = mejor_soldado
        tiempo_actual = time.time()

        if estado == 'Baja':
            return {
                "status": "alerta_baja", 
                "nombre": f"{rango} {nombre} {apellidos}", 
                "novedad": "baja",
                "cedula": cedula,
                "sexo": sexo
            }

        if cedula != ultima_cedula or tiempo_actual - ultimo_tiempo > 10:
            mensaje = registrar_asistencia(cedula)
            ultima_cedula = cedula
            ultimo_tiempo = tiempo_actual
        else:
            mensaje = "ya_registro"

        return {
            "status": "exito", 
            "nombre": f"{rango} {nombre} {apellidos}", 
            "novedad": mensaje,
            "cedula": cedula,
            "sexo": sexo
        }
    else:
        return {"status": "desconocido"}