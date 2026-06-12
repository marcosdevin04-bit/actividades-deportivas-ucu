import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from mysql.connector import Error
import services as svc

app = Flask(__name__,template_folder="../frontend/templates",static_folder="../frontend/static")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "deportes-ucu-2026-secret")


# ─── DECORADORES DE AUTENTICACIÓN ─────────────────────────────────────────────

def login_requerido(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "correo" not in session:
            flash("Debés iniciar sesión para acceder.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapped


def solo_admin(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if session.get("rol") != "admin":
            flash("Acceso restringido a administradores.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrapped


# ─── AUTH ─────────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if "correo" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        usuario = svc.autenticar(request.form["correo"], request.form["contrasena"])
        if usuario:
            session["correo"] = usuario["correo"]
            session["rol"] = usuario["rol"]
            session["documento"] = usuario["documento_estudiante"]
            return redirect(url_for("index"))
        flash("Correo o contraseña incorrectos.", "danger")
    return render_template("login.html")


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ─── HELPER ───────────────────────────────────────────────────────────────────

def safe_action(success_msg, redirect_endpoint, action):
    try:
        result = action()
        msg = f"{success_msg}"
        if isinstance(result, str) and result:
            msg += f" ({result})"
        flash(msg, "success")
    except (Error, ValueError) as exc:
        flash(str(exc), "danger")
    return redirect(url_for(redirect_endpoint))


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@app.route("/")
@login_requerido
def index():
    return render_template(
        "index.html",
        stats=svc.dashboard_stats(),
        actividades=svc.actividades("abierta")[:5]
    )


# ─── ESTUDIANTES ──────────────────────────────────────────────────────────────

@app.route("/estudiantes")
@login_requerido
@solo_admin
def estudiantes():
    return render_template(
        "estudiantes.html",
        estudiantes=svc.estudiantes(),
        carreras=svc.carreras()
    )


@app.post("/estudiantes")
@login_requerido
@solo_admin
def estudiantes_crear():
    return safe_action(
        "Estudiante creado. Login: correo del estudiante, contraseña: usuario123",
        "estudiantes",
        lambda: svc.crear_estudiante(request.form)
    )


@app.post("/estudiantes/<int:documento>/actualizar")
@login_requerido
@solo_admin
def estudiantes_actualizar(documento):
    return safe_action(
        "Estudiante actualizado",
        "estudiantes",
        lambda: svc.actualizar_estudiante(documento, request.form)
    )


@app.post("/estudiantes/<int:documento>/baja")
@login_requerido
@solo_admin
def estudiantes_baja(documento):
    return safe_action(
        "Estudiante dado de baja",
        "estudiantes",
        lambda: svc.baja_estudiante(documento)
    )


# ─── DISCIPLINAS ──────────────────────────────────────────────────────────────

@app.route("/disciplinas")
@login_requerido
@solo_admin
def disciplinas():
    return render_template("disciplinas.html", disciplinas=svc.disciplinas())


@app.post("/disciplinas")
@login_requerido
@solo_admin
def disciplinas_crear():
    return safe_action("Disciplina creada", "disciplinas",
                        lambda: svc.crear_disciplina(request.form))


@app.post("/disciplinas/<int:id_disciplina>/actualizar")
@login_requerido
@solo_admin
def disciplinas_actualizar(id_disciplina):
    return safe_action("Disciplina actualizada", "disciplinas",
                        lambda: svc.actualizar_disciplina(id_disciplina, request.form))


# ─── ESPACIOS ─────────────────────────────────────────────────────────────────

@app.route("/espacios")
@login_requerido
@solo_admin
def espacios():
    return render_template("espacios.html", espacios=svc.espacios())


@app.post("/espacios")
@login_requerido
@solo_admin
def espacios_crear():
    return safe_action("Espacio creado", "espacios",
                        lambda: svc.crear_espacio(request.form))


@app.post("/espacios/<int:id_espacio>/actualizar")
@login_requerido
@solo_admin
def espacios_actualizar(id_espacio):
    return safe_action("Espacio actualizado", "espacios",
                        lambda: svc.actualizar_espacio(id_espacio, request.form))


# ─── ACTIVIDADES ──────────────────────────────────────────────────────────────

@app.route("/actividades")
@login_requerido
@solo_admin
def actividades():
    return render_template(
        "actividades.html",
        actividades=svc.actividades(),
        disciplinas=svc.disciplinas(),
        espacios=svc.espacios(),
        dias=svc.DIAS,
        estados=svc.ESTADOS_ACTIVIDAD,
    )


@app.post("/actividades")
@login_requerido
@solo_admin
def actividades_crear():
    return safe_action("Actividad creada", "actividades",
                        lambda: svc.crear_actividad(request.form))


@app.post("/actividades/<int:id_actividad>/actualizar")
@login_requerido
@solo_admin
def actividades_actualizar(id_actividad):
    return safe_action("Actividad actualizada", "actividades",
                        lambda: svc.actualizar_actividad(id_actividad, request.form))


# ─── INSCRIPCIONES ────────────────────────────────────────────────────────────

@app.route("/inscripciones")
@login_requerido
@solo_admin
def inscripciones():
    return render_template(
        "inscripciones.html",
        inscripciones=svc.inscripciones(),
        estudiantes=svc.estudiantes(),
        actividades=svc.actividades("abierta"),
    )


@app.post("/inscripciones")
@login_requerido
@solo_admin
def inscripciones_crear():
    def action():
        estado = svc.inscribir(request.form["documento"], request.form["id_actividad"])
        return f"estado: {estado}"
    return safe_action("Inscripción registrada", "inscripciones", action)


@app.post("/inscripciones/<int:id_inscripcion>/cancelar")
@login_requerido
@solo_admin
def inscripciones_cancelar(id_inscripcion):
    return safe_action(
        "Inscripción cancelada. Si había lista de espera, se promovió al primero",
        "inscripciones",
        lambda: svc.cancelar_inscripcion(id_inscripcion)
    )


# ─── ASISTENCIAS ──────────────────────────────────────────────────────────────

@app.route("/asistencias")
@login_requerido
@solo_admin
def asistencias():
    return render_template(
        "asistencias.html",
        confirmadas=svc.inscripciones_confirmadas(),
        asistencias=svc.asistencias()
    )


@app.post("/asistencias")
@login_requerido
@solo_admin
def asistencias_crear():
    return safe_action("Asistencia registrada", "asistencias",
                        lambda: svc.registrar_asistencia(request.form))


# ─── REPORTES ─────────────────────────────────────────────────────────────────

@app.route("/reportes")
@login_requerido
def reportes():
    return render_template("reportes.html", reportes=svc.reportes())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
