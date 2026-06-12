import pytest
from app import app, conectar

@pytest.fixture
def cliente():
    # Prepara la app en modo "Testing"
    app.config['TESTING'] = True
    with app.test_client() as cliente:
        yield cliente

# Prueba 1: Verificar que la página principal carga bien
def test_inicio_carga_correctamente(cliente):
    respuesta = cliente.get('/')
    assert respuesta.status_code == 302 # 302 porque redirige al login si no estás logueado

# Prueba 2: Verificar la conexión a la Base de Datos
def test_conexion_bd():
    conexion = conectar()
    assert conexion is not None
    conexion.close()

# Prueba 3: Intentar login con llave incorrecta
def test_login_invalido(cliente):
    respuesta = cliente.post('/login', data={'llave': 'clave_super_falsa'})
    # Como la llave es mala, no debería dejarnos entrar, sino redirigir (302)
    assert respuesta.status_code == 302

# Prueba 4: Verificar que el logout redirige al login
def test_logout_redirige(cliente):
    respuesta = cliente.get('/logout')
    # Debería redirigir al login
    assert respuesta.status_code == 302

# Prueba 5: Verificar que una ruta protegida redirige sin login
def test_ruta_protegida_sin_login(cliente):
    respuesta = cliente.get('/registro_master')
    # Debería redirigir al login
    assert respuesta.status_code == 302
