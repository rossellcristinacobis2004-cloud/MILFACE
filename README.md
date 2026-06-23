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
flowchart TB
subgraph Frontend["Cliente Web"]
    UI["HTML5 + CSS3 + Bootstrap"]
    JS["JavaScript ES6"]
    Cam["WebRTC / Cámara Web"]
end

subgraph Backend["Backend Flask"]
    Router["REST API - app.py"]
    Auth["Autenticación y Control de Acceso"]
    Config["Variables de Entorno (.env)"]
end

subgraph CoreAI["Motor de Reconocimiento Facial"]
    Decoder["Decodificación Base64<br/>Frames recibidos"]
    Haar["Haar Cascade<br/>Detección facial"]
    Numpy["NumPy<br/>Matrices y Procesamiento"]
    LBPH["LBPH Recognizer<br/>Identificación Facial"]
end

subgraph Database["Persistencia"]
    SQLite[("SQLite3")]
    Fotos["Repositorio de Fotografías"]
end

subgraph Analytics["Reportes"]
    Pandas["Pandas + OpenPyXL"]
end

UI --- JS
JS --- Cam

Router --- Auth
Router --- Config

Decoder --> Haar
Haar --> Numpy
Numpy --> LBPH

SQLite --- Fotos

JS -- "1. Captura Frame" --> Cam
JS -- "2. POST /api/reconocer<br/>Imagen Base64" --> Router
Router -- "3. Envía Imagen" --> Decoder

LBPH -- "4. Resultado de Identificación" --> Router
Router -- "5. Consulta / Actualiza Registros" --> SQLite
Router -- "6. Lectura de Fotografías" --> Fotos
Router -- "7. Respuesta JSON" --> JS

Router --> Pandas

classDef frontend fill:#f0f9ff,stroke:#38bdf8,stroke-width:2px,color:#1e293b
classDef backend fill:#f5f3ff,stroke:#a855f7,stroke-width:2px,color:#1e293b
classDef ai fill:#fef2f2,stroke:#ef4444,stroke-width:2px,color:#1e293b
classDef db fill:#f0fdf4,stroke:#22c55e,stroke-width:2px,color:#1e293b
classDef tools fill:#fefce8,stroke:#eab308,stroke-width:2px,color:#1e293b

class UI,JS,Cam frontend
class Router,Auth,Config backend
class Decoder,Haar,Numpy,LBPH ai
class SQLite,Fotos db
class Pandas tools
```
---

#  Modelo Entidad Relación
```mermaid
erDiagram
    %% Relaciones

    SOLDADOS ||--o{ ASISTENCIA : "genera"
    SOLDADOS ||--o{ AUDITORIA_BAJAS : "posee historial"
    MASTER ||--o{ HISTORIAL_MASTER : "genera"

    SOLDADOS {
        INTEGER id PK
        TEXT nombre
        TEXT apellidos
        TEXT cedula UK
        TEXT rango
        TEXT sexo
        TEXT tipo_sangre
        TEXT foto_frente
        TEXT foto_derecha
        TEXT foto_izquierda
        TEXT estado
    }

    ASISTENCIA {
        INTEGER id PK
        INTEGER id_soldado FK
        TEXT fecha
        TEXT hora_entrada
        TEXT hora_salida
    }

    AUDITORIA_BAJAS {
        INTEGER id PK
        INTEGER id_soldado FK
        TEXT razon
        TEXT fecha
    }

    MASTER {
        INTEGER id PK
        TEXT nombre
        TEXT apellidos
        TEXT cedula UK
        TEXT componente
        TEXT rango
        TEXT foto_frente
        TEXT foto_derecha
        TEXT foto_izquierda
        TEXT fecha_registro
    }

    HISTORIAL_MASTER {
        INTEGER id PK
        INTEGER id_master FK
        TEXT fecha_inicio
        TEXT fecha_fin
        TEXT motivo_relevo
    }

    CONFIGURACIONES {
        TEXT clave PK
        TEXT valor
    }
```

---

# Modelado de Secuencia
```mermaid
sequenceDiagram

    participant Usuario as Comandante/Administrador
    participant Frontend
    participant Backend as Flask Backend
    participant Reconocimiento as Motor reconocimiento.py
    participant MasterBiometrico as Módulo Master (OpenCV/LBPH)
    participant DB as Base de Datos SQLite

    %% ================= LOGIN =================
    Note over Usuario,DB: 🔐 Autenticación del sistema

    Usuario->>Frontend: Ingresa llave maestra
    Frontend->>Backend: POST /login
    Backend->>DB: Consultar master / validación de sesión
    DB-->>Backend: Resultado
    Backend-->>Frontend: session['logged_in'] o error

    %% ================= REGISTRO SOLDADO =================
    Note over Usuario,DB: 👤 Registro de soldados

    Usuario->>Frontend: Registrar soldado
    Frontend->>Backend: POST /registrar
    Backend->>DB: INSERT soldados
    DB-->>Backend: Confirmación
    Backend-->>Frontend: Redirección a captura de fotos

    Frontend->>Backend: POST /api/guardar_foto (Base64 + posición)
    Backend->>DB: UPDATE soldados (foto_frente/derecha/izquierda)
    Backend-->>Frontend: OK

    %% ================= RECONOCIMIENTO =================
    Note over Usuario,DB: 📸 Reconocimiento facial asistencia

    Usuario->>Frontend: Activar cámara
    Frontend->>Frontend: Captura frame (WebRTC)
    Frontend->>Backend: POST /api/reconocer (imagen Base64)

    Backend->>Reconocimiento: reconocer_imagen(frame)
    Reconocimiento->>DB: Consultar soldados registrados
    DB-->>Reconocimiento: Dataset de rostros

    Reconocimiento-->>Backend: Resultado (identidad + confianza)
    Backend->>DB: INSERT/UPDATE asistencia
    DB-->>Backend: Confirmación
    Backend-->>Frontend: JSON resultado

    %% ================= CONSULTA =================
    Note over Usuario,DB: 📊 Consulta de asistencia

    Usuario->>Frontend: Ver asistencia
    Frontend->>Backend: GET /asistencia
    Backend->>DB: SELECT + JOIN soldados
    DB-->>Backend: Registros
    Backend-->>Frontend: Lista de asistencia
```

---
## Diagramas de flujo 
## 1. Flujo General del Sistema

```mermaid
flowchart TD
    A([ Usuario accede al sistema]) --> B{¿Sesión activa?}
    B -- Sí --> F[ Panel de Control]
    B -- No --> C[ Pantalla de Login]

    C --> D{¿Existe un Máster<br/>registrado?}
    D -- No --> E[ Registro de Máster]
    D -- Sí --> G[ Ingresar Llave Maestra]

    G --> H{¿Llave correcta?}
    H -- No --> I[ Error: Protocolo<br/>de bloqueo activo]
    I --> C
    H -- Sí --> J[ Crear sesión]
    J --> K[ IA: Saludo de Bienvenida]
    K --> F

    F --> L{Navegación por<br/>Menú Lateral}
    L --> M[ Registrar Personal]
    L --> N[ Galería Militar]
    L --> O[ Asistencia]
    L --> P[ Reportes]
    L --> Q[ Master Ajustes]
    L --> R[ Escaneo Facial<br/>Tecla J]

    F --> S[ Apagar Sistema]
    S --> T[ Cerrar Sesión]
    T --> C

    style A fill:#070b14,stroke:#00f2fe,color:#f0f8ff
    style C fill:#070b14,stroke:#ff2a5f,color:#f0f8ff
    style F fill:#070b14,stroke:#04d976,color:#f0f8ff
    style I fill:#070b14,stroke:#ff2a5f,color:#ff2a5f
    style J fill:#070b14,stroke:#04d976,color:#04d976
    style K fill:#070b14,stroke:#00f2fe,color:#00f2fe
```

---
## 2. Sistema Máster (Administrador)

```mermaid
flowchart TD
    subgraph REG[" REGISTRO INICIAL DEL MÁSTER"]
        A([No existe Máster]) --> B[Formulario de Registro]
        B --> C[Ingresar: Nombre, Apellidos,<br/>Cédula, Componente, Rango]
        C --> D{¿Campos completos?}
        D -- No --> E[ Flash: Campos obligatorios]
        E --> B
        D -- Sí --> F[ Guardar en tabla master]
        F --> G[ Captura Biométrica]
        G --> H[Foto Frente]
        G --> I[Foto Derecha]
        G --> J[Foto Izquierda]
        H & I & J --> K[Fotos guardadas en /fotos]
        K --> L[ Ir a Verificación]
    end

    subgraph VER[" VERIFICACIÓN BIOMÉTRICA"]
        L --> M[Activar cámara web]
        M --> N[Capturar frame en vivo]
        N --> O[Crear reconocedor LBPH<br/>con fotos del Máster]
        O --> P[Comparar rostro vs fotos]
        P --> Q{¿Confianza < 95?}
        Q -- Sí --> R[ Verificado<br/>Revelar Llave Maestra]
        Q -- No --> S[ No reconocido<br/>Reintentar]
        S --> N
    end

    subgraph REL[" RELEVO DE MANDO"]
        direction TB
        T{¿Máster presente?}
        T -- "Sí (Escenario 1)" --> U[Verificación biométrica<br/>del Máster actual]
        U --> V{¿Verificado?}
        V -- Sí --> W[Archivar Máster actual<br/>en historial_master]
        W --> X[Motivo: TRASPASO]
        X --> Y[Eliminar Máster de tabla]
        Y --> Z[Registrar nuevo Máster]

        T -- "No (Escenario 2)" --> AA[ Emergencia]
        AA --> AB[Ingresar código de emergencia]
        AB --> AC{¿Código correcto?}
        AC -- No --> AD[ Acceso Denegado]
        AC -- Sí --> AE[Archivar Máster actual<br/>en historial_master]
        AE --> AF[Motivo: EMERGENCIA]
        AF --> AG[Eliminar Máster de tabla]
        AG --> Z
    end

    style REG fill:#0d1423,stroke:#00f2fe,color:#f0f8ff
    style VER fill:#0d1423,stroke:#04d976,color:#f0f8ff
    style REL fill:#0d1423,stroke:#f8c102,color:#f0f8ff
```

---

## 3. Registro y Gestión de Personal Militar

```mermaid
flowchart TD
    subgraph REGISTRO[" REGISTRO DE SOLDADO"]
        A([Registrar Personal]) --> B[Formulario de Datos]
        B --> C["Ingresar: Nombre, Apellidos,<br/>Cédula, Rango, Sexo,<br/>Tipo de Sangre"]
        C --> D{¿Cédula ya existe?}
        D -- "Sí (Activo)" --> E[" Flash: Ya registrado"]
        D -- "Sí (Baja)" --> F[" Flash: Está de Baja<br/>Reincorporar desde Galería"]
        D -- No --> G[ INSERT en tabla soldados]
        G --> H[ Captura Biométrica]
        H --> I[Foto Frente]
        H --> J[Foto Derecha]
        H --> K[Foto Izquierda]
        I & J & K --> L[Guardar en /fotos<br/>Resetear modelo LBPH]
    end

    subgraph GALERIA[" GALERÍA MILITAR"]
        M([Ver Galería]) --> N[Grid de tarjetas<br/>con foto y datos]
        N --> O{Acción sobre soldado}
        O --> P[ Dar de Baja]
        O --> Q[ Reincorporar]

        P --> R[Ingresar justificación]
        R --> S["Estado → 'Baja'"]
        S --> T[Registro en<br/>auditoria_bajas]

        Q --> U[Ingresar Llave Maestra]
        U --> V{¿Llave válida?}
        V -- Sí --> W["Estado → NULL (Activo)"]
        W --> X[Resetear modelo LBPH]
        V -- No --> Y[ Acceso Denegado]
    end

    subgraph MASTER_GAL[" SECCIÓN MÁSTER EN GALERÍA"]
        Z[Mostrar Máster Activo]
        AA[Historial de Ex-Másters]
    end

    style REGISTRO fill:#0d1423,stroke:#00f2fe,color:#f0f8ff
    style GALERIA fill:#0d1423,stroke:#04d976,color:#f0f8ff
    style MASTER_GAL fill:#0d1423,stroke:#f8c102,color:#f0f8ff
```

---

## 4. Reconocimiento Facial en Tiempo Real

```mermaid
flowchart TD
    A([" Activar Escáner<br/>(Tecla J o Botón)"]) --> B[" IA: Iniciando cámaras<br/>de seguridad biométrica"]
    B --> C[Abrir cámara web<br/>en ventana flotante]
    C --> D[Capturar frame<br/>cada 1.5 segundos]

    D --> E{¿Modelo LBPH<br/>entrenado?}
    E -- No --> F[Entrenar modelo con<br/>fotos de todos los soldados]
    F --> G{¿Hay datos para<br/>entrenar?}
    G -- No --> H[ Error: Sin datos]
    G -- Sí --> I[Modelo listo]
    E -- Sí --> I

    I --> J[Convertir frame a<br/>escala de grises]
    J --> K[Detectar rostros<br/>con Haar Cascade]
    K --> L[Procesar cada rostro:<br/>GaussianBlur + CLAHE]
    L --> M[Redimensionar a 150x150]
    M --> N["Predecir con LBPH<br/>(label, confianza)"]

    N --> O{¿Confianza < 75?}
    O -- No --> P[" DESCONOCIDO<br/>Rostro no registrado"]
    O -- Sí --> Q[Identificar soldado<br/>en la BD]

    Q --> R{¿Estado del soldado?}
    R -- "Baja" --> S[" ALERTA MÁXIMA<br/>Acceso Denegado"]
    S --> T[" IA: Alerta de seguridad<br/>extrema. Personal de baja<br/>detectado (voz grave)"]

    R -- "Activo" --> U{¿Mismo soldado<br/>en últimos 10s?}
    U -- Sí --> V[Ignorar<br/>ya registrado]
    U -- No --> W[Registrar Asistencia]

    W --> X{¿Registro hoy?}
    X -- "No existe" --> Y[" ENTRADA registrada"]
    Y --> Z[" IA: Entrada registrada<br/>para Nombre, personal M/F"]
    X -- "Tiene entrada<br/>sin salida" --> AA[" SALIDA registrada"]
    AA --> AB[" IA: Salida registrada<br/>para Nombre, personal M/F"]
    X -- "Ya tiene entrada<br/>y salida" --> AC[Sin acción<br/>ya completó ciclo]

    style A fill:#070b14,stroke:#00f2fe,color:#f0f8ff
    style S fill:#070b14,stroke:#ff2a5f,color:#ff2a5f
    style Y fill:#070b14,stroke:#04d976,color:#04d976
    style AA fill:#070b14,stroke:#f8c102,color:#f8c102
    style P fill:#070b14,stroke:#ff2a5f,color:#ff2a5f
```

---

## 5. Módulo de Reportes e Inteligencia

```mermaid
flowchart TD
    A([ Reportes]) --> B[Cargar estadísticas<br/>desde la BD]

    B --> C[Total de Soldados Activos]
    B --> D["Distribución por Género<br/>(% Masculino / % Femenino)"]
    B --> E["Promedio Diario<br/>(Entradas y Salidas)"]
    B --> F[Distribución por Rango]
    B --> G[Distribución por Tipo de Sangre]
    B --> H[Alertas Activas]

    H --> I{"Personal sin<br/>marcar salida"}
    I -- "Fecha = Hoy" --> J[" Alerta Normal<br/>(Aún en servicio)"]
    I -- "Fecha < Hoy" --> K[" Alerta Crítica<br/>(Sin salida de día anterior)"]

    K --> L{Acción del Máster}
    L --> M["Registrar Salida Manual<br/>(hora actual del servidor)"]
    M --> N[" Flash: Cierre de Guardia<br/>Manual exitoso"]

    A --> O[ Exportar a Excel]
    O --> P[Generar archivo .xlsx<br/>con openpyxl + pandas]
    P --> Q[Descargar:<br/>Reporte_Asistencia.xlsx]

    style A fill:#070b14,stroke:#00f2fe,color:#f0f8ff
    style K fill:#070b14,stroke:#ff2a5f,color:#ff2a5f
    style J fill:#070b14,stroke:#f8c102,color:#f8c102
    style N fill:#070b14,stroke:#04d976,color:#04d976
    style Q fill:#070b14,stroke:#04d976,color:#04d976
```

---

##  6. Configuración del Sistema (Settings)

```mermaid
flowchart TD
    A([ Master Ajustes]) --> B[Panel de Configuración Global]

    B --> C[" Experiencia Visual"]
    C --> D{"Seleccionar Tema"}
    D --> E[" Modo Táctico<br/>(Oscuro + Cyan)"]
    D --> F[" Modo Ejecutivo<br/>(Claro + Violeta)"]

    B --> G[" Sintetizador de Voz"]
    G --> H["Editar frase de saludo<br/>(textarea personalizable)"]

    E & F & H --> I[" Aplicar Cambios Globales"]
    I --> J[UPDATE en tabla<br/>configuraciones]
    J --> K[" Flash: Configuraciones<br/>actualizadas permanentemente"]

    B --> L[" Protocolo de<br/>Relevo de Mando"]
    L --> M[ Ir a /relevo_mando]

    style A fill:#070b14,stroke:#00f2fe,color:#f0f8ff
    style E fill:#070b14,stroke:#00f2fe,color:#00f2fe
    style F fill:#f0f4f8,stroke:#9b51e0,color:#9b51e0
    style K fill:#070b14,stroke:#04d976,color:#04d976
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

## Documentación Técnica
Para generar la documentación autogenerada del código, ejecuta en la terminal:
`pdoc app.py -o documentacion/`

---
# Autor
Estudiante de Ingeniería de Sistemas
Universidad Nacional Experimental Politécnica de la Fuerza Armada Nacional Bolivariana (UNEFA)
