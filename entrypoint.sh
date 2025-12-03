#!/bin/bash

set -e

echo "Esperando a que PostgreSQL este disponible..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL disponible!"

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Recopilando archivos estaticos..."
python manage.py collectstatic --noinput

echo "Iniciando servidor..."
exec "$@"
