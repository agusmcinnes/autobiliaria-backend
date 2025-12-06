#!/bin/bash

# =============================================================================
# Script de Deploy para Autobiliaria Backend
# Uso: ./deploy.sh [prod|dev]
# =============================================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funciones de logging
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Validar argumento
ENV=${1:-prod}
if [[ "$ENV" != "prod" && "$ENV" != "dev" ]]; then
    log_error "Uso: $0 [prod|dev]"
    exit 1
fi

# Configuracion segun entorno
BASE_DIR="/home/deploy/autobiliaria"
if [ "$ENV" == "prod" ]; then
    PROJECT_DIR="${BASE_DIR}/prod/backend"
    COMPOSE_FILE="docker-compose.prod.yml"
    ENV_FILE=".env.prod"
    CONTAINER_BACKEND="autobiliaria-backend-prod"
    CONTAINER_DB="autobiliaria-db-prod"
    BRANCH="main"
else
    PROJECT_DIR="${BASE_DIR}/dev/backend"
    COMPOSE_FILE="docker-compose.dev.yml"
    ENV_FILE=".env.dev"
    CONTAINER_BACKEND="autobiliaria-backend-dev"
    CONTAINER_DB="autobiliaria-db-dev"
    BRANCH="develop"
fi

log_info "=========================================="
log_info "Deploy de Autobiliaria - Entorno: ${ENV^^}"
log_info "=========================================="

# =============================================================================
# 1. Backup de BD (solo en produccion)
# =============================================================================
if [ "$ENV" == "prod" ]; then
    log_step "1/6 Creando backup de base de datos..."

    BACKUP_DIR="${BASE_DIR}/backups"
    BACKUP_FILE="${BACKUP_DIR}/db_predeploy_$(date +%Y%m%d_%H%M%S).sql.gz"

    if docker ps | grep -q "$CONTAINER_DB"; then
        # Cargar variables de entorno para obtener credenciales
        if [ -f "${PROJECT_DIR}/${ENV_FILE}" ]; then
            source "${PROJECT_DIR}/${ENV_FILE}"
        fi

        docker exec "$CONTAINER_DB" pg_dump -U "${DB_USER}" "${DB_NAME}" 2>/dev/null | gzip > "$BACKUP_FILE"
        log_info "Backup creado: $BACKUP_FILE"

        # Mantener solo ultimos 10 backups
        ls -tp ${BACKUP_DIR}/db_*.sql.gz 2>/dev/null | tail -n +11 | xargs -I {} rm -- {} 2>/dev/null || true
    else
        log_warn "Contenedor de BD no esta corriendo, saltando backup"
    fi
else
    log_step "1/6 Saltando backup (entorno dev)"
fi

# =============================================================================
# 2. Actualizar codigo desde GitHub
# =============================================================================
log_step "2/6 Actualizando codigo desde GitHub..."

cd "$PROJECT_DIR"

# Guardar cambios locales si los hay
git stash 2>/dev/null || true

# Fetch y pull
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

log_info "Codigo actualizado a la ultima version de $BRANCH"

# =============================================================================
# 3. Verificar archivo de entorno
# =============================================================================
log_step "3/6 Verificando configuracion..."

if [ ! -f "${PROJECT_DIR}/${ENV_FILE}" ]; then
    log_error "Archivo ${ENV_FILE} no encontrado!"
    log_error "Crea el archivo con las variables de entorno necesarias"
    exit 1
fi

log_info "Archivo de configuracion encontrado"

# =============================================================================
# 4. Rebuild de contenedores
# =============================================================================
log_step "4/6 Reconstruyendo contenedores..."

cd "$PROJECT_DIR"

# Build con cache
docker compose -f "$COMPOSE_FILE" build

# Restart
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

log_info "Contenedores actualizados"

# =============================================================================
# 5. Esperar a que la BD este lista
# =============================================================================
log_step "5/6 Esperando a que la base de datos este lista..."

for i in {1..30}; do
    if docker exec "$CONTAINER_DB" pg_isready -U "${DB_USER:-postgres}" > /dev/null 2>&1; then
        log_info "Base de datos lista!"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "Timeout esperando base de datos"
        docker compose -f "$COMPOSE_FILE" logs "$CONTAINER_DB"
        exit 1
    fi
    sleep 1
done

# =============================================================================
# 6. Ejecutar migraciones y collectstatic
# =============================================================================
log_step "6/6 Ejecutando migraciones..."

# Migraciones
docker exec "$CONTAINER_BACKEND" python manage.py migrate --noinput

# Collectstatic
docker exec "$CONTAINER_BACKEND" python manage.py collectstatic --noinput

log_info "Migraciones completadas"

# =============================================================================
# Health check
# =============================================================================
log_info "Verificando estado del servicio..."

sleep 3

# Verificar que los contenedores esten corriendo
if docker ps | grep -q "$CONTAINER_BACKEND"; then
    log_info "Backend corriendo correctamente"
else
    log_error "Backend no esta corriendo!"
    docker logs "$CONTAINER_BACKEND" --tail 50
    exit 1
fi

# Verificar respuesta de la API
if [ "$ENV" == "prod" ]; then
    API_URL="http://localhost:8000/api/"
else
    API_URL="http://localhost:8001/api/"
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    log_info "API respondiendo correctamente (HTTP $HTTP_CODE)"
else
    log_warn "API responde con HTTP $HTTP_CODE (puede requerir autenticacion)"
fi

# =============================================================================
# Resumen
# =============================================================================
echo ""
log_info "=========================================="
log_info "Deploy completado exitosamente!"
log_info "=========================================="
log_info "Entorno: ${ENV^^}"
log_info "Rama: $BRANCH"
log_info "API: $API_URL"
echo ""
