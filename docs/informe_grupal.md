# Informe grupal - Sistema de Gestión de Actividades Deportivas Universitarias

## 1. Introducción

El objetivo del proyecto es implementar un sistema para administrar inscripciones de estudiantes a actividades deportivas universitarias. El sistema reemplaza una gestión manual basada en planillas y permite controlar cupos, lista de espera, asistencias y reportes para apoyar la gestión institucional.

## 2. Decisiones de diseño

Se diseñó una base de datos relacional en MySQL. Las principales entidades son: estudiante, facultad, carrera, disciplina deportiva, espacio deportivo, actividad deportiva, inscripción y asistencia.

La inscripción se modeló como una entidad propia porque representa la relación entre un estudiante y una actividad. Además, permite guardar fecha de inscripción y estado: confirmada, lista de espera o cancelada.

La asistencia se vinculó a `id_inscripcion` y no directamente a estudiante + actividad. Esta decisión mejora la consistencia, porque solo puede existir asistencia si antes existe una inscripción concreta.

## 3. Reglas de negocio implementadas

- Solo se admiten inscripciones en actividades abiertas.
- No se permite que un estudiante se inscriba dos veces a la misma actividad.
- Si hay cupo, la inscripción queda confirmada.
- Si no hay cupo, la inscripción queda en lista de espera.
- Al cancelar una inscripción confirmada, el sistema promueve automáticamente al primer estudiante en lista de espera si queda cupo.
- Solo se registra asistencia para inscripciones confirmadas.

Estas reglas se validan en frontend, backend y base de datos. En la base se usan claves únicas, claves foráneas, restricciones `CHECK` y triggers.

## 4. Mejoras del modelo de datos

Se agregó estado a estudiantes, disciplinas y espacios para implementar **bajas lógicas** en lugar de eliminación física. Cuando se da de baja un estudiante, el campo `estado` pasa a `inactivo`; en disciplinas y espacios pasa a `inactivo` o `cancelado`. El registro nunca se borra de la base de datos. Esta decisión tiene tres motivos: (1) preservar el historial de inscripciones y asistencias vinculado a esos registros, que quedaría huérfano con un DELETE; (2) evitar errores de integridad referencial por claves foráneas; (3) permitir reactivar un registro si fuera necesario sin pérdida de datos. También se separó `hora_inicio` y `hora_fin` en actividades, lo que resulta más claro que guardar un único campo de horario.

Se incluyó capacidad en espacio deportivo y cupo máximo en actividad. La capacidad del espacio sirve como dato maestro físico, mientras que el cupo máximo de la actividad permite adaptar cupos por tipo de actividad.

## 5. Aplicación

La aplicación fue desarrollada en Python usando Flask y conexión directa a MySQL mediante `mysql-connector-python`, sin ORM. El frontend permite operar el sistema desde el navegador, evitando depender de una consola para la defensa.

## 6. Reportes

Se implementaron los siete reportes pedidos en la letra y tres consultas adicionales propuestas por el equipo: lista de espera por actividad, actividades por espacio y estado, y estudiantes activos sin inscripciones confirmadas.

## 7. Bitácora resumida

1. Análisis de la letra del obligatorio.
2. Identificación de entidades, relaciones y restricciones.
3. Diseño del modelo relacional.
4. Creación de scripts SQL.
5. Carga de datos maestros y datos de prueba.
6. Desarrollo del backend Python sin ORM.
7. Desarrollo del frontend web.
8. Implementación de reportes.
9. Dockerización de la aplicación.
10. Documentación e instructivo de ejecución.

## 8. Bibliografía

- Documentación oficial de MySQL.
- Documentación oficial de Flask.
- Material del curso de Base de Datos 1.
