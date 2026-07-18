# RUNBOOK — MILFACE Sistema de Reconocimiento Facial Militar

> **Doc-as-Code** | Versión: 6.0.0 | Última actualización: 2026-07-18  
> Este documento es la guía de primeros auxilios operativos del sistema MILFACE.  
> En caso de incidente, siga las fases en orden estricto.

---

## Información del Sistema

| Campo | Valor |
|---|---|
| **Sistema** | MILFACE — Reconocimiento Facial Militar |
| **Stack** | Python 3.11 · Flask · SQLite · Gunicorn · Docker |
| **Repositorio** | https://github.com/rossellcristinacobis2004-cloud/MILFACE |
| **Producción** | Render Web Service (rama `main`) |
| **Health Check** | `GET /health` |
| **Contacto L3** | Administrador del repositorio GitHub |

---

## Fase #1 — Diagnóstico: Verificación del Estado del Sistema

> Ejecute estos pasos **primero** ante cualquier incidente. No escale sin completarlos.

### 1.1 Verificar salud del sistema (Health Check)

```bash
# Producción
curl -s https://<tu-app>.onrender.com/health | python3 -m json.tool

# Local con Docker
curl -s http://localhost:5000/health | python3 -m json.tool
```

**Respuesta esperada (sistema sano):**
```json
{
  "status": "ok",
  "sistema": "MILFACE - Sistema de Reconocimiento Facial Militar",
  "version": "6.0.0",
  "timestamp": "2026-07-18T21:00:00Z",
  "componentes": {
    "base_de_datos": "ok",
    "api": "ok"
  }
}
```

**Si `status` es `"degradado"` o el endpoint no responde** → continúe a Fase #2.

---

### 1.2 Verificar estado del contenedor Docker

```bash
# Ver estado del contenedor
docker ps -a --filter name=milface_app

# Ver últimas 50 líneas de logs (formato JSON estructurado)
docker logs milface_app --tail 50

# Filtrar solo errores
docker logs milface_app --tail 100 2>&1 | grep '"level":"ERROR"'

# Ver política de reinicio activa
docker inspect milface_app --format '{{.HostConfig.RestartPolicy.Name}}'
# Resultado esperado: unless-stopped
```

### 1.3 Verificar logs estructurados (Correlation ID)

```bash
# Buscar un incidente por su Correlation ID
docker logs milface_app 2>&1 | grep "CORRELATION-ID-AQUI"

# Ver todos los eventos de error en los últimos logs
docker logs milface_app 2>&1 | grep '"level":"ERROR"' | python3 -m json.tool
```

### 1.4 Verificar base de datos

```bash
# Dentro del contenedor
docker exec -it milface_app python3 -c "
import sqlite3
conn = sqlite3.connect('milfaces.db')
print('Tablas:', conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall())
print('Soldados:', conn.execute('SELECT COUNT(*) FROM soldados').fetchone()[0])
conn.close()
print('Base de datos: OK')
"
```

### 1.5 Verificar pipeline CI/CD (GitHub Actions)

```
URL: https://github.com/rossellcristinacobis2004-cloud/MILFACE/actions
```

- Pestaña **Actions** → verificar que el último workflow esté en ✅ verde
- Si está en ❌ rojo → revisar los logs del paso fallido antes de continuar

---

## Fase #2 — Protocolo ante Caídas: Contención y Escalado

> Aplique el nivel correcto según la severidad. **No salte niveles** sin agotar el anterior.

### Nivel L1 — Operador (Tiempo máximo: 5 minutos)

**Síntomas**: El sistema no responde, error 502/503, contenedor caído.

```bash
# Paso 1: Reiniciar el contenedor
docker restart milface_app

# Paso 2: Esperar 30 segundos y verificar salud
sleep 30 && curl -s http://localhost:5000/health

# Paso 3: Si persiste, forzar recreación del contenedor
docker compose down
docker compose up -d

# Paso 4: Confirmar que la política de auto-recuperación está activa
docker inspect milface_app --format '{{.HostConfig.RestartPolicy.Name}}'
```

**Si el sistema se recupera** → documentar el incidente con el Correlation ID de los logs y cerrar. ✅  
**Si NO se recupera en 5 minutos** → escalar a L2.

---

### Nivel L2 — Técnico de Soporte (Tiempo máximo: 20 minutos)

**Síntomas**: L1 no resolvió, errores persistentes en logs, BD corrupta o inaccesible.

```bash
# Paso 1: Inspeccionar logs detallados
docker logs milface_app --tail 200 2>&1 | grep -E '"level":"(ERROR|WARNING)"'

# Paso 2: Verificar espacio en disco
df -h

# Paso 3: Verificar integridad de la base de datos
docker exec -it milface_app python3 -c "
import sqlite3
conn = sqlite3.connect('milfaces.db')
result = conn.execute('PRAGMA integrity_check').fetchone()
print('Integridad BD:', result[0])  # Debe ser 'ok'
conn.close()
"

# Paso 4: Si la BD está corrupta, restaurar desde respaldo (ver Fase #3)

# Paso 5: Reconstruir la imagen Docker desde cero
docker compose down
docker compose build --no-cache
docker compose up -d
```

**Si el sistema se recupera** → documentar y cerrar. ✅  
**Si NO se recupera en 20 minutos** → escalar a L3.

---

### Nivel L3 — Administrador / Responsable del Proyecto (Sin límite de tiempo)

**Síntomas**: Falla total, brecha de seguridad sospechada, corrupción de datos.

**Acciones L3:**

1. **Poner el sistema en mantenimiento** (opcional, si hay página de mantenimiento):
   ```bash
   # Detener el servicio para proteger datos
   docker compose down
   ```

2. **Revisar el historial completo de eventos**:
   ```bash
   docker logs milface_app > incidente_$(date +%Y%m%d_%H%M%S).log
   ```

3. **Analizar todos los Correlation IDs de error** para detectar patrones de ataque:
   ```bash
   cat incidente_*.log | grep '"level":"ERROR"' | python3 -m json.tool
   ```

4. **Si hay sospecha de brecha de seguridad**:
   - Rotar `SECRET_KEY` y `LLAVE_MAESTRA` en las variables de entorno de Render/GitHub
   - Hacer `git push` a `main` para re-desplegar con nuevas credenciales

5. **Proceder con recuperación total** → ver **Fase #3**.

---

## Fase #3 — Recuperación ante Desastres: Restauración desde Cero

> Aplica la **Regla 3-2-1 de Respaldos**: 3 copias, 2 medios diferentes, 1 fuera del sitio.

### Regla 3-2-1 para MILFACE

| Copia | Medio | Ubicación |
|---|---|---|
| **Copia 1** (Primaria) | Volumen Docker local | Servidor de producción |
| **Copia 2** (Secundaria) | Archivo `.db` exportado | Drive / NAS local del operador |
| **Copia 3** (Off-site) | Backup en nube | Google Drive / Dropbox / S3 |

---

### 3.1 Crear respaldo antes de cualquier operación destructiva

```bash
# Respaldar la base de datos (ejecutar SIEMPRE antes de restaurar)
FECHA=$(date +%Y%m%d_%H%M%S)
docker exec milface_app sqlite3 milfaces.db ".backup /app/backup_milfaces_${FECHA}.db"
docker cp milface_app:/app/backup_milfaces_${FECHA}.db ./backups/

# Respaldar carpeta de fotos biométricas
docker cp milface_app:/app/fotos ./backups/fotos_${FECHA}/

echo "Respaldo creado: backup_milfaces_${FECHA}.db"
```

### 3.2 Procedimiento de restauración desde cero

```bash
# PASO 1: Clonar el repositorio limpio
git clone https://github.com/rossellcristinacobis2004-cloud/MILFACE.git
cd MILFACE

# PASO 2: Crear el archivo .env con las variables de entorno
# ⚠️  NUNCA commitear este archivo. Las credenciales deben estar en el servidor.
cat > .env << EOF
SECRET_KEY=TU_SECRET_KEY_AQUI
LLAVE_MAESTRA=TU_LLAVE_MAESTRA_AQUI
DATABASE_URL=milfaces.db
FLASK_DEBUG=0
EOF

# PASO 3: Construir la imagen Docker
docker compose build --no-cache

# PASO 4: Levantar el sistema (la BD se inicializa automáticamente)
docker compose up -d

# PASO 5: Verificar que el sistema está sano
sleep 40  # Esperar inicio de Gunicorn
curl -s http://localhost:5000/health

# PASO 6: Restaurar base de datos desde respaldo
docker cp ./backups/backup_milfaces_FECHA.db milface_app:/app/milfaces.db
docker restart milface_app

# PASO 7: Restaurar fotos biométricas
docker cp ./backups/fotos_FECHA/. milface_app:/app/fotos/

# PASO 8: Verificación final de integridad
docker exec milface_app python3 -c "
import sqlite3
conn = sqlite3.connect('milfaces.db')
print('Soldados restaurados:', conn.execute('SELECT COUNT(*) FROM soldados').fetchone()[0])
print('Master:', conn.execute('SELECT nombre FROM master LIMIT 1').fetchone())
print('Integridad:', conn.execute('PRAGMA integrity_check').fetchone()[0])
conn.close()
"
```

### 3.3 Verificación post-restauración

```bash
# Health check final
curl -s http://localhost:5000/health | python3 -m json.tool

# El sistema debe responder:
# { "status": "ok", "componentes": { "base_de_datos": "ok", "api": "ok" } }
```

**Sistema restaurado** ✅ — Documentar fecha, hora, Correlation IDs del incidente y cierre.

---

## Referencias Rápidas

| Acción | Comando |
|---|---|
| Ver estado del sistema | `curl http://localhost:5000/health` |
| Ver logs en vivo | `docker logs -f milface_app` |
| Reiniciar contenedor | `docker restart milface_app` |
| Reconstruir imagen | `docker compose build --no-cache` |
| Levantar sistema | `docker compose up -d` |
| Detener sistema | `docker compose down` |
| Acceder al contenedor | `docker exec -it milface_app bash` |
| Pipeline en GitHub | https://github.com/rossellcristinacobis2004-cloud/MILFACE/actions |
