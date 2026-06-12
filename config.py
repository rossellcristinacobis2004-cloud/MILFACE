import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR, "milfaces.db")
FOTOS_DIR = os.path.join(BASE_DIR, "fotos")
ENCODINGS_DIR = os.path.join(BASE_DIR, "encodings")

# Ajustes de Seguridad
SECRET_KEY = "operacion_milface_top_secret"
LLAVE_MAESTRA = "milface2026"