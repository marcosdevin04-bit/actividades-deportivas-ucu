# Sistema de Gestión de Actividades Deportivas — UCU

Sistema para administrar inscripciones de estudiantes a actividades deportivas universitarias. Backend Python + Flask, base de datos MySQL, sin ORM, con frontend web.

## Tecnologías

- Python 3.11 + Flask
- MySQL 8
- mysql-connector-python (sin ORM)
- HTML + CSS + Jinja2
- Docker + Docker Compose

## Cómo correr con Docker (recomendado)

```bash
docker compose down -v
docker compose up --build
```

Luego abrir en el navegador:

```
http://localhost:5000
```

La primera vez tarda ~20 segundos mientras MySQL inicializa la base de datos.

## Credenciales de prueba

| Rol       | Correo                        | Contraseña  |
|-----------|-------------------------------|-------------|
| Admin     | admin@ucu.edu.uy              | admin123    |
| Estudiante| facundo.gonzalez@ucu.edu.uy   | usuario123  |
| Estudiante| sofia.rodriguez@ucu.edu.uy    | usuario123  |

Las contraseñas se almacenan hasheadas con SHA-256 en la base de datos.

## Cómo correr sin Docker (desarrollo local)

Requiere MySQL 8 corriendo localmente. Crear la BD ejecutando los scripts en orden:

```bash
mysql -uroot -p < db/01schema.sql
mysql -uroot -p < db/02inserts.sql
mysql -uroot -p < db/04usuarios.sql
```

Luego instalar dependencias y arrancar:

```bash
cp .env.example .env        # ajustar DB_HOST=localhost
cd backend
pip install -r ../requirements.txt
python app.py
```

## Cómo reiniciar la base de datos desde cero

```bash
docker compose down -v
docker compose up --build
```

## Estructura del proyecto

```
actividades-deportivas-ucu/
├── backend/
│   ├── app.py          # Rutas Flask y control de sesión
│   ├── services.py     # Lógica de negocio y consultas SQL
│   ├── db.py           # Conexión MySQL + hasheo de contraseñas
│   ├── templates/      # HTML con Jinja2
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── index.html
│   │   ├── estudiantes.html
│   │   ├── disciplinas.html
│   │   ├── espacios.html
│   │   ├── actividades.html
│   │   ├── inscripciones.html
│   │   ├── asistencias.html
│   │   └── reportes.html
│   └── static/
│       └── styles.css
├── db/
│   ├── 01schema.sql    # Tablas, constraints, triggers
│   ├── 02inserts.sql   # Datos maestros y de prueba
│   ├── 03consultas.sql # Las 10 consultas requeridas
│   └── 04usuarios.sql  # Usuario MySQL de la app
├── docs/
│   ├── informe_grupal.md
│   └── informe_individual_modelo.md
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

## Funcionalidades

- Login con autenticación por sesión (rol admin y estudiante)
- ABM de estudiantes, disciplinas, espacios y actividades
- Gestión de inscripciones con cupo y lista de espera automática
- Promoción automática del primero en lista de espera al cancelar una confirmada
- Registro de asistencias solo para inscripciones confirmadas
- 10 reportes: 7 obligatorios + 3 adicionales

## Reglas de negocio

1. Solo se puede inscribir en actividades abiertas
2. No se supera el cupo máximo (si no hay cupo → lista de espera)
3. Un estudiante no puede inscribirse dos veces a la misma actividad
4. Solo se registra asistencia de estudiantes con inscripción confirmada
5. Actividades canceladas o finalizadas no aceptan nuevas inscripciones

Las reglas se validan en backend y se refuerzan en BD con claves únicas, CHECK y triggers.

## Seguridad

- Contraseñas almacenadas hasheadas con SHA-256
- Rutas protegidas por sesión (requieren login)
- Rutas de ABM restringidas al rol admin
- Usuario de BD con permisos mínimos (SELECT, INSERT, UPDATE, DELETE)
