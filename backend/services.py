from db import fetch_all, fetch_one, execute, get_connection, hashear

DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
ESTADOS_ACTIVIDAD = ["abierta", "cerrada", "finalizada", "cancelada"]


# ─── AUTH ─────────────────────────────────────────────────────────────────────

def autenticar(correo: str, contrasena: str):
    """Devuelve el row de login si las credenciales son válidas, sino None."""
    return fetch_one(
        "SELECT correo, rol, documento_estudiante FROM login WHERE correo = %s AND contrasena = %s",
        (correo.strip(), hashear(contrasena))
    )


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

def dashboard_stats():
    return {
        "estudiantes": fetch_one("SELECT COUNT(*) total FROM estudiante WHERE estado='activo'")["total"],
        "actividades": fetch_one("SELECT COUNT(*) total FROM actividad_deportiva")["total"],
        "abiertas":    fetch_one("SELECT COUNT(*) total FROM actividad_deportiva WHERE estado='abierta'")["total"],
        "confirmadas": fetch_one("SELECT COUNT(*) total FROM inscripcion WHERE estado='confirmada'")["total"],
        "espera":      fetch_one("SELECT COUNT(*) total FROM inscripcion WHERE estado='lista_espera'")["total"],
    }


# ─── CARRERAS ─────────────────────────────────────────────────────────────────

def carreras():
    return fetch_all("""
        SELECT c.id_carrera, c.nombre, f.nombre AS facultad
        FROM carrera c JOIN facultad f ON c.id_facultad = f.id_facultad
        ORDER BY f.nombre, c.nombre
    """)


# ─── ESTUDIANTES ──────────────────────────────────────────────────────────────

def estudiantes():
    return fetch_all("""
        SELECT e.documento, e.nombre, e.apellido, e.correo, e.estado,
               c.nombre AS carrera, f.nombre AS facultad
        FROM estudiante e
        JOIN carrera c ON e.id_carrera = c.id_carrera
        JOIN facultad f ON c.id_facultad = f.id_facultad
        ORDER BY e.estado, e.apellido, e.nombre
    """)


def crear_estudiante(form):
    execute("""
        INSERT INTO estudiante (documento, nombre, apellido, correo, id_carrera)
        VALUES (%s, %s, %s, %s, %s)
    """, (form["documento"], form["nombre"].strip(), form["apellido"].strip(),
          form["correo"].strip(), form["id_carrera"]))
    # Login con contraseña hasheada
    execute("""
        INSERT INTO login (correo, contrasena, rol, documento_estudiante, debe_cambiar_contrasena)
        VALUES (%s, %s, 'estudiante', %s, FALSE)
    """, (form["correo"].strip(), hashear("usuario123"), form["documento"]))


def actualizar_estudiante(documento, form):
    execute("""
        UPDATE estudiante SET nombre=%s, apellido=%s, correo=%s, id_carrera=%s, estado=%s
        WHERE documento=%s
    """, (form["nombre"].strip(), form["apellido"].strip(), form["correo"].strip(),
          form["id_carrera"], form["estado"], documento))


def baja_estudiante(documento):
    execute("UPDATE estudiante SET estado='inactivo' WHERE documento=%s", (documento,))


# ─── DISCIPLINAS ──────────────────────────────────────────────────────────────

def disciplinas():
    return fetch_all("SELECT * FROM disciplina_deportiva ORDER BY estado, nombre")


def crear_disciplina(form):
    execute(
        "INSERT INTO disciplina_deportiva (nombre, descripcion) VALUES (%s, %s)",
        (form["nombre"].strip(), form.get("descripcion", "").strip())
    )


def actualizar_disciplina(id_disciplina, form):
    execute(
        "UPDATE disciplina_deportiva SET nombre=%s, descripcion=%s, estado=%s WHERE id_disciplina=%s",
        (form["nombre"], form.get("descripcion", ""), form["estado"], id_disciplina)
    )


# ─── ESPACIOS ─────────────────────────────────────────────────────────────────

def espacios():
    return fetch_all("SELECT * FROM espacio_deportivo ORDER BY estado, nombre")


def crear_espacio(form):
    execute(
        "INSERT INTO espacio_deportivo (nombre, ubicacion, capacidad) VALUES (%s, %s, %s)",
        (form["nombre"].strip(), form["ubicacion"].strip(), form["capacidad"])
    )


def actualizar_espacio(id_espacio, form):
    execute(
        "UPDATE espacio_deportivo SET nombre=%s, ubicacion=%s, capacidad=%s, estado=%s WHERE id_espacio=%s",
        (form["nombre"], form["ubicacion"], form["capacidad"], form["estado"], id_espacio)
    )


# ─── ACTIVIDADES ──────────────────────────────────────────────────────────────

def actividades(estado=None):
    where = "WHERE a.estado = %s" if estado else ""
    params = (estado,) if estado else ()
    return fetch_all(f"""
        SELECT a.*, d.nombre AS disciplina, e.nombre AS espacio,
               COUNT(CASE WHEN i.estado='confirmada'   THEN 1 END) AS confirmados,
               COUNT(CASE WHEN i.estado='lista_espera' THEN 1 END) AS en_espera,
               a.cupo_maximo - COUNT(CASE WHEN i.estado='confirmada' THEN 1 END) AS cupos_disponibles
        FROM actividad_deportiva a
        JOIN disciplina_deportiva d ON a.id_disciplina = d.id_disciplina
        JOIN espacio_deportivo e    ON a.id_espacio    = e.id_espacio
        LEFT JOIN inscripcion i     ON a.id_actividad  = i.id_actividad
        {where}
        GROUP BY a.id_actividad, d.nombre, e.nombre
        ORDER BY FIELD(a.dia_semana,'lunes','martes','miercoles','jueves','viernes','sabado','domingo'), a.hora_inicio
    """, params)


def crear_actividad(form):
    execute("""
        INSERT INTO actividad_deportiva
            (nombre, id_disciplina, id_espacio, cupo_maximo, dia_semana, hora_inicio, hora_fin, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (form["nombre"].strip(), form["id_disciplina"], form["id_espacio"],
          form["cupo_maximo"], form["dia_semana"],
          form["hora_inicio"], form["hora_fin"], form["estado"]))


def actualizar_actividad(id_actividad, form):
    execute("""
        UPDATE actividad_deportiva
        SET nombre=%s, id_disciplina=%s, id_espacio=%s, cupo_maximo=%s,
            dia_semana=%s, hora_inicio=%s, hora_fin=%s, estado=%s
        WHERE id_actividad=%s
    """, (form["nombre"], form["id_disciplina"], form["id_espacio"], form["cupo_maximo"],
          form["dia_semana"], form["hora_inicio"], form["hora_fin"], form["estado"],
          id_actividad))


# ─── INSCRIPCIONES ────────────────────────────────────────────────────────────

def inscripciones():
    return fetch_all("""
        SELECT i.id_inscripcion, i.estado, i.fecha_inscripcion,
               e.documento, e.nombre AS estudiante_nombre, e.apellido,
               a.id_actividad, a.nombre AS actividad, a.estado AS estado_actividad
        FROM inscripcion i
        JOIN estudiante e         ON i.documento_estudiante = e.documento
        JOIN actividad_deportiva a ON i.id_actividad         = a.id_actividad
        ORDER BY a.nombre,
                 FIELD(i.estado, 'confirmada', 'lista_espera', 'cancelada'),
                 i.fecha_inscripcion
    """)


def inscribir(documento, id_actividad):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT estado, cupo_maximo FROM actividad_deportiva WHERE id_actividad = %s",
            (id_actividad,)
        )
        act = cur.fetchone()
        if not act:
            raise ValueError("La actividad no existe.")
        if act["estado"] != "abierta":
            raise ValueError("Solo se puede inscribir en actividades abiertas.")

        cur.execute(
            "SELECT COUNT(*) total FROM inscripcion WHERE documento_estudiante=%s AND id_actividad=%s",
            (documento, id_actividad)
        )
        if cur.fetchone()["total"] > 0:
            raise ValueError("El estudiante ya está inscripto en esta actividad.")

        cur.execute(
            "SELECT COUNT(*) total FROM inscripcion WHERE id_actividad=%s AND estado='confirmada'",
            (id_actividad,)
        )
        confirmadas = cur.fetchone()["total"]
        estado = "confirmada" if confirmadas < act["cupo_maximo"] else "lista_espera"

        cur.execute(
            "INSERT INTO inscripcion (documento_estudiante, id_actividad, estado) VALUES (%s, %s, %s)",
            (documento, id_actividad, estado)
        )
        conn.commit()
        return estado
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def cancelar_inscripcion(id_inscripcion):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT id_actividad, estado FROM inscripcion WHERE id_inscripcion = %s",
            (id_inscripcion,)
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("La inscripción no existe.")

        id_actividad = row["id_actividad"]
        cur.execute(
            "UPDATE inscripcion SET estado='cancelada' WHERE id_inscripcion=%s",
            (id_inscripcion,)
        )

        # Promover primer estudiante en lista de espera si hay cupo
        cur.execute(
            "SELECT cupo_maximo FROM actividad_deportiva WHERE id_actividad=%s",
            (id_actividad,)
        )
        cupo = cur.fetchone()["cupo_maximo"]
        cur.execute(
            "SELECT COUNT(*) total FROM inscripcion WHERE id_actividad=%s AND estado='confirmada'",
            (id_actividad,)
        )
        if cur.fetchone()["total"] < cupo:
            cur.execute("""
                SELECT id_inscripcion FROM inscripcion
                WHERE id_actividad=%s AND estado='lista_espera'
                ORDER BY fecha_inscripcion, id_inscripcion
                LIMIT 1
            """, (id_actividad,))
            espera = cur.fetchone()
            if espera:
                cur.execute(
                    "UPDATE inscripcion SET estado='confirmada' WHERE id_inscripcion=%s",
                    (espera["id_inscripcion"],)
                )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─── ASISTENCIAS ──────────────────────────────────────────────────────────────

def inscripciones_confirmadas():
    return fetch_all("""
        SELECT i.id_inscripcion, e.documento, e.nombre, e.apellido,
               a.nombre AS actividad
        FROM inscripcion i
        JOIN estudiante e          ON i.documento_estudiante = e.documento
        JOIN actividad_deportiva a ON i.id_actividad         = a.id_actividad
        WHERE i.estado = 'confirmada'
        ORDER BY a.nombre, e.apellido
    """)


def registrar_asistencia(form):
    execute("""
        INSERT INTO asistencia (id_inscripcion, fecha, presente, observacion)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            presente    = VALUES(presente),
            observacion = VALUES(observacion)
    """, (form["id_inscripcion"], form["fecha"],
          1 if form.get("presente") == "1" else 0,
          form.get("observacion", "")))


def asistencias():
    return fetch_all("""
        SELECT ast.id_asistencia, ast.fecha, ast.presente, ast.observacion,
               e.documento, e.nombre, e.apellido,
               a.nombre AS actividad
        FROM asistencia ast
        JOIN inscripcion i          ON ast.id_inscripcion   = i.id_inscripcion
        JOIN estudiante e           ON i.documento_estudiante = e.documento
        JOIN actividad_deportiva a  ON i.id_actividad        = a.id_actividad
        ORDER BY ast.fecha DESC, a.nombre, e.apellido
    """)


# ─── REPORTES ─────────────────────────────────────────────────────────────────

def reportes():
    return {
        "mas_inscriptos": fetch_all("""
            SELECT a.nombre AS actividad, COUNT(i.id_inscripcion) AS confirmados
            FROM actividad_deportiva a
            LEFT JOIN inscripcion i ON a.id_actividad = i.id_actividad AND i.estado = 'confirmada'
            GROUP BY a.id_actividad, a.nombre
            ORDER BY confirmados DESC
        """),
        "cupos": fetch_all("""
            SELECT a.nombre AS actividad, a.cupo_maximo,
                   COUNT(i.id_inscripcion) AS confirmados,
                   a.cupo_maximo - COUNT(i.id_inscripcion) AS cupos_disponibles
            FROM actividad_deportiva a
            LEFT JOIN inscripcion i ON a.id_actividad = i.id_actividad AND i.estado = 'confirmada'
            WHERE a.estado = 'abierta'
            GROUP BY a.id_actividad, a.nombre, a.cupo_maximo
            HAVING cupos_disponibles > 0
            ORDER BY cupos_disponibles DESC
        """),
        "por_disciplina": fetch_all("""
            SELECT d.nombre AS disciplina,
                   COUNT(CASE WHEN i.estado='confirmada'   THEN 1 END) AS confirmados,
                   COUNT(CASE WHEN i.estado='lista_espera' THEN 1 END) AS en_espera,
                   COUNT(i.id_inscripcion) AS total
            FROM disciplina_deportiva d
            LEFT JOIN actividad_deportiva a ON d.id_disciplina = a.id_disciplina
            LEFT JOIN inscripcion i         ON a.id_actividad  = i.id_actividad
            GROUP BY d.id_disciplina, d.nombre
            ORDER BY total DESC
        """),
        "por_carrera": fetch_all("""
            SELECT f.nombre AS facultad, c.nombre AS carrera,
                   COUNT(CASE WHEN i.estado='confirmada' THEN 1 END) AS inscriptos_confirmados,
                   COUNT(i.id_inscripcion) AS total
            FROM facultad f
            JOIN carrera c      ON f.id_facultad  = c.id_facultad
            JOIN estudiante e   ON c.id_carrera   = e.id_carrera
            LEFT JOIN inscripcion i ON e.documento = i.documento_estudiante
            GROUP BY f.id_facultad, f.nombre, c.id_carrera, c.nombre
            ORDER BY f.nombre, inscriptos_confirmados DESC
        """),
        "ocupacion": fetch_all("""
            SELECT a.nombre AS actividad, a.cupo_maximo,
                   COUNT(i.id_inscripcion) AS confirmados,
                   ROUND(COUNT(i.id_inscripcion) * 100.0 / a.cupo_maximo, 2) AS porcentaje_ocupacion
            FROM actividad_deportiva a
            LEFT JOIN inscripcion i ON a.id_actividad = i.id_actividad AND i.estado = 'confirmada'
            GROUP BY a.id_actividad, a.nombre, a.cupo_maximo
            ORDER BY porcentaje_ocupacion DESC
        """),
        "asistencia": fetch_all("""
            SELECT a.nombre AS actividad,
                   COUNT(ast.id_asistencia) AS registros,
                   SUM(CASE WHEN ast.presente THEN 1 ELSE 0 END) AS presentes,
                   ROUND(
                       SUM(CASE WHEN ast.presente THEN 1 ELSE 0 END) * 100.0 /
                       NULLIF(COUNT(ast.id_asistencia), 0), 2
                   ) AS porcentaje_asistencia
            FROM actividad_deportiva a
            LEFT JOIN inscripcion i ON a.id_actividad   = i.id_actividad
            LEFT JOIN asistencia ast ON i.id_inscripcion = ast.id_inscripcion
            GROUP BY a.id_actividad, a.nombre
            ORDER BY porcentaje_asistencia DESC
        """),
        "inasistencias": fetch_all("""
            SELECT e.documento, e.nombre, e.apellido,
                   COUNT(ast.id_asistencia) AS inasistencias
            FROM estudiante e
            JOIN inscripcion i   ON e.documento       = i.documento_estudiante
            JOIN asistencia ast  ON i.id_inscripcion  = ast.id_inscripcion
            WHERE ast.presente = FALSE
            GROUP BY e.documento, e.nombre, e.apellido
            HAVING inasistencias >= 3
            ORDER BY inasistencias DESC
        """),
        # Consultas adicionales
        "lista_espera": fetch_all("""
            SELECT a.nombre AS actividad,
                   e.documento, e.nombre, e.apellido,
                   i.fecha_inscripcion
            FROM inscripcion i
            JOIN actividad_deportiva a ON i.id_actividad         = a.id_actividad
            JOIN estudiante e          ON i.documento_estudiante = e.documento
            WHERE i.estado = 'lista_espera'
            ORDER BY a.nombre, i.fecha_inscripcion
        """),
        "por_espacio_estado": fetch_all("""
            SELECT ed.nombre AS espacio, a.estado,
                   COUNT(*) AS cantidad_actividades
            FROM actividad_deportiva a
            JOIN espacio_deportivo ed ON a.id_espacio = ed.id_espacio
            GROUP BY ed.nombre, a.estado
            ORDER BY ed.nombre, a.estado
        """),
        "sin_confirmadas": fetch_all("""
            SELECT e.documento, e.nombre, e.apellido, e.correo
            FROM estudiante e
            LEFT JOIN inscripcion i
                ON e.documento = i.documento_estudiante AND i.estado = 'confirmada'
            WHERE e.estado = 'activo'
            GROUP BY e.documento, e.nombre, e.apellido, e.correo
            HAVING COUNT(i.id_inscripcion) = 0
        """),
    }
