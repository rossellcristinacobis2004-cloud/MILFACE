# MilFace

## Sistema de Control de Asistencia Militar mediante Reconocimiento Facial

MilFace es una aplicación web desarrollada para la automatización del control de asistencia del personal militar mediante técnicas de reconocimiento facial. El sistema permite registrar entradas y salidas de forma automatizada, gestionar información del personal y generar reportes de asistencia, reduciendo errores humanos y optimizando los procesos administrativos.

Este proyecto fue desarrollado como parte de la carrera de Ingeniería de Sistemas en la Universidad Nacional Experimental Politécnica de la Fuerza Armada Nacional Bolivariana (UNEFA).

---

# Objetivo General

Desarrollar un sistema web de reconocimiento facial que permita automatizar el proceso de control de asistencia del personal militar, garantizando rapidez, seguridad y confiabilidad en el registro de información.

---

# Funcionalidades Principales

* Registro de personal militar.
* Captura y procesamiento de imágenes faciales.
* Reconocimiento facial automático.
* Registro de entradas y salidas.
* Gestión de asistencia.
* Administración de usuarios.
* Generación de reportes.
* Auditoría de bajas del sistema.
* Gestión de configuraciones internas.

# Instalación

Clonar el repositorio:

```bash
git clone URL_DEL_REPOSITORIO
```

Ingresar al directorio:

```bash
cd MilFace
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar el sistema:

```bash
python app.py
```

---

# Variables de Entorno

El proyecto utiliza un archivo `.env.example` como referencia para la configuración local.

Ejemplo:

```env
DATABASE_NAME=milfaces.db
PORT=5000
DEBUG=False
```

---

# Arquitectura del Sistema

```mermaid
flowchart LR

 subgraph Client[" Cliente (Frontend JS)"]
        HTML5["HTML5 + CSS3 + Bootstrap"]
        JS["JavaScript"]
        Camara["📷 Cámara Web"]
  end

 subgraph FacialAnalysis[" Reconocimiento Facial"]
        Cascada["Detección Facial"]
        OpenCV["OpenCV"]
        LIBH["Reconocimiento"]
        NumPy["NumPy"]
  end

 subgraph Backend[" Backend Flask"]
        API["REST API"]
        Fetch["Fetch API"]
        DecoLog["Seguridad"]
        ConfigSec["Configuración"]
  end

 subgraph Database[" Base de Datos"]
        SQL["SQLite3"]
        Table1["Personal Militar"]
        Table2["Asistencia"]
        Table3["Configuraciones"]
  end

 subgraph Reports[" Reportes"]
        ReportModule["Pandas + OpenPyXL"]
  end

    HTML5 --> Camara
    Camara --> Cascada
    Camara --> JS
    JS --> Fetch
    Cascada --> OpenCV
    OpenCV --> LIBH
    LIBH --> NumPy
    NumPy --> API
    Fetch --> API
    API --> DecoLog
    API --> ConfigSec
    API --> SQL
    SQL --> Table1
    SQL --> Table2
    SQL --> Table3
    ReportModule --> API
```

---

#  Modelo Entidad Relación

```mermaid
erDiagram

    SOLDADOS ||--o{ ASISTENCIA : registra
    SOLDADOS ||--o{ AUDITORIA_BAJAS : tiene_historial

    SOLDADOS {
        int id PK
        string nombre
        string apellidos
        string cedula
        string rango
        string sexo
        string tipo_sangre
        string foto_frente
        string foto_derecha
        string foto_izquierda
        string estado
    }

    ASISTENCIA {
        int id PK
        int id_soldado FK
        string fecha
        string hora_entrada
        string hora_salida
    }

    AUDITORIA_BAJAS {
        int id PK
        string cedula FK
        string razon
        string fecha
    }

    CONFIGURACIONES {
        string clave PK
        string valor
    }
```

---

# Diagrama de Secuencia

```mermaid
sequenceDiagram

    participant Comandante as Comandante/Administrador
    participant Frontend
    participant Backend as Backend Flask
    participant ReconocimientoFacial
    participant BaseDatos

    Note over Comandante,BaseDatos: Inicio de Sesión

    Comandante->>Frontend: Ingresa credenciales
    Frontend->>Backend: Enviar credenciales
    Backend->>ReconocimientoFacial: Validar usuario
    ReconocimientoFacial->>BaseDatos: Consultar identidad
    BaseDatos-->>Backend: Resultado
    Backend-->>Frontend: Acceso permitido o denegado

    Note over Comandante,BaseDatos: Registro de Asistencia

    Comandante->>Frontend: Activar registro
    Frontend->>Backend: Solicitar registro
    Backend->>ReconocimientoFacial: Procesar rostro
    ReconocimientoFacial-->>Backend: Identidad validada
    Backend->>BaseDatos: Registrar asistencia
    BaseDatos-->>Backend: Confirmación
    Backend-->>Frontend: Resultado

    Note over Comandante,BaseDatos: Consulta de Asistencias

    Comandante->>Frontend: Consultar asistencias
    Frontend->>Backend: Solicitar registros
    Backend->>BaseDatos: Obtener datos
    BaseDatos-->>Backend: Registros
    Backend-->>Frontend: Mostrar información
```

---

# Control de Calidad

El proyecto implementa:

* Protección de la rama principal (`main`).
* Pull Requests obligatorios.
* Revisión previa de cambios.
* Conventional Commits.
* GitFlow simplificado.
* Pipeline CI/CD mediante GitHub Actions.

---

# Estado del Proyecto

En desarrollo activo.
Actualmente se encuentra en fase de optimización y fortalecimiento de los módulos de reconocimiento facial, control de asistencia y generación de reportes.

---

# Autor
Estudiante de Ingeniería de Sistemas
Universidad Nacional Experimental Politécnica de la Fuerza Armada Nacional Bolivariana (UNEFA)

---

## Documentación Técnica
Para generar la documentación autogenerada del código, ejecuta en la terminal:
`pdoc app.py -o documentacion/`
