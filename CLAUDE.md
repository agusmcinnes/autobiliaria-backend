# Autobiliaria - Backend

Sistema de gestion para automotora/concesionaria de vehiculos.

## Stack Tecnologico

- Python 3.13
- Django 5.2.8
- Django REST Framework 3.16.1
- PostgreSQL 16 (Docker)
- JWT (SimpleJWT)
- django-filter (filtros avanzados)
- Gunicorn (produccion)
- psycopg 3.2.3

## Estructura del Proyecto

```
backend/
├── config/                     # Configuracion Django
│   ├── settings.py             # JWT, DRF, CORS, seguridad
│   └── urls.py                 # Rutas principales
├── apps/
│   ├── usuarios/               # Sistema de autenticacion (IMPLEMENTADO)
│   │   ├── models.py           # Modelo Usuario personalizado
│   │   ├── managers.py         # UsuarioManager
│   │   ├── serializers.py      # JWT serializers
│   │   ├── views.py            # Login, logout, refresh, me
│   │   ├── urls.py             # /api/auth/*
│   │   └── admin.py            # Admin personalizado
│   ├── api/                    # Router principal (IMPLEMENTADO)
│   │   └── urls.py             # Agrupa todas las rutas + endpoint raiz
│   ├── vendedores/             # Gestion de vendedores (IMPLEMENTADO)
│   │   ├── models.py           # Modelo Vendedor
│   │   ├── serializers.py      # VendedorSerializer, VendedorListSerializer
│   │   ├── views.py            # VendedorViewSet (CRUD completo)
│   │   ├── urls.py             # /api/vendedores/*
│   │   └── admin.py            # Admin con fieldsets
│   ├── parametros/             # Catalogos del sistema (IMPLEMENTADO)
│   │   ├── models.py           # 10 modelos de parametros
│   │   ├── serializers.py      # Serializers para cada parametro
│   │   ├── views.py            # ViewSets con CRUD completo
│   │   ├── urls.py             # /api/parametros/*
│   │   ├── admin.py            # Admin para todos los parametros
│   │   └── management/commands/cargar_parametros.py
│   └── vehiculos/              # Inventario de vehiculos (IMPLEMENTADO)
│       ├── models.py           # Vehiculo, ImagenVehiculo
│       ├── serializers.py      # VehiculoSerializer, VehiculoListSerializer
│       ├── views.py            # VehiculoViewSet (CRUD + acciones extra)
│       ├── filters.py          # VehiculoFilter (filtros avanzados)
│       ├── urls.py             # /api/vehiculos/*
│       └── admin.py            # Admin con inlines
├── docs/                       # Documentacion de APIs
│   ├── vendedores.md
│   └── parametros.md
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── requirements.txt
└── .env.example
```

## Apps Registradas en INSTALLED_APPS

- `apps.usuarios` - Sistema de autenticacion
- `apps.api` - Router de API
- `apps.vendedores` - Gestion de vendedores (duenos de autos)
- `apps.parametros` - Catalogos (marcas, modelos, combustibles, etc.)
- `apps.vehiculos` - Inventario de vehiculos

---

## Modelo de Usuario

```python
Usuario(AbstractUser):
    email          # Identificador principal (unique) - usado para login
    username       # Opcional, para mostrar en UI
    first_name     # Nombre (requerido)
    last_name      # Apellido (requerido)
    rol            # 'admin' | 'staff'
    is_active      # Estado
    created_at     # Fecha creacion
    updated_at     # Fecha actualizacion
```

- Email como identificador principal para login
- Username opcional
- Roles: admin y staff (ambos tienen acceso al Django Admin)
- Solo se crean desde Django Admin (no hay registro publico)

## Modelo Vendedor

```python
Vendedor(Model):
    nombre         # CharField(100)
    apellido       # CharField(100)
    email          # EmailField (unique)
    direccion      # CharField(255)
    celular        # CharField(20)
    dni            # CharField(20, unique)
    tiene_cartel   # BooleanField (default=False)
    activo         # BooleanField (default=True)
    comentarios    # TextField (opcional)
    created_at     # DateTimeField (auto)
    updated_at     # DateTimeField (auto)
```

## Modelos de Parametros

```python
# Modelo base abstracto
ParametroBase(Model):
    nombre         # CharField(100)
    activo         # BooleanField (default=True)
    orden          # PositiveIntegerField (default=0)
    created_at     # DateTimeField (auto)
    updated_at     # DateTimeField (auto)

# Modelos concretos (heredan de ParametroBase)
Caja              # Automatica, Manual
Combustible       # Diesel, Nafta, GNC, etc.
Condicion         # Excelente, Buen estado, etc.
Estado            # 0Km, Usado, Nuevo
Iva               # Consumidor Final, Inscripto, etc.
Localidad         # Capital Federal, Mar del Plata, etc.
Moneda            # ARS, USD, EUROS, YENS
Segmento          # SUV, Sedan, Pick up, etc.
Marca             # Ford, Chevrolet, Toyota, etc.
Modelo            # Focus, Corolla, etc. (FK a Marca)
```

## Modelo Vehiculo

```python
Vehiculo(Model):
    # Relaciones
    marca              # FK -> Marca
    modelo             # FK -> Modelo (debe pertenecer a marca)
    segmento1          # FK -> Segmento (opcional)
    segmento2          # FK -> Segmento (opcional)
    combustible        # FK -> Combustible
    caja               # FK -> Caja
    estado             # FK -> Estado
    condicion          # FK -> Condicion
    moneda             # FK -> Moneda
    vendedor_dueno     # FK -> Vendedor
    cargado_por        # FK -> Usuario

    # Campos generales
    version            # CharField(100), opcional
    patente            # CharField(10), unique
    anio               # PositiveIntegerField
    km                 # PositiveIntegerField
    color              # CharField(50)
    precio             # DecimalField(12,2)
    porcentaje_financiacion  # DecimalField(5,2), opcional
    cant_duenos        # PositiveSmallIntegerField

    # Booleans estado
    vtv, plan_ahorro, reservado, vendido

    # Booleans web
    mostrar_en_web, destacar_en_web, oportunidad, oportunidad_grupo, reventa

    # MercadoLibre
    publicado_en_ml    # bool
    ml_item_id         # CharField(50), unique, nullable
    ml_estado          # CharField(20)
    ml_fecha_sync      # DateTimeField, nullable
    ml_error           # TextField
    ml_permalink       # URLField

    # Otros
    comentario_carga   # TextField
    created_at, updated_at, deleted_at  # Soft delete
```

## Modelo ImagenVehiculo

```python
ImagenVehiculo(Model):
    vehiculo           # FK -> Vehiculo (CASCADE)
    imagen             # ImageField(upload_to='vehiculos/%Y/%m/')
    orden              # PositiveSmallIntegerField
    es_principal       # BooleanField
    created_at
```

**Regla:** Maximo 15 imagenes por vehiculo

---

## Endpoints API

### Autenticacion (`/api/auth/`)

| Metodo | URL | Descripcion | Auth |
|--------|-----|-------------|------|
| GET | `/api/` | Info de endpoints disponibles | No |
| POST | `/api/auth/login/` | Login (email + password) | No |
| POST | `/api/auth/refresh/` | Refrescar access token | No |
| POST | `/api/auth/logout/` | Cerrar sesion | Si |
| GET | `/api/auth/me/` | Usuario actual | Si |

### Vendedores (`/api/vendedores/`)

| Metodo | URL | Descripcion | Auth |
|--------|-----|-------------|------|
| GET | `/api/vendedores/` | Listar vendedores | Si |
| POST | `/api/vendedores/` | Crear vendedor | Si |
| GET | `/api/vendedores/{id}/` | Detalle vendedor | Si |
| PUT | `/api/vendedores/{id}/` | Actualizar vendedor | Si |
| PATCH | `/api/vendedores/{id}/` | Actualizar parcial | Si |
| DELETE | `/api/vendedores/{id}/` | Eliminar vendedor | Si |

**Filtros:** `?activo=true`, `?tiene_cartel=true`, `?search=texto`

### Parametros (`/api/parametros/`)

Todos los parametros tienen CRUD completo:

| Recurso | URL |
|---------|-----|
| Cajas | `/api/parametros/cajas/` |
| Combustibles | `/api/parametros/combustibles/` |
| Condiciones | `/api/parametros/condiciones/` |
| Estados | `/api/parametros/estados/` |
| IVAs | `/api/parametros/ivas/` |
| Localidades | `/api/parametros/localidades/` |
| Marcas | `/api/parametros/marcas/` |
| Modelos | `/api/parametros/modelos/` |
| Monedas | `/api/parametros/monedas/` |
| Segmentos | `/api/parametros/segmentos/` |

**Filtros:** `?activo=true`, `?search=texto`, `?marca={id}` (solo modelos)

### Vehiculos (`/api/vehiculos/`)

| Metodo | URL | Descripcion | Auth |
|--------|-----|-------------|------|
| GET | `/api/vehiculos/` | Listar vehiculos | Si |
| POST | `/api/vehiculos/` | Crear vehiculo | Si |
| GET | `/api/vehiculos/{id}/` | Detalle vehiculo | Si |
| PUT | `/api/vehiculos/{id}/` | Actualizar vehiculo | Si |
| PATCH | `/api/vehiculos/{id}/` | Actualizar parcial | Si |
| DELETE | `/api/vehiculos/{id}/` | Soft delete | Si |
| POST | `/api/vehiculos/{id}/imagenes/` | Subir imagen | Si |
| DELETE | `/api/vehiculos/{id}/imagenes/{img_id}/` | Eliminar imagen | Si |
| POST | `/api/vehiculos/{id}/restaurar/` | Restaurar eliminado | Si |
| PATCH | `/api/vehiculos/{id}/marcar-vendido/` | Marcar vendido | Si |
| PATCH | `/api/vehiculos/{id}/marcar-reservado/` | Toggle reservado | Si |

**Filtros:**
- Por FK: `?marca=1`, `?modelo=5`, `?combustible=2`, `?caja=1`, `?estado=1`, `?condicion=1`, `?moneda=1`, `?segmento=10`, `?vendedor=3`
- Por rango: `?precio_min=10000&precio_max=50000`, `?anio_min=2018&anio_max=2023`, `?km_max=100000`
- Booleanos: `?vendido=false`, `?reservado=false`, `?disponible=true`, `?mostrar_en_web=true`, `?publicado_en_ml=true`
- Busqueda: `?search=ford+focus`
- Orden: `?ordering=-precio,anio`
- Incluir eliminados: `?include_deleted=true`

---

## Docker

### Levantar proyecto

```bash
cd backend
docker-compose up --build -d
```

### Crear superusuario

```bash
docker-compose exec backend python manage.py createsuperuser
```

### Cargar parametros iniciales

```bash
docker-compose exec backend python manage.py cargar_parametros --csv /app/automan.csv
```

### Ver logs

```bash
docker-compose logs -f backend
```

### Detener

```bash
docker-compose down
```

### Resetear BD (elimina datos)

```bash
docker-compose down -v
docker-compose up -d
```

---

## Seguridad Implementada

- JWT con access (15 min) y refresh (1 dia)
- Rotacion automatica de refresh tokens
- Blacklist de tokens en logout
- Password minimo 8 caracteres
- Rate limiting: 5 login/min, 100 req/min
- Usuario no-root en Docker
- BD no expuesta externamente (solo accesible desde backend)
- CORS configurado
- Filtros globales con django-filter

## Variables de Entorno (.env)

```bash
DJANGO_SECRET_KEY=cambiar-en-produccion
DJANGO_DEBUG=True
DB_NAME=autobiliaria
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:3000
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Acceso

- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

---

## Documentacion Detallada

- `docs/vendedores.md` - API de vendedores con ejemplos
- `docs/parametros.md` - API de parametros con ejemplos
- `docs/vehiculos.md` - API de vehiculos con ejemplos

## Datos Cargados

### Parametros
- Cajas: 2
- Combustibles: 5
- Condiciones: 6
- Estados: 3
- IVAs: 5
- Localidades: 8
- Monedas: 4
- Segmentos: 43
- Marcas: ~130
- Modelos: ~440

---

## Almacenamiento de Imagenes

### Configuracion Actual

```python
# apps/vehiculos/models.py
imagen = ImageField(upload_to='vehiculos/%Y/%m/')
```

- Imagenes almacenadas en carpeta `media/vehiculos/YYYY/MM/`
- Maximo 15 imagenes por vehiculo
- Formatos soportados: todos los que soporte Pillow (JPEG, PNG, WebP, etc.)

### Configuracion para Produccion (Hostinger KVM 2)

La implementacion actual es adecuada para un VPS KVM. Recomendaciones:

1. **Nginx para archivos estaticos:**
```nginx
location /media/ {
    alias /app/media/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

location /static/ {
    alias /app/staticfiles/;
    expires 30d;
}
```

2. **Variables de entorno:**
```bash
MEDIA_URL=/media/
MEDIA_ROOT=/app/media/
```

3. **Backup automatico:**
- Configurar cron job para backup diario de `media/`
- rsync a almacenamiento externo o S3

### Optimizaciones Futuras

Si el volumen de imagenes crece significativamente:

1. **Procesamiento de imagenes:**
   - Agregar django-imagekit para thumbnails automaticos
   - Comprimir imagenes al subir (80% calidad JPEG)
   - Resize a maximo 1920x1080 para web

2. **CDN/Almacenamiento externo:**
   - django-storages + Cloudflare R2 (compatible S3, bajo costo)
   - O Amazon S3 + CloudFront

3. **Lazy loading en frontend:**
   - Cargar thumbnails en listados
   - Imagen completa solo en detalle

---

## Integracion MercadoLibre (Pendiente)

### Campos Preparados en Modelo Vehiculo

```python
publicado_en_ml     # Control interno: publicar o no
ml_item_id          # ID de MercadoLibre (MLA123456789)
ml_estado           # active, paused, closed, under_review
ml_fecha_sync       # Ultima sincronizacion exitosa
ml_error            # Ultimo error de la API
ml_permalink        # URL directa a la publicacion
```

### Flujo de Integracion Sugerido

1. **Autenticacion OAuth2:**
   - Crear app en developers.mercadolibre.com.ar
   - Almacenar access_token y refresh_token
   - Renovar automaticamente antes de expiracion

2. **Sincronizacion:**
   - Publicar: `POST /items` con datos del vehiculo
   - Actualizar: `PUT /items/{ml_item_id}`
   - Pausar: `PUT /items/{ml_item_id}` con `status: paused`
   - Finalizar: `PUT /items/{ml_item_id}` con `status: closed`

3. **Campos a agregar (futuro):**
```python
# En Vehiculo
ml_categoria_id    # ID de categoria ML (MLA1744 = Autos)
ml_listing_type    # gold_special, gold, silver (tipo publicacion)

# Nuevo modelo para tracking
class MLSyncLog(Model):
    vehiculo       # FK
    accion         # create, update, pause, close
    request_data   # JSON enviado
    response_data  # JSON recibido
    success        # bool
    error_message  # texto error
    created_at
```

4. **Mapeo de atributos:**
   - Marca/Modelo: Buscar IDs en API ML (`/categories/MLA1744/attributes`)
   - Kilometros, Ano, Color: Atributos directos
   - Precio: En la moneda correcta (ARS)
   - Imagenes: Subir a ML y obtener URLs

5. **Celery tasks sugeridas:**
   - `sync_vehiculo_to_ml(vehiculo_id)` - Sincronizar individual
   - `sync_all_pending()` - Sincronizar pendientes (cron)
   - `refresh_ml_tokens()` - Renovar tokens

### Endpoints API a Crear

| Metodo | URL | Descripcion |
|--------|-----|-------------|
| POST | `/api/vehiculos/{id}/publicar-ml/` | Publicar en ML |
| POST | `/api/vehiculos/{id}/pausar-ml/` | Pausar publicacion |
| POST | `/api/vehiculos/{id}/reactivar-ml/` | Reactivar publicacion |
| POST | `/api/vehiculos/{id}/finalizar-ml/` | Cerrar publicacion |
| POST | `/api/vehiculos/{id}/sync-ml/` | Forzar sincronizacion |
| GET | `/api/ml/estado/` | Estado de la cuenta ML |

---

## Proximos Pasos

1. **Integracion MercadoLibre** - Publicacion automatica de vehiculos
2. **Optimizacion de imagenes** - Thumbnails, compresion, CDN
3. **Panel de estadisticas** - Vehiculos vendidos, tiempos, precios
4. **Notificaciones** - Email/WhatsApp para leads de ML
