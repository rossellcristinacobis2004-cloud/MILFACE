import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cargar variables del entorno desde el archivo .env local
load_dotenv(os.path.join(BASE_DIR, '.env'))

DATABASE = os.path.join(BASE_DIR, "milfaces.db")
FOTOS_DIR = os.path.join(BASE_DIR, "fotos")
ENCODINGS_DIR = os.path.join(BASE_DIR, "encodings")

# Ajustes de Seguridad leyendo de .env
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_por_defecto")
LLAVE_MAESTRA = os.getenv("LLAVE_MAESTRA", "milface_fallback")