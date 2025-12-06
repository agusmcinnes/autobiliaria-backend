#!/bin/bash

# =============================================================================
# Script de Backup para Autobiliaria
# Ejecutar via cron: 0 3 * * * /home/deploy/autobiliaria/backup.sh
# =============================================================================

set -e

# Configuracion
BASE_DIR="/home/deploy/autobiliaria"
BACKUP_DIR="${BASE_DIR}/backups"
PROJECT_DIR="${BASE_DIR}/prod/backend"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }

# Crear directorio de backups si no existe
mkdir -p "$BACKUP_DIR"

log "Iniciando backup..."

# =============================================================================
# Cargar variables de entorno
# =============================================================================
if [ -f "${PROJECT_DIR}/.env.prod" ]; then
    export $(grep -v '^#' "${PROJECT_DIR}/.env.prod" | xargs)
fi

DB_USER="${DB_USER:-autobiliaria_prod_user}"
DB_NAME="${DB_NAME:-autobiliaria_prod}"

# =============================================================================
# Backup de Base de Datos
# =============================================================================
log "Creando backup de base de datos..."

DB_BACKUP="${BACKUP_DIR}/db_${DATE}.sql.gz"

if docker ps | grep -q autobiliaria-db-prod; then
    docker exec autobiliaria-db-prod pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$DB_BACKUP"
    log "Backup de BD creado: $DB_BACKUP ($(du -h "$DB_BACKUP" | cut -f1))"
else
    log "ERROR: Contenedor autobiliaria-db-prod no esta corriendo"
    exit 1
fi

# =============================================================================
# Backup de archivos Media (imagenes de vehiculos)
# =============================================================================
log "Creando backup de archivos media..."

MEDIA_DIR="${BASE_DIR}/prod/media"
MEDIA_BACKUP="${BACKUP_DIR}/media_${DATE}.tar.gz"

if [ -d "$MEDIA_DIR" ] && [ "$(ls -A $MEDIA_DIR 2>/dev/null)" ]; then
    tar -czf "$MEDIA_BACKUP" -C "${BASE_DIR}/prod" media/
    log "Backup de media creado: $MEDIA_BACKUP ($(du -h "$MEDIA_BACKUP" | cut -f1))"
else
    log "Directorio media vacio o no existe, saltando..."
fi

# =============================================================================
# Limpiar backups antiguos
# =============================================================================
log "Limpiando backups antiguos (mas de ${RETENTION_DAYS} dias)..."

# Backups de BD
DELETED_DB=$(find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +${RETENTION_DAYS} -delete -print | wc -l)
log "Backups de BD eliminados: $DELETED_DB"

# Backups de media
DELETED_MEDIA=$(find "$BACKUP_DIR" -name "media_*.tar.gz" -mtime +${RETENTION_DAYS} -delete -print | wc -l)
log "Backups de media eliminados: $DELETED_MEDIA"

# =============================================================================
# Resumen
# =============================================================================
log "Backup completado!"
log "Espacio usado en backups: $(du -sh "$BACKUP_DIR" | cut -f1)"
log "Archivos en directorio de backups:"
ls -lh "$BACKUP_DIR" | tail -10

echo ""
