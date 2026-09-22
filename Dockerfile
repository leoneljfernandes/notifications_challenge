# 1. Imagen base oficial ligera de Python
FROM python:3.11-slim

# 2. Instalar uv desde la imagen oficial de Astral
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Variables de entorno recomendadas para Python en contenedores
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Carpeta de trabajo dentro del contenedor
WORKDIR /code

# 5. Copiar únicamente los archivos de definición de dependencias
COPY pyproject.toml uv.lock ./

# 6. Instalar dependencias congeladas del lockfile sin instalar el proyecto aún
RUN uv sync --frozen --no-install-project

# 7. Copiar el código fuente de tu aplicación
COPY app/ ./app

# 8. Agregar el entorno virtual de uv al PATH
ENV PATH="/code/.venv/bin:$PATH"

# 9. Puerto expuesto
EXPOSE 8000

# 10. Comando de arranque (FastAPI con uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]