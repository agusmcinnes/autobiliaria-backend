# Backups - Autobiliaria

## Configuracion Actual

| Aspecto | Valor |
|---------|-------|
| Frecuencia | Diario a las 3:00 AM (hora del servidor) |
| Retencion | 7 dias |
| Ubicacion | `/home/deploy/autobiliaria/backups/` |
| Log | `/var/log/autobiliaria-backup.log` |
| Script | `/home/deploy/autobiliaria/prod/scripts/backup.sh` |

## Que se respalda

1. **Base de datos PostgreSQL (PROD)**
   - Archivo: `db_YYYYMMDD_HHMMSS.sql.gz`
   - Contenido: Dump completo de la base de datos de produccion
   - Comprimido con gzip

2. **Archivos Media**
   - Archivo: `media_YYYYMMDD_HHMMSS.tar.gz`
   - Contenido: Imagenes de vehiculos y otros uploads
   - Solo se crea si hay archivos en el directorio media

## Comandos Utiles

### Ver backups existentes
```bash
ls -lh /home/deploy/autobiliaria/backups/
```

### Ejecutar backup manual
```bash
bash /home/deploy/autobiliaria/prod/scripts/backup.sh
```

### Ver log de backups
```bash
tail -50 /var/log/autobiliaria-backup.log
```

### Ver cron configurado
```bash
crontab -l
```

## Restaurar Backup

### Restaurar Base de Datos
```bash
# 1. Detener el backend para evitar conexiones activas
docker stop autobiliaria-backend-prod

# 2. Restaurar el backup (reemplazar ARCHIVO con el nombre del backup)
gunzip -c /home/deploy/autobiliaria/backups/db_XXXXXXXX_XXXXXX.sql.gz | \
  docker exec -i autobiliaria-db-prod psql -U autobiliaria_prod_user -d autobiliaria_prod

# 3. Reiniciar el backend
docker start autobiliaria-backend-prod
```

### Restaurar Archivos Media
```bash
# Extraer backup de media
cd /home/deploy/autobiliaria/prod
tar -xzf /home/deploy/autobiliaria/backups/media_XXXXXXXX_XXXXXX.tar.gz
```

## Recomendaciones de Seguridad

### 1. Backup Offsite (MUY RECOMENDADO)

Los backups actuales estan en el mismo servidor. **Si el servidor falla, se pierden los backups.**

#### Opcion A: Rclone + Google Drive (Gratis hasta 15GB)
```bash
# Instalar rclone
curl https://rclone.org/install.sh | sudo bash

# Configurar Google Drive
rclone config

# Agregar al final del script backup.sh:
rclone copy /home/deploy/autobiliaria/backups/ gdrive:autobiliaria-backups/
```

#### Opcion B: AWS S3
```bash
# Instalar AWS CLI
apt install awscli

# Configurar credenciales
aws configure

# Agregar al final del script backup.sh:
aws s3 sync /home/deploy/autobiliaria/backups/ s3://tu-bucket/autobiliaria-backups/
```

#### Opcion C: Rsync a otro servidor
```bash
# Agregar al final del script backup.sh:
rsync -avz /home/deploy/autobiliaria/backups/ usuario@otro-servidor:/backups/autobiliaria/
```

### 2. Monitoreo de Backups

Agregar notificacion por Telegram cuando falla un backup:

```bash
# Agregar al final del script backup.sh:
if [ $? -ne 0 ]; then
    curl -s -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
        -d "chat_id=<CHAT_ID>" \
        -d "text=Error en backup de Autobiliaria"
fi
```

### 3. Verificar Backups Periodicamente

Es importante verificar que los backups sean validos. Mensualmente:

```bash
# Probar que el backup se puede descomprimir
gunzip -t /home/deploy/autobiliaria/backups/db_XXXXXXXX_XXXXXX.sql.gz

# Verificar contenido del backup
gunzip -c /home/deploy/autobiliaria/backups/db_XXXXXXXX_XXXXXX.sql.gz | head -50
```

### 4. Aumentar Retencion

Para proyectos criticos, considerar aumentar la retencion editando `scripts/backup.sh`:

```bash
RETENTION_DAYS=30  # Cambiar de 7 a 30 dias
```

## Checklist de Backups

- [x] Script de backup configurado
- [x] Cron job activo (diario 3 AM)
- [x] Backup de base de datos
- [x] Backup de archivos media
- [ ] Backup offsite (S3, Google Drive, etc.)
- [ ] Notificaciones de error
- [ ] Verificacion mensual de backups
- [ ] Documentacion de restauracion probada

## Troubleshooting

Si hay problemas con los backups, revisar:

1. **Log de backups:**
   ```bash
   tail -100 /var/log/autobiliaria-backup.log
   ```

2. **Estado de contenedores:**
   ```bash
   docker ps
   ```

3. **Espacio en disco:**
   ```bash
   df -h
   ```

4. **Permisos del script:**
   ```bash
   ls -la /home/deploy/autobiliaria/prod/scripts/backup.sh
   chmod +x /home/deploy/autobiliaria/prod/scripts/backup.sh
   ```

## Credenciales Relacionadas

| Servicio | Usuario | Base de Datos |
|----------|---------|---------------|
| PostgreSQL PROD | `autobiliaria_prod_user` | `autobiliaria_prod` |
| PostgreSQL DEV | `autobiliaria_dev_user` | `autobiliaria_dev` |

> Las contraseñas estan en los archivos `.env.prod` y `.env.dev` en el servidor.
