import subprocess
import sys

def ejecutar_reconocimiento():
    subprocess.Popen([sys.executable, "reconocimiento.py"])