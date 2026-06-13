DROP DATABASE IF EXISTS actividades_deportivas;
CREATE DATABASE actividades_deportivas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE actividades_deportivas;

CREATE TABLE facultad (
    id_facultad INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE carrera (
    id_carrera INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL UNIQUE,
    id_facultad INT NOT NULL,
    FOREIGN KEY (id_facultad) REFERENCES facultad(id_facultad)
);

CREATE TABLE estudiante (
    documento INT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    apellido VARCHAR(60) NOT NULL,
    correo VARCHAR(120) NOT NULL UNIQUE,
    id_carrera INT NOT NULL,
    estado ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
    CHECK (documento > 0),
    CHECK (correo LIKE '%@%.%'),
    FOREIGN KEY (id_carrera) REFERENCES carrera(id_carrera)
);

CREATE TABLE login (
    correo VARCHAR(120) PRIMARY KEY,
    contrasena VARCHAR(255) NOT NULL,
    rol ENUM('admin','estudiante') NOT NULL DEFAULT 'estudiante',
    documento_estudiante INT NULL,
    debe_cambiar_contrasena BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (documento_estudiante) REFERENCES estudiante(documento) ON DELETE CASCADE
);

CREATE TABLE disciplina_deportiva (
    id_disciplina INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    estado ENUM('activa','inactiva') NOT NULL DEFAULT 'activa'
);

CREATE TABLE espacio_deportivo (
    id_espacio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    ubicacion VARCHAR(150) NOT NULL,
    capacidad INT NOT NULL,
    estado ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
    CHECK (capacidad > 0)
);

CREATE TABLE actividad_deportiva (
    id_actividad INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    id_disciplina INT NOT NULL,
    id_espacio INT NOT NULL,
    cupo_maximo INT NOT NULL,
    dia_semana ENUM('lunes','martes','miercoles','jueves','viernes','sabado','domingo') NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    estado ENUM('abierta','cerrada','finalizada','cancelada') NOT NULL DEFAULT 'abierta',
    CHECK (cupo_maximo > 0),
    CHECK (hora_fin > hora_inicio),
    FOREIGN KEY (id_disciplina) REFERENCES disciplina_deportiva(id_disciplina),
    FOREIGN KEY (id_espacio) REFERENCES espacio_deportivo(id_espacio)
);

CREATE TABLE inscripcion (
    id_inscripcion INT AUTO_INCREMENT PRIMARY KEY,
    documento_estudiante INT NOT NULL,
    id_actividad INT NOT NULL,
    fecha_inscripcion DATE NOT NULL DEFAULT (CURRENT_DATE),
    estado ENUM('confirmada','lista_espera','cancelada') NOT NULL,
    FOREIGN KEY (documento_estudiante) REFERENCES estudiante(documento),
    FOREIGN KEY (id_actividad) REFERENCES actividad_deportiva(id_actividad),
    UNIQUE KEY uq_estudiante_actividad (documento_estudiante, id_actividad)
);

CREATE TABLE asistencia (
    id_asistencia INT AUTO_INCREMENT PRIMARY KEY,
    id_inscripcion INT NOT NULL,
    fecha DATE NOT NULL,
    presente BOOLEAN NOT NULL,
    observacion VARCHAR(255),
    FOREIGN KEY (id_inscripcion) REFERENCES inscripcion(id_inscripcion),
    UNIQUE KEY uq_asistencia_fecha (id_inscripcion, fecha)
);

CREATE TABLE log_acciones (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    accion VARCHAR(120) NOT NULL,
    detalle VARCHAR(255),
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$
CREATE TRIGGER trg_validar_inscripcion_insert
BEFORE INSERT ON inscripcion
FOR EACH ROW
BEGIN
    DECLARE v_estado_actividad VARCHAR(20);
    DECLARE v_cupo INT;
    DECLARE v_confirmadas INT;

    SELECT estado, cupo_maximo INTO v_estado_actividad, v_cupo
    FROM actividad_deportiva WHERE id_actividad = NEW.id_actividad;

    IF v_estado_actividad <> 'abierta' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Solo se permiten inscripciones en actividades abiertas.';
    END IF;

    SELECT COUNT(*) INTO v_confirmadas
    FROM inscripcion
    WHERE id_actividad = NEW.id_actividad AND estado = 'confirmada';

    IF NEW.estado = 'confirmada' AND v_confirmadas >= v_cupo THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No hay cupo para confirmar la inscripción. Debe quedar en lista de espera.';
    END IF;
END$$

CREATE TRIGGER trg_validar_inscripcion_update
BEFORE UPDATE ON inscripcion
FOR EACH ROW
BEGIN
    DECLARE v_estado_actividad VARCHAR(20);
    DECLARE v_cupo INT;
    DECLARE v_confirmadas INT;

    SELECT estado, cupo_maximo INTO v_estado_actividad, v_cupo
    FROM actividad_deportiva WHERE id_actividad = NEW.id_actividad;

    IF NEW.estado IN ('confirmada','lista_espera') AND v_estado_actividad <> 'abierta' AND OLD.estado = 'cancelada' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede reactivar inscripción en actividad no abierta.';
    END IF;

    SELECT COUNT(*) INTO v_confirmadas
    FROM inscripcion
    WHERE id_actividad = NEW.id_actividad AND estado = 'confirmada' AND id_inscripcion <> NEW.id_inscripcion;

    IF NEW.estado = 'confirmada' AND v_confirmadas >= v_cupo THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No hay cupo para confirmar esta inscripción.';
    END IF;
END$$

CREATE TRIGGER trg_validar_asistencia_insert
BEFORE INSERT ON asistencia
FOR EACH ROW
BEGIN
    DECLARE v_estado_inscripcion VARCHAR(20);
    SELECT estado INTO v_estado_inscripcion FROM inscripcion WHERE id_inscripcion = NEW.id_inscripcion;
    IF v_estado_inscripcion <> 'confirmada' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Solo se puede registrar asistencia de estudiantes confirmados.';
    END IF;
END$$

CREATE TRIGGER trg_validar_asistencia_update
BEFORE UPDATE ON asistencia
FOR EACH ROW
BEGIN
    DECLARE v_estado_inscripcion VARCHAR(20);
    SELECT estado INTO v_estado_inscripcion FROM inscripcion WHERE id_inscripcion = NEW.id_inscripcion;
    IF v_estado_inscripcion <> 'confirmada' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Solo se puede actualizar asistencia de estudiantes confirmados.';
    END IF;
END$$
DELIMITER ;


DELIMITER $$

CREATE TRIGGER trg_validar_capacidad_actividad_insert
BEFORE INSERT ON actividad_deportiva
FOR EACH ROW
BEGIN
    DECLARE v_capacidad INT;

    SELECT capacidad
    INTO v_capacidad
    FROM espacio_deportivo
    WHERE id_espacio = NEW.id_espacio;

    IF NEW.cupo_maximo > v_capacidad THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
            'El cupo máximo no puede superar la capacidad del espacio.';
    END IF;
END$$

CREATE TRIGGER trg_validar_capacidad_actividad_update
BEFORE UPDATE ON actividad_deportiva
FOR EACH ROW
BEGIN
    DECLARE v_capacidad INT;

    SELECT capacidad
    INTO v_capacidad
    FROM espacio_deportivo
    WHERE id_espacio = NEW.id_espacio;

    IF NEW.cupo_maximo > v_capacidad THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
            'El cupo máximo no puede superar la capacidad del espacio.';
    END IF;
END$$

DELIMITER ;