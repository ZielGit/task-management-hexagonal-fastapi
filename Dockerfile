# Multi-stage Dockerfile

# ============= BASE STAGE =============
FROM python:3.13-slim as base

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app


# ============= DEPENDENCIES STAGE =============
FROM base as dependencies

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt


# ============= DEVELOPMENT STAGE =============
FROM dependencies as development

# Copiar código fuente
COPY . .

# Crear directorio para logs
RUN mkdir -p /app/logs

# Exponer puerto
EXPOSE 8000

# Comando por defecto para desarrollo (con reload)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# ============= PRODUCTION STAGE =============
FROM dependencies as production

# Copiar solo lo necesario para producción
COPY ./src /app/src
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/alembic.ini

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Crear directorio para logs
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app/logs

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Comando por defecto para producción
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]


# ============= TEST STAGE =============
FROM dependencies as test

# Copiar todo el código
COPY . .

# Instalar dependencias adicionales de testing
RUN pip install pytest pytest-asyncio pytest-cov httpx

# Comando para ejecutar tests
CMD ["pytest", "tests/", "-v", "--cov=src", "--cov-report=html"]
