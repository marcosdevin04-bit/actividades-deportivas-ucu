USE actividades_deportivas;

SET NAMES utf8mb4;

INSERT INTO facultad (nombre) VALUES
('Facultad de Ingeniería y Tecnologías'),
('Facultad de Ciencias Empresariales'),
('Facultad de Ciencias Humanas'),
('Facultad de Ciencias de la Salud');

INSERT INTO carrera (nombre, id_facultad) VALUES
('Ingeniería en Inteligencia Artificial y Ciencia de Datos', 1),
('Ingeniería Informática', 1),
('Licenciatura en Dirección de Empresas', 2),
('Contador Público', 2),
('Psicología', 3),
('Medicina', 4);

INSERT INTO estudiante (documento, nombre, apellido, correo, id_carrera) VALUES
(50123456, 'Facundo',   'González',  'facundo.gonzalez@ucu.edu.uy',  1),
(50234567, 'Sofía',     'Rodríguez', 'sofia.rodriguez@ucu.edu.uy',   2),
(50345678, 'Martín',    'Pérez',     'martin.perez@ucu.edu.uy',      3),
(50456789, 'Valentina', 'Silva',     'valentina.silva@ucu.edu.uy',   4),
(50567890, 'Lucas',     'Fernández', 'lucas.fernandez@ucu.edu.uy',   5),
(50678901, 'Camila',    'Martínez',  'camila.martinez@ucu.edu.uy',   6),
(50789012, 'Juan',      'López',     'juan.lopez@ucu.edu.uy',        1),
(50890123, 'Lucía',     'Sosa',      'lucia.sosa@ucu.edu.uy',        2);

-- Contraseñas hasheadas con SHA-256.
-- admin123   -> 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
-- usuario123 -> dfa7a2273567dcd1efffb9a46308e91c20fa13c44c3441bc69cd6a7869b3f7fd
INSERT INTO login (correo, contrasena, rol, documento_estudiante, debe_cambiar_contrasena) VALUES
('admin@ucu.edu.uy',              '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin',      NULL,     FALSE),
('facundo.gonzalez@ucu.edu.uy',   'dfa7a2273567dcd1efffb9a46308e91c20fa13c44c3441bc69cd6a7869b3f7fd', 'estudiante', 50123456, FALSE),
('sofia.rodriguez@ucu.edu.uy',    'dfa7a2273567dcd1efffb9a46308e91c20fa13c44c3441bc69cd6a7869b3f7fd', 'estudiante', 50234567, FALSE),
('martin.perez@ucu.edu.uy',       'dfa7a2273567dcd1efffb9a46308e91c20fa13c44c3441bc69cd6a7869b3f7fd', 'estudiante', 50345678, FALSE);

INSERT INTO disciplina_deportiva (nombre, descripcion) VALUES
('Fútbol',      'Actividades recreativas y competitivas de fútbol.'),
('Básquetbol',  'Entrenamientos y partidos internos de básquetbol.'),
('Atletismo',   'Pruebas de velocidad, resistencia y técnica.'),
('Vóleibol',    'Entrenamientos recreativos y mixtos.'),
('Yoga',        'Actividad de movilidad, respiración y bienestar.'),
('Funcional',   'Entrenamiento general por circuitos.'),
('Gimnasio',    'Uso supervisado de sala de musculación.');

INSERT INTO espacio_deportivo (nombre, ubicacion, capacidad) VALUES
('Cancha multideporte',  'Campus central - exterior',           30),
('Gimnasio principal',   'Edificio deportivo - planta baja',    25),
('Sala de yoga',         'Edificio deportivo - primer piso',    18),
('Pista de atletismo',   'Campus central - sector norte',       40),
('Sala funcional',       'Edificio deportivo - subsuelo',       20);

INSERT INTO actividad_deportiva (nombre, id_disciplina, id_espacio, cupo_maximo, dia_semana, hora_inicio, hora_fin, estado) VALUES
('Fútbol recreativo mixto',  1, 1,  4, 'lunes',     '18:00:00', '19:30:00', 'abierta'),
('Básquetbol inicial',       2, 2, 12, 'martes',    '17:00:00', '18:30:00', 'abierta'),
('Atletismo inicial',        3, 4, 20, 'miercoles', '08:00:00', '09:00:00', 'abierta'),
('Vóleibol recreativo',      4, 1, 16, 'jueves',    '19:00:00', '20:30:00', 'cerrada'),
('Yoga turno mañana',        5, 3, 10, 'viernes',   '08:00:00', '09:00:00', 'abierta'),
('Funcional turno mañana',   6, 5,  6, 'lunes',     '07:30:00', '08:30:00', 'abierta'),
('Gimnasio supervisado',     7, 2, 15, 'sabado',    '10:00:00', '12:00:00', 'finalizada');

INSERT INTO inscripcion (documento_estudiante, id_actividad, estado) VALUES
(50123456, 1, 'confirmada'),
(50234567, 1, 'confirmada'),
(50345678, 1, 'confirmada'),
(50456789, 1, 'confirmada'),
(50567890, 1, 'lista_espera'),
(50678901, 2, 'confirmada'),
(50789012, 2, 'confirmada'),
(50890123, 5, 'confirmada'),
(50123456, 6, 'confirmada'),
(50234567, 6, 'confirmada');

INSERT INTO asistencia (id_inscripcion, fecha, presente, observacion) VALUES
(1, '2026-06-01', TRUE,  'Asistió'),
(2, '2026-06-01', FALSE, 'No asistió'),
(3, '2026-06-01', TRUE,  'Asistió'),
(6, '2026-06-02', TRUE,  'Asistió'),
(8, '2026-06-05', FALSE, 'No asistió'),
(9, '2026-06-01', FALSE, 'No asistió'),
(9, '2026-06-08', FALSE, 'No asistió'),
(9, '2026-06-15', FALSE, 'No asistió');
