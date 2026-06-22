# Usar una imagen oficial de Python ligera
FROM python:3.11-slim

# Instalar dependencias del sistema operativo que OpenCV necesita
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar el archivo de dependencias primero (optimización de Docker)
COPY requirements.txt .

# Instalar las librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto al contenedor
COPY . .

# Exponer el puerto que usa Flask por defecto
EXPOSE 5000

# Comando para arrancar el servidor web (Gunicorn es recomendado para producción)
RUN pip install gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
