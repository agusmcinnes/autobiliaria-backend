# Dockerfile para backend Django
FROM python:3.13-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

# Crear directorio de trabajo
WORKDIR $APP_HOME

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar codigo fuente
COPY . .

# Crear usuario no-root para seguridad
RUN addgroup --system django && \
    adduser --system --ingroup django django && \
    chown -R django:django $APP_HOME

# Crear directorios para static y media
RUN mkdir -p $APP_HOME/static $APP_HOME/media && \
    chown -R django:django $APP_HOME/static $APP_HOME/media

# Script de entrada
COPY --chown=django:django entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Cambiar a usuario no-root
USER django

ENTRYPOINT ["/entrypoint.sh"]

# Puerto por defecto
EXPOSE 8000

# Comando por defecto (Gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
