# Integración con Mercado Libre - Documentación Técnica

## Resumen

Se implementó una integración completa con la API de Mercado Libre que permite:

- Conectar la cuenta de ML mediante OAuth2
- Importar publicaciones existentes de ML
- Vincular publicaciones a vehículos del sistema por patente
- Publicar vehículos desde el sistema a ML
- Gestionar estados de publicaciones (pausar, activar, cerrar)

---

## Arquitectura Implementada

### Backend

**Nueva app**: `apps/integraciones/mercadolibre/`

```
apps/integraciones/mercadolibre/
├── __init__.py
├── apps.py
├── models.py          # MLCredential, MLPublication, MLSyncLog
├── services.py        # MLClient, MLSyncService
├── views.py           # ViewSets y endpoints
├── serializers.py     # Serializers DRF
├── urls.py            # Rutas /api/mercadolibre/*
├── admin.py           # Admin Django
└── migrations/
    └── 0001_initial.py
```

### Modelos

| Modelo | Descripción |
|--------|-------------|
| `MLCredential` | Tokens OAuth2 (access_token, refresh_token, expires_at) |
| `MLPublication` | Publicaciones importadas/creadas en ML |
| `MLSyncLog` | Log de acciones (importar, crear, pausar, etc.) |

### Endpoints API

```
# Estado y conexión
GET    /api/mercadolibre/status/              # Estado de conexión
POST   /api/mercadolibre/auth/url/            # Obtener URL OAuth2
GET    /api/mercadolibre/auth/callback/       # Callback OAuth2
DELETE /api/mercadolibre/disconnect/          # Desconectar cuenta

# Sincronización
POST   /api/mercadolibre/sync/                # Importar publicaciones
GET    /api/mercadolibre/statistics/          # Estadísticas

# Publicaciones
GET    /api/mercadolibre/publications/        # Listar publicaciones
POST   /api/mercadolibre/publications/{id}/link/    # Vincular a vehículo
POST   /api/mercadolibre/publications/{id}/unlink/  # Desvincular
PATCH  /api/mercadolibre/publications/{id}/status/  # Cambiar estado

# Acciones en vehículos
POST   /api/vehiculos/{id}/publicar-ml/       # Publicar en ML
PATCH  /api/vehiculos/{id}/ml-status/         # Pausar/activar
DELETE /api/vehiculos/{id}/cerrar-ml/         # Cerrar publicación

# Logs
GET    /api/mercadolibre/logs/                # Ver logs de sync
```

### Frontend

**Nuevas páginas**:
- `/admin/mercadolibre/` - Dashboard con estado de conexión y estadísticas
- `/admin/mercadolibre/publicaciones/` - Lista de publicaciones ML

**Nuevo servicio**:
- `services/mercadolibre-api.ts` - Cliente API para ML

**Modificaciones**:
- `components/admin-sidebar.tsx` - Agregado link a Mercado Libre

---

## Variables de Entorno Requeridas

```bash
# Mercado Libre OAuth2
ML_APP_ID=123456789012345678
ML_SECRET_KEY=AbCdEfGhIjKlMnOpQrStUvWxYz123456
ML_REDIRECT_URI=https://api.autobiliaria.cloud/api/mercadolibre/auth/callback/

# URLs del sistema
FRONTEND_URL=https://admin.autobiliaria.cloud
MEDIA_BASE_URL=https://api.autobiliaria.cloud
```

---

## Deploy de DEV a PROD

### 1. Verificar que todo funciona en DEV

```bash
# Verificar contenedor corriendo
ssh root@92.112.177.217
docker ps | grep autobiliaria-backend-dev
```

### 2. Merge a main

```bash
# En local
git checkout main
git merge develop
git push origin main
```

### 3. Deploy automático (si hay CI/CD configurado)

El push a `main` debería disparar el deploy automático via GitHub Actions.

### 4. Deploy manual (si es necesario)

```bash
# En el servidor
ssh root@92.112.177.217
cd /home/deploy/autobiliaria/prod

# Pull cambios
git pull origin main

# Rebuild y restart
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build

# Aplicar migraciones
docker exec autobiliaria-backend-prod python manage.py migrate
```

### 5. Configurar variables de entorno en PROD

```bash
# Editar .env.prod
nano /home/deploy/autobiliaria/prod/.env.prod

# Agregar:
ML_APP_ID=xxx
ML_SECRET_KEY=xxx
ML_REDIRECT_URI=https://api.autobiliaria.cloud/api/mercadolibre/auth/callback/
FRONTEND_URL=https://admin.autobiliaria.cloud
MEDIA_BASE_URL=https://api.autobiliaria.cloud

# Restart para aplicar cambios
docker compose -f docker-compose.prod.yml restart
```

### 6. Verificar

```bash
# Test endpoint
curl https://api.autobiliaria.cloud/api/mercadolibre/status/

# Ver logs
docker logs autobiliaria-backend-prod --tail 50
```

---

## Flujo OAuth2

```
1. Usuario hace clic en "Conectar con Mercado Libre"
2. Frontend llama POST /api/mercadolibre/auth/url/
3. Backend genera URL con client_id, redirect_uri, state
4. Usuario es redirigido a auth.mercadolibre.com.ar
5. Usuario autoriza la aplicación
6. ML redirige a /api/mercadolibre/auth/callback/?code=XXX
7. Backend intercambia code por access_token + refresh_token
8. Guarda credenciales en MLCredential
9. Redirige al frontend con éxito
```

---

## Matching por Patente

El sistema extrae automáticamente la patente de las publicaciones de ML usando:

1. **Atributos de ML**: Busca `LICENSE_PLATE` o `VEHICLE_LICENSE_PLATE`
2. **Regex en título**: Patrones argentinos
   - Nuevo formato: `AA 123 BB` o `AA123BB`
   - Viejo formato: `ABC 123` o `ABC123`

Al sincronizar, si encuentra un vehículo en el sistema con la misma patente, lo vincula automáticamente.

---

## Troubleshooting

### Error "Las credenciales de autenticación no se proveyeron"
- Normal si no estás autenticado. Los endpoints requieren JWT.

### Error al conectar con ML
- Verificar que `ML_APP_ID` y `ML_SECRET_KEY` estén configurados
- Verificar que `ML_REDIRECT_URI` coincida exactamente con el configurado en ML

### Token expirado
- El sistema renueva automáticamente el access_token usando el refresh_token
- Si el refresh_token expira (6 meses), el usuario debe reconectar

### Container reiniciando
- Revisar logs: `docker logs autobiliaria-backend-dev --tail 100`
- Errores comunes: imports faltantes, variables de entorno

---

## Archivos Modificados/Creados

### Backend
- `apps/integraciones/` (nuevo directorio completo)
- `config/settings.py` - Agregada app y variables ML
- `apps/api/urls.py` - Agregadas rutas ML
- `apps/vehiculos/views.py` - Acciones ML en vehículos
- `requirements.txt` - Agregado `requests`

### Frontend
- `services/mercadolibre-api.ts` (nuevo)
- `app/admin/mercadolibre/page.tsx` (nuevo)
- `app/admin/mercadolibre/publicaciones/page.tsx` (nuevo)
- `components/admin-sidebar.tsx` - Link a ML


  Estado Actual

  | Componente      | DEV                        | PROD                 |
  |-----------------|----------------------------|----------------------|
  | Backend ML      | ✅ Deployado y funcionando | ❌ Pendiente         |
  | Frontend ML     | ✅ Código listo (en repo)  | ❌ Pendiente         |
  | Migraciones     | ✅ Aplicadas               | ❌ Pendiente         |
  | Credenciales ML | ❌ Faltan configurar       | ❌ Faltan configurar |

  Cuando tengas las credenciales del cliente

  Configurarlas en el servidor de dev:

  ssh root@92.112.177.217
  nano /home/deploy/autobiliaria/dev/.env.dev

  # Agregar estas 3 líneas:
  ML_APP_ID=xxx
  ML_SECRET_KEY=xxx
  ML_REDIRECT_URI=https://api-dev.autobiliaria.cloud/api/mercadolibre/auth/callback/

  # Reiniciar
  cd /home/deploy/autobiliaria/dev
  docker compose -f docker-compose.dev.yml restart

  Archivos clave de referencia

  - Documentación técnica: docs/mercadolibre-integracion.md
  - Plan original: /Users/agusmc/.claude/plans/piped-forging-bengio.md
  - Servicio principal: apps/integraciones/mercadolibre/services.py
  - Frontend pages: app/admin/mercadolibre/ (en el repo web)

  Para PROD (cuando esté listo)

  1. Merge develop → main en ambos repos
  2. Cambiar redirect URI en la app de ML a la URL de prod
  3. Configurar variables en .env.prod
  4. Aplicar migraciones en prod