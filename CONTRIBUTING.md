# Guía de Contribución
## Flujo de trabajo GitFlow

El proyecto utiliza una estrategia GitFlow simplificada para organizar el desarrollo y proteger la estabilidad del código.

### Ramas principales
* main: contiene la versión estable y lista para producción.
* develop: contiene la integración de nuevas funcionalidades antes de pasar a producción.

### Ramas de trabajo
Las ramas deberán seguir la siguiente nomenclatura:

* feature/nombre-funcionalidad
* fix/nombre-correccion
* docs/nombre-documentacion

Ejemplos:
* feature/reconocimiento-facial
* feature/modulo-asistencia
* fix/error-registro
* docs/actualizacion-readme

## Pull Requests
Todo cambio debe realizarse en una rama de trabajo independiente.
Antes de fusionar cambios a las ramas principales, se deberá crear un Pull Request para su revisión y validación.
La rama principal (main) se encuentra protegida y no permite cambios directos.

## Conventional Commits
Los mensajes de commit deberán seguir el estándar Conventional Commits.

Formatos permitidos:
* feat: nueva funcionalidad
* fix: corrección de errores
* docs: cambios en documentación
* refactor: mejora interna del código
* style: cambios de formato o estilo
* test: incorporación o modificación de pruebas

Ejemplos:
feat: agregar módulo de reconocimiento facial
fix: corregir validación de usuarios
docs: actualizar documentación del proyecto
refactor: optimizar consultas de base de datos

## Buenas prácticas
* Mantener el código organizado y documentado.
* No subir credenciales ni información sensible.
* Verificar el correcto funcionamiento antes de crear un Pull Request.
* Mantener actualizado el archivo CHANGELOG.md con los cambios relevantes del proyecto.