#!/bin/bash

set -e

DB_HOST=${DB_HOST:-db}

echo "Esperando a que PostgreSQL este disponible en $DB_HOST..."
while ! nc -z $DB_HOST 5432; do
  sleep 1
done
echo "PostgreSQL disponible!"

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Recopilando archivos estaticos..."
python manage.py collectstatic --noinput

echo "Iniciando servidor..."
exec "$@"
