# ── Artefacto inmutable de producción ──────────────────────────────────────
# Avance 5: Imagen lista para producción, agnóstica al entorno.
# Las variables sensibles se inyectan desde el entorno de ejecución (NO aquí).
FROM python:3.11-slim

# Instalar dependencias del sistema operativo que OpenCV necesita
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1-mesa-glx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Variables de entorno de producción (sin credenciales)
ENV FLASK_DEBUG=0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Crear directorio de trabajo
WORKDIR /app

# Copiar el archivo de dependencias primero (optimización de caché de Docker)
COPY requirements.txt .

# Instalar las librerías de Python (gunicorn ya incluido en requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto al contenedor
COPY . .

# Exponer el puerto
EXPOSE 5000

# ── Health Check nativo de Docker (Auto-recuperación) ──────────────────────
# Docker verifica el estado cada 30s; si falla 3 veces reinicia el contenedor.
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Arrancar con Gunicorn (servidor WSGI de producción)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
