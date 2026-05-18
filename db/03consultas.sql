USE actividades_deportivas;

-- 1. Actividades con mayor cantidad de inscriptos confirmados.
SELECT a.id_actividad, a.nombre, COUNT(i.id_inscripcion) AS confirmados
FROM actividad_deportiva a
LEFT JOIN inscripcion i ON a.id_actividad = i.id_actividad AND i.estado = 'confirmada'
GROUP BY a.id_actividad, a.nombre
ORDER BY confirmados DESC;

-- 2. Actividades con cupos disponibles.
SELECT a.id_actividad, a.nombre, a.cupo_maximo,
       COUNT(i.id_inscripcion) AS confirmados,
       a.cupo_maximo - COUNT(i.id_inscripcion) AS cupos_disponibles
FROM actividad_deportiva a
LEFT JOIN inscripcion i ON a.id_actividad = i.id_actividad AND i.estado = 'confirmada'
WHERE a.estado = 'abierta'
GROUP BY a.id_actividad, a.nombre, a.cupo_maximo
HAVING cupos_disponibles > 0
ORDER BY cupos_disponibles DESC;

-- 3. Cantidad de inscriptos por disciplina deportiva.
SELECT d.nombre AS disciplina, COUNT(i.id_inscripcion) AS inscriptos_confirmados
FROM disciplina_deportiva d
LEFT JOIN actividad_deportiva a ON d.id_disciplina = a.id_disciplina
LEFT JOIN inscripcion i ON a.id_actividad = i.id_actividad AND i.estado = 'confirmada'
GROUP BY d.id_disciplina, d.nombre
ORDER BY inscriptos_confirmados DESC;

-- 4. Cantidad de inscriptos por carrera y facultad.
SELECT f.nombre AS facultad, c.nombre AS carrera, COUNT(i.id_inscripcion) AS inscriptos_confirmados
FROM facultad f
JOIN carrera c ON f.id_facultad = c.id_facultad
JOIN estudiante e ON c.id_carrera = e.id_carrera
JOIN inscripcion i ON e.documento = i.documento_estudiante AND i.estado = 'confirmada'
GROUP BY f.nombre, c.nombre
ORDER BY f.nombre, c.nombre;

-- 5. Porcentaje de ocupación de cada actividad.
SELECT a.id_actividad, a.nombre, a.cupo_maximo,
       COUNT(i.id_inscripcion) AS confirmados,
       ROUND(COUNT(i.id_inscripcion) * 100 / a.cupo_maximo, 2) AS porcentaje_ocupacion
FROM actividad_deportiva a
LEFT JOIN inscripcion i ON a.id_actividad = i.id_actividad AND i.estado = 'confirmada'
GROUP BY a.id_actividad, a.nombre, a.cupo_maximo
ORDER BY porcentaje_ocupacion DESC;

-- 6. Porcentaje de asistencia por actividad.
SELECT a.id_actividad, a.nombre,
       COUNT(ast.id_asistencia) AS asistencias_registradas,
       SUM(CASE WHEN ast.presente THEN 1 ELSE 0 END) AS presentes,
       ROUND(SUM(CASE WHEN ast.presente THEN 1 ELSE 0 END) * 100 / NULLIF(COUNT(ast.id_asistencia), 0), 2) AS porcentaje_asistencia
FROM actividad_deportiva a
LEFT JOIN inscripcion i ON a.id_actividad = i.id_actividad
LEFT JOIN asistencia ast ON i.id_inscripcion = ast.id_inscripcion
GROUP BY a.id_actividad, a.nombre
ORDER BY porcentaje_asistencia DESC;

-- 7. Estudiantes con tres o más inasistencias registradas.
SELECT e.documento, e.nombre, e.apellido, COUNT(ast.id_asistencia) AS inasistencias
FROM estudiante e
JOIN inscripcion i ON e.documento = i.documento_estudiante
JOIN asistencia ast ON i.id_inscripcion = ast.id_inscripcion
WHERE ast.presente = FALSE
GROUP BY e.documento, e.nombre, e.apellido
HAVING inasistencias >= 3
ORDER BY inasistencias DESC;

-- 8 adicional. Lista de espera por actividad.
SELECT a.nombre AS actividad, e.documento, e.nombre, e.apellido, i.fecha_inscripcion
FROM inscripcion i
JOIN actividad_deportiva a ON i.id_actividad = a.id_actividad
JOIN estudiante e ON i.documento_estudiante = e.documento
WHERE i.estado = 'lista_espera'
ORDER BY a.nombre, i.fecha_inscripcion;

-- 9 adicional. Actividades por espacio y estado.
SELECT ed.nombre AS espacio, a.estado, COUNT(*) AS cantidad_actividades
FROM actividad_deportiva a
JOIN espacio_deportivo ed ON a.id_espacio = ed.id_espacio
GROUP BY ed.nombre, a.estado
ORDER BY ed.nombre, a.estado;

-- 10 adicional. Estudiantes activos sin inscripciones confirmadas.
SELECT e.documento, e.nombre, e.apellido, e.correo
FROM estudiante e
LEFT JOIN inscripcion i ON e.documento = i.documento_estudiante AND i.estado = 'confirmada'
WHERE e.estado = 'activo'
GROUP BY e.documento, e.nombre, e.apellido, e.correo
HAVING COUNT(i.id_inscripcion) = 0;
