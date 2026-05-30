from flask import Flask, render_template, request, redirect, Response, send_from_directory, send_file, session, flash
from functools import wraps
import sqlite3
from datetime import date
import cv2
import os
import pandas as pd
import base64
import numpy as np
import reconocimiento
import io
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

def conectar():
    return sqlite3.connect("milfaces.db")

def init_db():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS configuraciones (
        clave TEXT PRIMARY KEY,
        valor TEXT
    )""")
    cursor.execute("INSERT OR IGNORE INTO configuraciones (clave, valor) VALUES ('tema_visual', 'dark')")
    cursor.execute("INSERT OR IGNORE INTO configuraciones (clave, valor) VALUES ('saludo_ia', 'Acceso Concedido. Bienvenido Comandante al Sistema de Inteligencia Milface.')")
    conexion.commit()
    conexion.close()

init_db()

@app.context_processor
def inject_config():
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT clave, valor FROM configuraciones")
        filas = cursor.fetchall()
        conf = {k: v for k, v in filas}
    except:
        conf = {'tema_visual': 'dark', 'saludo_ia': 'Acceso Concedido.'}
    finally:
        conexion.close()
    return dict(app_config=conf)

# ------------------ SEGURIDAD ------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya está logueado, mandarlo al inicio
    if 'logged_in' in session:
        return redirect('/')

    if request.method == 'POST':
        llave = request.form.get('llave')
        if llave == config.LLAVE_MAESTRA:
            session['logged_in'] = True
            return redirect('/')
        else:
            flash("Llave maestra incorrecta. Protocolo de bloqueo activo.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ------------------ CAMARA (WEB) ------------------

@app.route('/api/guardar_foto', methods=['POST'])
@login_required
def api_guardar_foto():
    data = request.json
    cedula = data.get("cedula")
    posicion = data.get("posicion")
    imagen_base64 = data.get("imagen")

    if not cedula or not posicion or not imagen_base64:
        return {"status": "error", "mensaje": "Faltan datos"}, 400

    # Decodificar Base64
    header, encoded = imagen_base64.split(",", 1)
    imagen_data = base64.b64decode(encoded)
    np_arr = np.frombuffer(imagen_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if not os.path.exists("fotos"):
        os.makedirs("fotos")

    ruta = f"fotos/{cedula}_{posicion}.jpg"
    cv2.imwrite(ruta, frame)

    conexion = conectar()
    cursor = conexion.cursor()
    if posicion == "frente":
        cursor.execute("UPDATE soldados SET foto_frente = ? WHERE cedula = ?", (ruta, cedula))
    elif posicion == "derecha":
        cursor.execute("UPDATE soldados SET foto_derecha = ? WHERE cedula = ?", (ruta, cedula))
    elif posicion == "izquierda":
        cursor.execute("UPDATE soldados SET foto_izquierda = ? WHERE cedula = ?", (ruta, cedula))

    # Asegurar que se vuelve a entrenar al añadir rostros
    reconocimiento.modelo_entrenado = False
    
    conexion.commit()
    conexion.close()

    return {"status": "ok"}

@app.route('/api/reconocer', methods=['POST'])
@login_required
def api_reconocer():
    data = request.json
    imagen_base64 = data.get("imagen")

    if not imagen_base64:
        return {"status": "error"}, 400

    try:
        header, encoded = imagen_base64.split(",", 1)
        imagen_data = base64.b64decode(encoded)
        np_arr = np.frombuffer(imagen_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Analizar con el motor
        resultado = reconocimiento.reconocer_imagen(frame)
        return resultado
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}, 500
# ------------------ FIN CAMARA (WEB) ------------------

#---------------ASISTENCIA------------------
@app.route("/asistencia")
@login_required
def ver_asistencia():
    conexion = conectar()
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT asistencia.cedula, soldados.nombre, asistencia.fecha,
               asistencia.hora_entrada, asistencia.hora_salida
        FROM asistencia
        JOIN soldados ON asistencia.cedula = soldados.cedula
        ORDER BY asistencia.fecha DESC
    """)

    datos = cursor.fetchall()

    asistencia = []

    for fila in datos:
        if fila["hora_entrada"] and not fila["hora_salida"]:
            estado = "Dentro"
        elif fila["hora_entrada"] and fila["hora_salida"]:
            estado = "Fuera"
        else:
            estado = "Sin registro"

        asistencia.append({
            "cedula": fila["cedula"],
            "nombre": fila["nombre"],
            "fecha": fila["fecha"],
            "hora_entrada": fila["hora_entrada"],
            "hora_salida": fila["hora_salida"],
            "estado": estado
        })

    conexion.close()

    return render_template("asistencia.html", asistencia=asistencia)

# ------------------ PAGINAS ------------------

@app.route("/")
@login_required
def index():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) FROM soldados WHERE estado != 'Baja' OR estado IS NULL")
    total_soldados = cursor.fetchone()[0]

    hoy = date.today()
    cursor.execute("SELECT COUNT(*) FROM asistencia WHERE fecha = ?", (hoy,))
    asistencias_hoy = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM asistencia WHERE fecha = ? AND hora_entrada IS NOT NULL", (hoy,))
    entradas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM asistencia WHERE fecha = ? AND hora_salida IS NOT NULL", (hoy,))
    salidas = cursor.fetchone()[0]

    conexion.close()

    return render_template("index.html",
                           total_soldados=total_soldados,
                           asistencias_hoy=asistencias_hoy,
                           entradas=entradas,
                           salidas=salidas)

@app.route("/registrar", methods=["GET", "POST"])
@login_required
def registrar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        cedula = request.form["cedula"]
        rango = request.form["rango"]
        sexo = request.form["sexo"]
        tipo_sangre = request.form["tipo_sangre"]

        conexion = conectar()
        cursor = conexion.cursor()

        # Verificar si la cédula ya existe
        cursor.execute("SELECT id, estado FROM soldados WHERE cedula = ?", (cedula,))
        existente = cursor.fetchone()
        
        if existente:
            id_sol, estado_sol = existente
            if estado_sol == 'Baja':
                flash("Este soldado ya está registrado en el sistema pero está dado de Baja. Puede reincorporarlo desde la Galería Militar.", "warning")
            else:
                flash("Este soldado ya ha sido registrado con esta Cédula en el sistema.", "danger")
            conexion.close()
            return redirect("/registrar")

        try:
            cursor.execute("INSERT INTO soldados (cedula, nombre, apellidos, rango, sexo, tipo_sangre) VALUES (?, ?, ?, ?, ?, ?)",
                           (cedula, nombre, apellidos, rango, sexo, tipo_sangre))
            conexion.commit()
            conexion.close()
            return redirect(f"/registrar?cedula={cedula}")
        except sqlite3.IntegrityError:
            flash("Error de integridad de base de datos al guardar los datos.", "danger")
            conexion.close()
            return redirect("/registrar")

    return render_template("registrar.html")

@app.route("/fotos/<path:filename>")
@login_required
def servir_foto(filename):
    return send_from_directory("fotos", filename)


@app.route("/dar_baja", methods=["POST"])
@login_required
def dar_baja():
    cedula = request.form.get("cedula")
    razon = request.form.get("razon")
    if not razon or not cedula:
        flash("Justificación inválida.")
        return redirect("/soldados")
        
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE soldados SET estado = 'Baja' WHERE cedula = ?", (cedula,))
    hoy = date.today().isoformat()
    cursor.execute("INSERT INTO auditoria_bajas (cedula, razon, fecha) VALUES (?, ?, ?)", (cedula, razon, hoy))
    conexion.commit()
    conexion.close()
    
    # flash("Soldado dado de baja y registrado en auditoría.")
    return redirect("/soldados")

@app.route("/soldados")
@login_required
def ver_soldados():
    conexion = conectar()
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT cedula, nombre, apellidos, rango, foto_frente, estado FROM soldados")
    todos = cursor.fetchall()
    
    soldados = [s for s in todos if s['estado'] != 'Baja']
    soldados_baja = [s for s in todos if s['estado'] == 'Baja']
    
    conexion.close()
    return render_template("soldados.html", soldados=soldados, soldados_baja=soldados_baja)

@app.route("/reincorporar", methods=["POST"])
@login_required
def reincorporar():
    cedula = request.form.get("cedula")
    llave = request.form.get("llave")
    
    import config
    if llave == config.LLAVE_MAESTRA:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("UPDATE soldados SET estado = NULL WHERE cedula = ?", (cedula,))
        conexion.commit()
        conexion.close()
        reconocimiento.modelo_entrenado = False
        flash("Reincorporación oficial autorizada. Motor biométrico actualizado.")
    else:
        flash("❌ ACCESO DENEGADO: Credencial de Comandante Inválida.")
    
    return redirect("/soldados")

@app.route("/reporte")
@login_required
def vista_reporte():
    conexion = conectar()
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()

    # 1. Total Soldados Activos
    cursor.execute("SELECT COUNT(*) FROM soldados WHERE estado != 'Baja' OR estado IS NULL")
    total_soldados = cursor.fetchone()[0]

    # 2. Distribución de Género
    cursor.execute("SELECT sexo, COUNT(*) FROM soldados WHERE (estado != 'Baja' OR estado IS NULL) GROUP BY sexo")
    genero_data = {r[0]: r[1] for r in cursor.fetchall()}
    masculino = genero_data.get('Masculino', 0)
    femenino = genero_data.get('Femenino', 0)
    
    total_genero = masculino + femenino
    porcentaje_masc = round((masculino / total_genero) * 100, 1) if total_genero > 0 else 0
    porcentaje_fem = round((femenino / total_genero) * 100, 1) if total_genero > 0 else 0

    # 3. Promedio diario de Entradas y Salidas
    cursor.execute("SELECT COUNT(DISTINCT fecha) FROM asistencia")
    dias_operacionales = cursor.fetchone()[0] or 1 # Evitar división por cero

    cursor.execute("SELECT COUNT(*) FROM asistencia WHERE hora_entrada IS NOT NULL")
    total_entradas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM asistencia WHERE hora_salida IS NOT NULL")
    total_salidas = cursor.fetchone()[0]

    promedio_entradas = round(total_entradas / dias_operacionales, 1)
    promedio_salidas = round(total_salidas / dias_operacionales, 1)

    # 4. Distribución por Rango
    cursor.execute("SELECT rango, COUNT(*) as cant FROM soldados WHERE (estado != 'Baja' OR estado IS NULL) GROUP BY rango ORDER BY cant DESC")
    rangos = [{"rango": r["rango"], "cant": r["cant"]} for r in cursor.fetchall()]

    # 5. Distribución por Tipo de Sangre
    cursor.execute("SELECT tipo_sangre, COUNT(*) as cant FROM soldados WHERE (estado != 'Baja' OR estado IS NULL) GROUP BY tipo_sangre ORDER BY cant DESC")
    sangres = [{"tipo_sangre": r["tipo_sangre"], "cant": r["cant"]} for r in cursor.fetchall()]

    # 6. Alertas Activas (Dentro sin marcar salida)
    cursor.execute("""
        SELECT a.cedula, s.nombre, s.apellidos, s.rango, a.fecha, a.hora_entrada, a.id as asistencia_id
        FROM asistencia a
        JOIN soldados s ON a.cedula = s.cedula
        WHERE a.hora_entrada IS NOT NULL AND a.hora_salida IS NULL
        ORDER BY a.fecha DESC, a.hora_entrada DESC
    """)
    alertas_db = cursor.fetchall()
    
    # Pasar hoy para verificar si la alerta es de ayer o anterior
    from datetime import date
    hoy_str = date.today().isoformat()
    
    alertas = []
    for a in alertas_db:
        es_hoy = (a["fecha"] == hoy_str)
        alertas.append({
            "asistencia_id": a["asistencia_id"],
            "cedula": a["cedula"],
            "nombre": f"{a['rango']} {a['nombre']} {a['apellidos']}",
            "fecha": a["fecha"],
            "hora_entrada": a["hora_entrada"],
            "es_hoy": es_hoy
        })

    conexion.close()

    return render_template("reporte.html",
                           total_soldados=total_soldados,
                           masculino=masculino,
                           femenino=femenino,
                           porcentaje_masc=porcentaje_masc,
                           porcentaje_fem=porcentaje_fem,
                           promedio_entradas=promedio_entradas,
                           promedio_salidas=promedio_salidas,
                           rangos=rangos,
                           sangres=sangres,
                           alertas=alertas,
                           total_alertas=len(alertas))

@app.route("/exportar_reporte_excel")
@login_required
def exportar_excel():
    conexion = conectar()
    query = """
        SELECT asistencia.cedula as 'Cédula', soldados.nombre as 'Nombres', soldados.apellidos as 'Apellidos',
               soldados.rango as 'Rango', asistencia.fecha as 'Fecha',
               asistencia.hora_entrada as 'Hora Entrada', asistencia.hora_salida as 'Hora Salida'
        FROM asistencia
        JOIN soldados ON asistencia.cedula = soldados.cedula
        ORDER BY asistencia.fecha DESC, asistencia.hora_entrada DESC
    """
    df = pd.read_sql_query(query, conexion)
    conexion.close()

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Asistencia Real MILFACES')
    
    output.seek(0)
    return send_file(output, download_name="Reporte_Asistencia.xlsx", as_attachment=True)

@app.route("/registrar_salida_manual", methods=["POST"])
@login_required
def registrar_salida_manual():
    asistencia_id = request.form.get("asistencia_id")
    if not asistencia_id:
        flash("ID de asistencia inválido.", "danger")
        return redirect("/reporte")

    from datetime import datetime
    hora_actual = datetime.now().strftime("%H:%M:%S")

    conexion = conectar()
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    # Obtener datos de asistencia para auditoria o flash
    cursor.execute("""
        SELECT a.cedula, s.nombre, s.apellidos, s.rango 
        FROM asistencia a
        JOIN soldados s ON a.cedula = s.cedula
        WHERE a.id = ?
    """, (asistencia_id,))
    soldado = cursor.fetchone()
    
    if soldado:
        cedula, nombre, apellidos, rango = soldado
        cursor.execute("UPDATE asistencia SET hora_salida = ? WHERE id = ?", (hora_actual, asistencia_id))
        conexion.commit()
        flash(f"Cierre de Guardia Manual exitoso para {rango} {nombre} {apellidos} a las {hora_actual}.", "success")
    else:
        flash("❌ No se encontró el registro de asistencia correspondiente.", "danger")
        
    conexion.close()
    return redirect("/reporte")

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings_page():
    if request.method == "POST":
        tema = request.form.get("tema_visual", "dark")
        saludo = request.form.get("saludo_ia", "")
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("UPDATE configuraciones SET valor = ? WHERE clave = 'tema_visual'", (tema,))
        cursor.execute("UPDATE configuraciones SET valor = ? WHERE clave = 'saludo_ia'", (saludo,))
        conexion.commit()
        conexion.close()
        flash("Las configuraciones del Master han sido actualizadas permanentemente.")
        return redirect("/settings")
    return render_template("settings.html")

if __name__ == "__main__":
    app.run(debug=True)
