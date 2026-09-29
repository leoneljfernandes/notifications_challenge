# Notifications Challenge API

## Descripción del Proyecto
Esta es una API RESTful desarrollada con **FastAPI** y **SQLAlchemy** (modo asíncrono) enfocada en la gestión de notificaciones multicanal para usuarios. Implementa un sistema de autenticación seguro mediante tokens **JWT** y utiliza el **Patrón de Diseño Strategy** (Estrategia) para despachar notificaciones de manera dinámica a través de múltiples canales (`email`, `sms`, `push`).

La arquitectura está diseñada para ser escalable, cuenta con persistencia de datos en PostgreSQL, está completamente dockerizada, y posee una suite integral de pruebas End-to-End (E2E) para garantizar su robustez frente a errores de lógica o validaciones asíncronas.

## Badges
[![CircleCI](https://dl.circleci.com/status-badge/img/circleci/XZTndtAwv9XQN3WLyPAvnc/3MgNayMbunoTswwNGr1Vrd/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/circleci/XZTndtAwv9XQN3WLyPAvnc/3MgNayMbunoTswwNGr1Vrd/tree/main)

## Tecnologías Utilizadas
* **Lenguaje:** Python 3.14+
* **Framework Web:** FastAPI
* **ORM y Base de Datos:** SQLAlchemy 2.0 (modo asíncrono), PostgreSQL (con `asyncpg`), SQLite en memoria (para tests).
* **Validación y Tipado:** Pydantic V2
* **Autenticación y Seguridad:** JWT, Passlib (Bcrypt)
* **Testing:** Pytest, HTTPX (TestClient), aiosqlite
* **Infraestructura:** Docker, Docker Compose
* **Gestor de Paquetes:** uv

## Decisiones Arquitectónicas

1. **Patrón Strategy (Estrategia):**
   Se implementó para el envío de notificaciones. La lógica de despacho de cada canal (SMS, Email, Push) se encapsuló en clases independientes que heredan de una clase base. 
   * **¿Por qué?** Respeta el principio Open/Closed (SOLID). Si el día de mañana se necesita agregar un nuevo canal (ej. WhatsApp o Slack), solo se debe crear una nueva clase que herede de la base, sin modificar el despachador ni los endpoints, manteniendo el código escalable y fácil de mantener.

2. **Base de Datos y ORM Asíncrono (`asyncpg`):**
   Se optó por utilizar SQLAlchemy de forma puramente asíncrona.
   * **¿Por qué?** Las APIs web son inherentemente procesos limitados por Entrada/Salida (I/O-bound). Al hacer las llamadas a la base de datos asíncronas, el servidor FastAPI no bloquea el hilo principal y puede atender miles de peticiones concurrentes mientras espera que Postgres responda.

3. **Carga Proactiva de Relaciones (Eager Loading):**
   Para la relación entre Notificaciones y Usuarios se definió el parámetro `lazy="selectin"` en el modelo ORM.
   * **¿Por qué?** SQLAlchemy asíncrono no soporta el "Lazy Loading" clásico, lo que genera errores `MissingGreenlet` en tiempo de ejecución. Al configurarlo de esta manera, nos aseguramos de que el usuario siempre esté disponible en memoria cuando se despacha la notificación.

4. **Testing Aislado (Clean-Execute-Clean):**
   La suite de pruebas utiliza una base de datos local SQLite configurada con `aiosqlite`, aplicando el patrón Clean-Execute-Clean a través de fixtures de Pytest.
   * **¿Por qué?** Garantiza que cada test se ejecute en un entorno prístino (tablas creadas y destruidas por cada test), asegurando que ninguna prueba falle por "datos basura" dejados por un test anterior y aislando la base de datos de producción/desarrollo.

## Estructura del Proyecto

```text
notifications_challenge/
├── app/                            # Código fuente principal de la aplicación
│   ├── api/                        # Controladores/Endpoints de la API
│   │   ├── notification.py         # Endpoints para crear/modificar/borrar notificaciones
│   │   └── users.py                # Endpoints para registro de usuarios
│   ├── auth.py                     # Lógica de autenticación (JWT, Hash de contraseñas)
│   ├── config.py                   # Configuraciones globales (Pydantic Settings)
│   ├── crud/                       # Operaciones de Base de Datos (Create, Read, Update, Delete)
│   │   ├── notification.py
│   │   └── user.py
│   ├── database.py                 # Configuración del Engine Asíncrono de SQLAlchemy
│   ├── main.py                     # Punto de entrada de la aplicación FastAPI (Lifespan events)
│   ├── models/                     # Modelos ORM (SQLAlchemy)
│   │   ├── notification.py
│   │   └── user.py
│   ├── schemas/                    # Validadores y serializadores de Pydantic
│   │   ├── notification.py
│   │   └── user.py
│   ├── services/                   # Lógica de negocio core (Patrón Strategy)
│   │   ├── channel.py              # Clase Base (Strategy Interface)
│   │   ├── dispatcher.py           # Despachador (Contexto del Strategy)
│   │   ├── email.py                # Estrategia concreta de Email
│   │   ├── push.py                 # Estrategia concreta de notificaciones Push
│   │   └── sms.py                  # Estrategia concreta de SMS
│   └── utils/
├── tests/                          # Suite de pruebas E2E (Pytest)
│   ├── conftest.py                 # Configuración DB asíncrona en memoria para tests (Clean-Setup-Clean)
│   ├── test_login.py               # Casos de prueba de autenticación
│   ├── test_notifications.py       # Casos de prueba de notificaciones, estrategias y validaciones
│   └── test_users.py               # Casos de prueba de registro
├── docker-compose.yml              # Orquestación de contenedores (App FastAPI + PostgreSQL)
├── Dockerfile                      # Definición de la imagen de Docker
├── pyproject.toml                  # Dependencias del entorno gestionadas por 'uv'
├── pytest.ini                      # Configuración de rutas (PYTHONPATH) para pytest
└── README.md                       # Documentación del proyecto
```

## Instalación y Configuración

El proyecto utiliza `uv` como gestor de paquetes (mucho más rápido que pip). Sigue estos pasos para prepararlo en tu entorno local:

1. **Sincronizar e instalar dependencias:**
   Ejecuta el siguiente comando en la raíz del proyecto para descargar todas las librerías necesarias:
   ```bash
   uv sync
   ```

2. **Configuración de Variables de Entorno:**
   Asegúrate de contar con el archivo `.env` en la raíz del proyecto. Debe contener las credenciales de tu base de datos y la clave JWT:
   ```ini
   POSTGRES_USER=tu_usuario
   POSTGRES_PASSWORD=tu_contraseña
   POSTGRES_DB=notifications_db
   # URL para el contenedor de Postgres
   DATABASE_URL=postgresql+asyncpg://tu_usuario:tu_contraseña@postgres_db:5432/notifications_db
   SECRET_KEY=tu_super_clave_secreta_jwt
   ```

## Ejecución de la API

La aplicación está dockerizada para evitar problemas de compatibilidad de entornos. La forma recomendada de levantar el proyecto es a través de Docker Compose, el cual levantará tanto la API como la base de datos PostgreSQL.

**Levantar los contenedores:**
```bash
docker compose up --build
```

Una vez que los contenedores estén corriendo ("Container postgres_db Healthy"), podrás acceder a:
- **API Base:** [http://localhost:8000](http://localhost:8000)
- **Documentación Interactiva (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

Para detener la aplicación, presiona `CTRL+C` en la terminal o ejecuta:
```bash
docker compose down
```

## Ejecución de Pruebas (Tests E2E)

El proyecto cuenta con una suite completa de pruebas End-to-End. Utilizan una base de datos de pruebas (SQLite asíncrona por archivo) operando bajo el patrón **Clean-Execute-Clean**. Esto garantiza que cada prueba levante tablas limpias y luego las borre, evitando modificar los datos reales de tu desarrollo (PostgreSQL).

Para ejecutar toda la suite de pruebas localmente:
```bash
uv run pytest tests/ -v
```

Si deseas ejecutar un archivo de pruebas en específico:
```bash
uv run pytest tests/test_notifications.py -v
```

## Aspectos Posibles a Mejorar

Toda aplicación tiene oportunidad de crecimiento. Para llevar este proyecto a un nivel totalmente productivo ("Enterprise-grade"), se recomendaría implementar:

1. **Colas de Mensajería Asíncrona (Celery / RabbitMQ / Redis):**
   Actualmente, la petición de despachar la notificación se procesa en el mismo hilo HTTP (aunque de forma asíncrona). Si el envío del SMS tarda 5 segundos por el proveedor, la respuesta a la API tardará 5 segundos. Introducir un "Task Queue" permitiría retornar un `202 Accepted` de manera instantánea y delegar el envío a un worker secundario en background (ej. Celery, ARQ).
2. **Migraciones de Base de Datos (Alembic):**
   Hoy en día la app utiliza `Base.metadata.create_all` al inicializar. En producción es crucial tener control de versiones sobre los cambios estructurales de la base de datos utilizando **Alembic** para correr migraciones de forma segura.
3. **Paginación:**
   El endpoint `/my-notifications` devuelve una lista plana. Si un usuario tiene miles de notificaciones, esto podría impactar el rendimiento. Sería ideal implementar paginación mediante `limit` y `offset` (o cursores).
4. **Manejo Centralizado de Excepciones:**
   El patrón Strategy arroja actualmente `ValueError` cuando faltan parámetros específicos en la metadata. Crear un *Exception Handler* global en FastAPI que atrape estos `ValueError` específicos y los traduzca amigablemente en un `HTTP 400 Bad Request` mejoraría significativamente la experiencia del desarrollador que consuma la API.
