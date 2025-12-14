# Guía Completa de Administración del VPS - Autobiliaria

## Información General

| Concepto | Valor |
|----------|-------|
| **Proveedor** | Hostinger KVM 2 |
| **IP del servidor** | 92.112.177.217 |
| **Sistema operativo** | Ubuntu |
| **Dominio producción** | api.autobiliaria.cloud |
| **Dominio desarrollo** | api-dev.autobiliaria.cloud |

---

## 1. Cómo Conectarse al Servidor

### Desde Windows (PowerShell o CMD)

```bash
ssh root@92.112.177.217
```

Te pedirá la contraseña de root.

### Desde VS Code

1. Instalá la extensión "Remote - SSH"
2. Presioná `Ctrl+Shift+P` → "Remote-SSH: Connect to Host"
3. Escribí: `root@92.112.177.217`

---

## 2. Estructura de Archivos en el Servidor

```
/home/deploy/autobiliaria/
├── prod/                    # ← PRODUCCIÓN (rama main)
│   ├── docker-compose.prod.yml
│   ├── .env.prod            # Variables de entorno (SECRETO)
│   ├── apps/                # Código fuente
│   │   ├── usuarios/
│   │   ├── api/
│   │   ├── vendedores/
│   │   ├── parametros/
│   │   ├── vehiculos/
│   │   └── consultas/
│   ├── static/              # Archivos CSS/JS de Django
│   └── media/               # Imágenes subidas
│
├── dev/                     # ← DESARROLLO (rama develop)
│   ├── docker-compose.dev.yml
│   ├── .env.dev
│   ├── apps/
│   ├── static/
│   └── media/
│
├── backups/                 # Backups de base de datos
└── logs/                    # Logs de scripts
```

---

## 3. Comandos Esenciales

### 3.1 Ver estado de los contenedores

```bash
# Ver todos los contenedores corriendo
docker ps

# Deberías ver 4 contenedores:
# - autobiliaria-backend-prod (puerto 8000)
# - autobiliaria-db-prod
# - autobiliaria-backend-dev (puerto 8001)
# - autobiliaria-db-dev
```

### 3.2 Ver logs de la aplicación

```bash
# Logs de producción (los últimos 100 y seguir en vivo)
docker logs autobiliaria-backend-prod --tail 100 -f

# Logs de desarrollo
docker logs autobiliaria-backend-dev --tail 100 -f

# Para salir de los logs: Ctrl+C
```

### 3.3 Reiniciar la aplicación

```bash
# Reiniciar producción
cd /home/deploy/autobiliaria/prod
docker compose -f docker-compose.prod.yml restart

# Reiniciar desarrollo
cd /home/deploy/autobiliaria/dev
docker compose -f docker-compose.dev.yml restart
```

### 3.4 Detener la aplicación

```bash
# Detener producción (¡CUIDADO! La web quedará offline)
cd /home/deploy/autobiliaria/prod
docker compose -f docker-compose.prod.yml down

# Detener desarrollo
cd /home/deploy/autobiliaria/dev
docker compose -f docker-compose.dev.yml down
```

### 3.5 Iniciar la aplicación

```bash
# Iniciar producción
cd /home/deploy/autobiliaria/prod
docker compose -f docker-compose.prod.yml up -d

# Iniciar desarrollo
cd /home/deploy/autobiliaria/dev
docker compose -f docker-compose.dev.yml up -d
```

---

## 4. Deploy Automático (CI/CD)

El proyecto tiene **deploy automático** configurado con GitHub Actions:

| Rama | Ambiente | URL |
|------|----------|-----|
| `main` | Producción | https://api.autobiliaria.cloud |
| `develop` | Desarrollo | https://api-dev.autobiliaria.cloud |

### Cómo funciona

1. Hacés push a `develop` → Se despliega automáticamente a desarrollo
2. Hacés push a `main` → Se despliega automáticamente a producción

El CI/CD ejecuta automáticamente:
- `git pull` de la rama correspondiente
- `docker compose up -d --build --force-recreate`
- `python manage.py migrate`
- `python manage.py collectstatic`
- Arregla permisos de archivos estáticos

### Ver estado del deploy

En GitHub → Actions podés ver el estado de cada deploy.

### Deploy Manual (solo si falla el CI/CD)

```bash
# DESARROLLO
ssh root@92.112.177.217
cd /home/deploy/autobiliaria/dev
git pull origin develop
docker compose -f docker-compose.dev.yml up -d --build --force-recreate
docker exec autobiliaria-backend-dev python manage.py migrate

# PRODUCCIÓN
cd /home/deploy/autobiliaria/prod
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build --force-recreate
docker exec autobiliaria-backend-prod python manage.py migrate
```

---

## 5. Gestión de Base de Datos

### 5.1 Acceder a la base de datos

```bash
# Producción
docker exec -it autobiliaria-db-prod psql -U autobiliaria_prod_user -d autobiliaria_prod

# Desarrollo
docker exec -it autobiliaria-db-dev psql -U autobiliaria_dev_user -d autobiliaria_dev
```

Comandos útiles dentro de PostgreSQL:
```sql
\dt                     -- Ver todas las tablas
\d nombre_tabla         -- Ver estructura de una tabla
SELECT * FROM tabla;    -- Ver datos
\q                      -- Salir
```

### 5.2 Hacer backup de la base de datos

```bash
# Backup de producción
docker exec autobiliaria-db-prod pg_dump -U autobiliaria_prod_user autobiliaria_prod > /home/deploy/autobiliaria/backups/backup_prod_$(date +%Y%m%d_%H%M%S).sql

# Ver backups guardados
ls -la /home/deploy/autobiliaria/backups/
```

### 5.3 Restaurar un backup

```bash
# ¡CUIDADO! Esto reemplaza todos los datos actuales
cat /home/deploy/autobiliaria/backups/NOMBRE_ARCHIVO.sql | docker exec -i autobiliaria-db-prod psql -U autobiliaria_prod_user -d autobiliaria_prod
```

---

## 6. Gestión de Usuarios Django

### 6.1 Crear un nuevo superusuario

```bash
docker exec -it autobiliaria-backend-prod python manage.py createsuperuser
```

### 6.2 Cambiar contraseña de un usuario

```bash
docker exec autobiliaria-backend-prod python manage.py shell -c "
from apps.usuarios.models import Usuario
u = Usuario.objects.get(email='EMAIL_DEL_USUARIO')
u.set_password('NUEVA_CONTRASEÑA')
u.save()
print('Contraseña actualizada')
"
```

### 6.3 Ver usuarios existentes

```bash
docker exec autobiliaria-backend-prod python manage.py shell -c "
from apps.usuarios.models import Usuario
for u in Usuario.objects.all():
    print(f'{u.email} - Staff: {u.is_staff} - Active: {u.is_active}')
"
```

---

## 7. Certificados SSL (HTTPS)

Los certificados de Let's Encrypt se renuevan automáticamente. Pero podés verificar:

### Ver fecha de expiración

```bash
certbot certificates
```

### Renovar manualmente (si fuera necesario)

```bash
certbot renew
systemctl reload nginx
```

### Probar renovación automática

```bash
certbot renew --dry-run
```

---

## 8. Nginx (Servidor Web)

### Ver estado de Nginx

```bash
systemctl status nginx
```

### Reiniciar Nginx

```bash
systemctl restart nginx
```

### Ver errores de Nginx

```bash
# Errores de producción
tail -50 /var/log/nginx/autobiliaria_prod_error.log

# Errores de desarrollo
tail -50 /var/log/nginx/autobiliaria_dev_error.log
```

### Verificar configuración antes de reiniciar

```bash
nginx -t
```

### Archivo de configuración

```bash
nano /etc/nginx/sites-available/autobiliaria
```

---

## 9. Firewall (UFW)

### Ver estado

```bash
ufw status
```

### Puertos abiertos actualmente

- 22 (SSH) - para conectarte
- 80 (HTTP) - redirige a HTTPS
- 443 (HTTPS) - la web

---

## 10. Monitoreo y Diagnóstico

### Ver uso de disco

```bash
df -h
```

### Ver uso de memoria

```bash
free -h
```

### Ver procesos que más consumen

```bash
htop
# (salir con Q)
```

### Ver espacio usado por Docker

```bash
docker system df
```

### Limpiar recursos de Docker no usados

```bash
# Elimina contenedores detenidos, redes no usadas, imágenes huérfanas
docker system prune -f

# También eliminar imágenes no usadas (libera más espacio)
docker system prune -a -f
```

---

## 11. Problemas Comunes y Soluciones

### "La web no carga" (Error 502 Bad Gateway)

1. Verificar que los contenedores estén corriendo:
   ```bash
   docker ps
   ```

2. Si no aparece `autobiliaria-backend-prod`:
   ```bash
   cd /home/deploy/autobiliaria/prod
   docker compose -f docker-compose.prod.yml up -d
   ```

3. Ver logs para encontrar el error:
   ```bash
   docker logs autobiliaria-backend-prod --tail 50
   ```

### "No se ven los estilos del admin"

Problema de permisos. Ejecutar:
```bash
chmod 755 /home/deploy /home/deploy/autobiliaria
chown -R www-data:www-data /home/deploy/autobiliaria/prod/static
```

### "Error de base de datos"

1. Verificar que el contenedor de BD esté corriendo:
   ```bash
   docker ps | grep db-prod
   ```

2. Si no está, levantarlo:
   ```bash
   cd /home/deploy/autobiliaria/prod
   docker compose -f docker-compose.prod.yml up -d db-prod
   ```

### "No puedo conectarme por SSH"

1. Verificar que el servidor esté encendido desde el panel de Hostinger
2. Verificar que tu IP no esté bloqueada (contactar soporte Hostinger)

### "Disco lleno"

```bash
# Ver qué ocupa espacio
du -sh /home/deploy/autobiliaria/*

# Limpiar Docker
docker system prune -a -f

# Eliminar backups viejos
ls -la /home/deploy/autobiliaria/backups/
rm /home/deploy/autobiliaria/backups/backup_antiguo.sql
```

---

## 12. Credenciales Importantes

### Acceso SSH

| Campo | Valor |
|-------|-------|
| IP | 92.112.177.217 |
| Usuario | root |
| Contraseña | (la que configuraste en Hostinger) |

### Django Admin - Producción

| Campo | Valor |
|-------|-------|
| URL | https://api.autobiliaria.cloud/admin/ |
| Email | admin@autobiliaria.cloud |
| Password | Admin2024 |

### Django Admin - Desarrollo

| Campo | Valor |
|-------|-------|
| URL | https://api-dev.autobiliaria.cloud/admin/ |
| Email | admin@autobiliaria.cloud |
| Password | Admin2024 |

### Base de Datos Producción

| Campo | Valor |
|-------|-------|
| Host | db-prod (interno Docker) |
| Base de datos | autobiliaria_prod |
| Usuario | autobiliaria_prod_user |
| Contraseña | (ver archivo .env.prod) |

### Base de Datos Desarrollo

| Campo | Valor |
|-------|-------|
| Host | db-dev (interno Docker) |
| Base de datos | autobiliaria_dev |
| Usuario | autobiliaria_dev_user |
| Contraseña | (ver archivo .env.dev) |

---

## 13. Backups

### Backup automático de Hostinger

Hostinger hace backups automáticos del servidor completo. Podés restaurarlos desde:
- hPanel → VPS → Backups

### Backup manual de la base de datos

Hacelo regularmente:
```bash
docker exec autobiliaria-db-prod pg_dump -U autobiliaria_prod_user autobiliaria_prod > /home/deploy/autobiliaria/backups/backup_prod_$(date +%Y%m%d).sql
```

### Descargar backup a tu PC

Desde tu PC (no desde el servidor):
```bash
scp root@92.112.177.217:/home/deploy/autobiliaria/backups/NOMBRE.sql ./
```

---

## 14. Recomendaciones de Seguridad

1. **Cambiá la contraseña de root** regularmente desde el panel de Hostinger

2. **Nunca compartas las contraseñas** por chat/email sin cifrar

3. **Hacé backups** de la base de datos antes de cambios importantes

4. **Probá primero en desarrollo** antes de subir cambios a producción

5. **Revisá los logs** periódicamente para detectar problemas

---

## 15. Contactos de Emergencia

- **Soporte Hostinger**: Desde hPanel → Ayuda
- **Documentación Django**: https://docs.djangoproject.com/
- **Documentación Docker**: https://docs.docker.com/

---

## Resumen de Comandos Más Usados

```bash
# Conectarse
ssh root@92.112.177.217

# Ver contenedores
docker ps

# Ver logs producción
docker logs autobiliaria-backend-prod --tail 100 -f

# Ver logs desarrollo
docker logs autobiliaria-backend-dev --tail 100 -f

# Deploy automático (solo hacer push a GitHub)
git push origin develop   # → Despliega a desarrollo automáticamente
git push origin main      # → Despliega a producción automáticamente

# Deploy manual (solo si falla CI/CD)
cd /home/deploy/autobiliaria/prod
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build --force-recreate
docker exec autobiliaria-backend-prod python manage.py migrate

# Reiniciar producción
cd /home/deploy/autobiliaria/prod
docker compose -f docker-compose.prod.yml restart

# Backup de base de datos
docker exec autobiliaria-db-prod pg_dump -U autobiliaria_prod_user autobiliaria_prod > /home/deploy/autobiliaria/backups/backup_$(date +%Y%m%d).sql

# Cambiar contraseña usuario Django
docker exec autobiliaria-backend-prod python manage.py shell -c "
from apps.usuarios.models import Usuario
u = Usuario.objects.get(email='EMAIL')
u.set_password('NUEVA')
u.save()
"
```
