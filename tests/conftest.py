import sys
import os

# Agrega la raíz del proyecto al PYTHONPATH para que pytest pueda
# importar app.py sin importar desde qué directorio se ejecute.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
