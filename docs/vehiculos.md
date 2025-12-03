# API Vehiculos

Documentacion de endpoints para la gestion de vehiculos del inventario.

## Base URL

```
http://localhost:8000/api/vehiculos/
```

## Autenticacion

Todos los endpoints requieren autenticacion JWT. Incluir el header:

```
Authorization: Bearer <access_token>
```

---

## Endpoints CRUD

### Listar vehiculos

```http
GET /api/vehiculos/
```

**Query Parameters - Filtros:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `marca` | integer | Filtrar por ID de marca |
| `modelo` | integer | Filtrar por ID de modelo |
| `combustible` | integer | Filtrar por ID de combustible |
| `caja` | integer | Filtrar por ID de caja |
| `estado` | integer | Filtrar por ID de estado |
| `condicion` | integer | Filtrar por ID de condicion |
| `moneda` | integer | Filtrar por ID de moneda |
| `segmento` | integer | Filtrar por segmento1 o segmento2 |
| `vendedor` | integer | Filtrar por ID de vendedor/dueno |
| `precio_min` | decimal | Precio minimo |
| `precio_max` | decimal | Precio maximo |
| `anio_min` | integer | Ano minimo |
| `anio_max` | integer | Ano maximo |
| `km_min` | integer | Kilometraje minimo |
| `km_max` | integer | Kilometraje maximo |
| `vendido` | boolean | Filtrar por estado vendido |
| `reservado` | boolean | Filtrar por estado reservado |
| `disponible` | boolean | Solo disponibles (no vendido, no reservado, no eliminado) |
| `mostrar_en_web` | boolean | Filtrar por visibilidad web |
| `destacar_en_web` | boolean | Filtrar por destacados |
| `oportunidad` | boolean | Filtrar oportunidades |
| `publicado_en_ml` | boolean | Filtrar por estado MercadoLibre |
| `vtv` | boolean | Filtrar por VTV vigente |
| `include_deleted` | boolean | Incluir vehiculos eliminados (soft delete) |
| `search` | string | Buscar en patente, marca, modelo, version, color |
| `ordering` | string | Ordenar por campo (`precio`, `-precio`, `anio`, `-created_at`) |

**Ejemplo:**

```bash
# Listar todos los disponibles
curl -X GET "http://localhost:8000/api/vehiculos/?disponible=true" \
  -H "Authorization: Bearer <token>"

# Filtrar por marca y rango de precio
curl -X GET "http://localhost:8000/api/vehiculos/?marca=1&precio_min=10000&precio_max=50000" \
  -H "Authorization: Bearer <token>"

# Buscar por texto
curl -X GET "http://localhost:8000/api/vehiculos/?search=ford+focus" \
  -H "Authorization: Bearer <token>"

# Ordenar por precio descendente
curl -X GET "http://localhost:8000/api/vehiculos/?ordering=-precio" \
  -H "Authorization: Bearer <token>"
```

**Respuesta (lista resumida):**

```json
[
  {
    "id": 1,
    "titulo": "Ford Focus 1.6 SE 2020",
    "patente": "AB123CD",
    "marca": 1,
    "marca_nombre": "Ford",
    "modelo": 5,
    "modelo_nombre": "Focus",
    "version": "1.6 SE",
    "anio": 2020,
    "km": 45000,
    "color": "Gris",
    "precio": "2500000.00",
    "moneda": 1,
    "moneda_nombre": "ARS",
    "estado": 2,
    "estado_nombre": "Usado",
    "vendedor_dueno": 1,
    "vendedor_nombre": "Juan Perez",
    "reservado": false,
    "vendido": false,
    "disponible": true,
    "mostrar_en_web": true,
    "destacar_en_web": false,
    "oportunidad": false,
    "publicado_en_ml": true,
    "ml_item_id": "MLA123456789",
    "imagen_principal": "http://localhost:8000/media/vehiculos/2024/01/foto1.jpg",
    "cant_imagenes": 5,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### Crear vehiculo

```http
POST /api/vehiculos/
```

**Body:**

```json
{
  "marca": 1,
  "modelo": 5,
  "segmento1": 2,
  "segmento2": null,
  "combustible": 1,
  "caja": 1,
  "estado": 2,
  "condicion": 1,
  "moneda": 1,
  "vendedor_dueno": 1,
  "version": "1.6 SE",
  "patente": "AB123CD",
  "anio": 2020,
  "km": 45000,
  "color": "Gris",
  "precio": "2500000.00",
  "porcentaje_financiacion": "15.00",
  "cant_duenos": 1,
  "vtv": true,
  "plan_ahorro": false,
  "reservado": false,
  "vendido": false,
  "mostrar_en_web": true,
  "destacar_en_web": false,
  "oportunidad": false,
  "oportunidad_grupo": false,
  "reventa": false,
  "publicado_en_ml": false,
  "comentario_carga": "Vehiculo en excelente estado"
}
```

**Campos requeridos:** `marca`, `modelo`, `combustible`, `caja`, `estado`, `condicion`, `moneda`, `vendedor_dueno`, `patente`, `anio`, `color`, `precio`

**Nota:** El campo `cargado_por` se asigna automaticamente al usuario autenticado.

**Ejemplo:**

```bash
curl -X POST http://localhost:8000/api/vehiculos/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "marca": 1,
    "modelo": 5,
    "combustible": 1,
    "caja": 1,
    "estado": 2,
    "condicion": 1,
    "moneda": 1,
    "vendedor_dueno": 1,
    "patente": "AB123CD",
    "anio": 2020,
    "km": 45000,
    "color": "Gris",
    "precio": "2500000.00"
  }'
```

**Respuesta (201 Created):** Objeto vehiculo completo (ver detalle).

---

### Obtener detalle

```http
GET /api/vehiculos/{id}/
```

**Ejemplo:**

```bash
curl -X GET http://localhost:8000/api/vehiculos/1/ \
  -H "Authorization: Bearer <token>"
```

**Respuesta:**

```json
{
  "id": 1,
  "titulo": "Ford Focus 1.6 SE 2020",
  "marca": 1,
  "modelo": 5,
  "segmento1": 2,
  "segmento2": null,
  "combustible": 1,
  "caja": 1,
  "estado": 2,
  "condicion": 1,
  "moneda": 1,
  "vendedor_dueno": 1,
  "cargado_por": 1,
  "marca_detail": {
    "id": 1,
    "nombre": "Ford",
    "activo": true,
    "orden": 1
  },
  "modelo_detail": {
    "id": 5,
    "nombre": "Focus",
    "marca": 1,
    "activo": true,
    "orden": 1
  },
  "segmento1_detail": {
    "id": 2,
    "nombre": "Sedan",
    "activo": true,
    "orden": 2
  },
  "segmento2_detail": null,
  "combustible_detail": {
    "id": 1,
    "nombre": "Nafta",
    "activo": true,
    "orden": 1
  },
  "caja_detail": {
    "id": 1,
    "nombre": "Manual",
    "activo": true,
    "orden": 1
  },
  "estado_detail": {
    "id": 2,
    "nombre": "Usado",
    "activo": true,
    "orden": 2
  },
  "condicion_detail": {
    "id": 1,
    "nombre": "Excelente",
    "activo": true,
    "orden": 1
  },
  "moneda_detail": {
    "id": 1,
    "nombre": "ARS",
    "activo": true,
    "orden": 1
  },
  "vendedor_detail": {
    "id": 1,
    "nombre": "Juan",
    "apellido": "Perez",
    "full_name": "Juan Perez",
    "email": "juan@email.com",
    "celular": "1122334455",
    "dni": "12345678",
    "tiene_cartel": true,
    "activo": true
  },
  "cargado_por_nombre": "Admin User",
  "version": "1.6 SE",
  "patente": "AB123CD",
  "anio": 2020,
  "km": 45000,
  "color": "Gris",
  "precio": "2500000.00",
  "precio_financiado": "2875000.00",
  "porcentaje_financiacion": "15.00",
  "cant_duenos": 1,
  "vtv": true,
  "plan_ahorro": false,
  "reservado": false,
  "vendido": false,
  "disponible": true,
  "mostrar_en_web": true,
  "destacar_en_web": false,
  "oportunidad": false,
  "oportunidad_grupo": false,
  "reventa": false,
  "publicado_en_ml": true,
  "ml_item_id": "MLA123456789",
  "ml_estado": "active",
  "ml_fecha_sync": "2024-01-15T12:00:00Z",
  "ml_error": "",
  "ml_permalink": "https://articulo.mercadolibre.com.ar/MLA-123456789",
  "comentario_carga": "Vehiculo en excelente estado",
  "imagenes": [
    {
      "id": 1,
      "imagen": "vehiculos/2024/01/foto1.jpg",
      "imagen_url": "http://localhost:8000/media/vehiculos/2024/01/foto1.jpg",
      "orden": 0,
      "es_principal": true,
      "created_at": "2024-01-15T10:35:00Z"
    },
    {
      "id": 2,
      "imagen": "vehiculos/2024/01/foto2.jpg",
      "imagen_url": "http://localhost:8000/media/vehiculos/2024/01/foto2.jpg",
      "orden": 1,
      "es_principal": false,
      "created_at": "2024-01-15T10:36:00Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T12:00:00Z",
  "deleted_at": null
}
```

---

### Actualizar vehiculo (completo)

```http
PUT /api/vehiculos/{id}/
```

Requiere enviar todos los campos editables.

---

### Actualizar vehiculo (parcial)

```http
PATCH /api/vehiculos/{id}/
```

Permite actualizar solo algunos campos.

**Ejemplo:**

```bash
# Actualizar precio
curl -X PATCH http://localhost:8000/api/vehiculos/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"precio": "2300000.00"}'

# Marcar como destacado
curl -X PATCH http://localhost:8000/api/vehiculos/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"destacar_en_web": true}'
```

---

### Eliminar vehiculo (soft delete)

```http
DELETE /api/vehiculos/{id}/
```

No elimina fisicamente, marca `deleted_at` con la fecha actual.

**Ejemplo:**

```bash
curl -X DELETE http://localhost:8000/api/vehiculos/1/ \
  -H "Authorization: Bearer <token>"
```

**Respuesta:** `204 No Content`

---

## Acciones Extra

### Subir imagen

```http
POST /api/vehiculos/{id}/imagenes/
```

**Content-Type:** `multipart/form-data`

**Campos:**
- `imagen` (file, requerido): Archivo de imagen
- `orden` (integer, opcional): Orden de visualizacion (default: 0)
- `es_principal` (boolean, opcional): Marcar como principal (default: false)

**Limite:** Maximo 15 imagenes por vehiculo.

**Ejemplo:**

```bash
curl -X POST http://localhost:8000/api/vehiculos/1/imagenes/ \
  -H "Authorization: Bearer <token>" \
  -F "imagen=@/path/to/foto.jpg" \
  -F "orden=0" \
  -F "es_principal=true"
```

**Respuesta (201 Created):**

```json
{
  "id": 3,
  "imagen": "vehiculos/2024/01/foto3.jpg",
  "imagen_url": "http://localhost:8000/media/vehiculos/2024/01/foto3.jpg",
  "orden": 0,
  "es_principal": true,
  "created_at": "2024-01-15T14:00:00Z"
}
```

---

### Eliminar imagen

```http
DELETE /api/vehiculos/{id}/imagenes/{imagen_id}/
```

**Ejemplo:**

```bash
curl -X DELETE http://localhost:8000/api/vehiculos/1/imagenes/3/ \
  -H "Authorization: Bearer <token>"
```

**Respuesta:** `204 No Content`

---

### Restaurar vehiculo eliminado

```http
POST /api/vehiculos/{id}/restaurar/
```

Restaura un vehiculo que fue eliminado (soft delete).

**Ejemplo:**

```bash
curl -X POST http://localhost:8000/api/vehiculos/1/restaurar/ \
  -H "Authorization: Bearer <token>"
```

**Respuesta:** Objeto vehiculo completo restaurado.

---

### Marcar como vendido

```http
PATCH /api/vehiculos/{id}/marcar-vendido/
```

Marca el vehiculo como vendido. Automaticamente:
- `vendido = true`
- `reservado = false`
- `mostrar_en_web = false`

**Ejemplo:**

```bash
curl -X PATCH http://localhost:8000/api/vehiculos/1/marcar-vendido/ \
  -H "Authorization: Bearer <token>"
```

**Respuesta:** Objeto vehiculo actualizado.

---

### Marcar/Desmarcar como reservado

```http
PATCH /api/vehiculos/{id}/marcar-reservado/
```

Toggle del estado reservado. Si esta reservado, lo desmarca; si no lo esta, lo reserva.

**Ejemplo:**

```bash
curl -X PATCH http://localhost:8000/api/vehiculos/1/marcar-reservado/ \
  -H "Authorization: Bearer <token>"
```

**Respuesta:** Objeto vehiculo actualizado.

---

## Errores Comunes

### 400 Bad Request

```json
{
  "patente": ["vehiculo with this patente already exists."],
  "modelo": ["El modelo \"Focus\" no pertenece a la marca \"Chevrolet\"."],
  "segmento2": ["El segmento secundario debe ser diferente al principal."],
  "error": "El vehiculo ya tiene el maximo de 15 imagenes."
}
```

### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found

```json
{
  "detail": "No encontrado."
}
```

```json
{
  "error": "Vehiculo no encontrado."
}
```

```json
{
  "error": "Imagen no encontrada."
}
```

---

## Integracion con Frontend

### Ejemplo con Fetch (JavaScript)

```javascript
const API_URL = 'http://localhost:8000/api';

const token = localStorage.getItem('access_token');

const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${token}`
};

// Listar vehiculos con filtros
async function getVehiculos(filters = {}) {
  const params = new URLSearchParams(filters);
  const response = await fetch(`${API_URL}/vehiculos/?${params}`, { headers });
  return response.json();
}

// Crear vehiculo
async function createVehiculo(data) {
  const response = await fetch(`${API_URL}/vehiculos/`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data)
  });
  return response.json();
}

// Obtener vehiculo por ID
async function getVehiculo(id) {
  const response = await fetch(`${API_URL}/vehiculos/${id}/`, { headers });
  return response.json();
}

// Actualizar vehiculo
async function updateVehiculo(id, data) {
  const response = await fetch(`${API_URL}/vehiculos/${id}/`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(data)
  });
  return response.json();
}

// Eliminar vehiculo (soft delete)
async function deleteVehiculo(id) {
  const response = await fetch(`${API_URL}/vehiculos/${id}/`, {
    method: 'DELETE',
    headers
  });
  return response.ok;
}

// Subir imagen (multipart/form-data)
async function uploadImagen(vehiculoId, file, orden = 0, esPrincipal = false) {
  const formData = new FormData();
  formData.append('imagen', file);
  formData.append('orden', orden);
  formData.append('es_principal', esPrincipal);

  const response = await fetch(`${API_URL}/vehiculos/${vehiculoId}/imagenes/`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  return response.json();
}

// Marcar como vendido
async function marcarVendido(id) {
  const response = await fetch(`${API_URL}/vehiculos/${id}/marcar-vendido/`, {
    method: 'PATCH',
    headers
  });
  return response.json();
}

// Restaurar vehiculo
async function restaurarVehiculo(id) {
  const response = await fetch(`${API_URL}/vehiculos/${id}/restaurar/`, {
    method: 'POST',
    headers
  });
  return response.json();
}
```

### Ejemplo con Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' }
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const vehiculosService = {
  // CRUD basico
  list: (params) => api.get('/vehiculos/', { params }),
  get: (id) => api.get(`/vehiculos/${id}/`),
  create: (data) => api.post('/vehiculos/', data),
  update: (id, data) => api.patch(`/vehiculos/${id}/`, data),
  delete: (id) => api.delete(`/vehiculos/${id}/`),

  // Imagenes
  uploadImagen: (id, formData) => api.post(`/vehiculos/${id}/imagenes/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  deleteImagen: (vehiculoId, imagenId) => api.delete(`/vehiculos/${vehiculoId}/imagenes/${imagenId}/`),

  // Acciones de estado
  marcarVendido: (id) => api.patch(`/vehiculos/${id}/marcar-vendido/`),
  marcarReservado: (id) => api.patch(`/vehiculos/${id}/marcar-reservado/`),
  restaurar: (id) => api.post(`/vehiculos/${id}/restaurar/`),
};

// Uso
const vehiculos = await vehiculosService.list({ disponible: true, marca: 1 });
const detalle = await vehiculosService.get(1);
```

### Ejemplo React Hooks

```javascript
import { useState, useEffect, useCallback } from 'react';
import { vehiculosService } from './api';

// Hook para listar vehiculos
function useVehiculos(filters = {}) {
  const [vehiculos, setVehiculos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchVehiculos = useCallback(async () => {
    try {
      setLoading(true);
      const { data } = await vehiculosService.list(filters);
      setVehiculos(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(filters)]);

  useEffect(() => {
    fetchVehiculos();
  }, [fetchVehiculos]);

  return { vehiculos, loading, error, refetch: fetchVehiculos };
}

// Hook para detalle de vehiculo
function useVehiculo(id) {
  const [vehiculo, setVehiculo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!id) return;
    const fetchVehiculo = async () => {
      try {
        setLoading(true);
        const { data } = await vehiculosService.get(id);
        setVehiculo(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchVehiculo();
  }, [id]);

  return { vehiculo, loading, error };
}

// Componente de ejemplo
function VehiculosList() {
  const { vehiculos, loading, error, refetch } = useVehiculos({
    disponible: true,
    ordering: '-created_at'
  });

  const handleVender = async (id) => {
    await vehiculosService.marcarVendido(id);
    refetch();
  };

  if (loading) return <p>Cargando...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      {vehiculos.map(v => (
        <div key={v.id}>
          <img src={v.imagen_principal} alt={v.titulo} />
          <h3>{v.titulo}</h3>
          <p>{v.moneda_nombre} {v.precio}</p>
          <p>{v.km} km - {v.anio}</p>
          <button onClick={() => handleVender(v.id)}>Marcar Vendido</button>
        </div>
      ))}
    </div>
  );
}
```

---

## Campos del Modelo Vehiculo

| Campo | Tipo | Requerido | Unico | Descripcion |
|-------|------|-----------|-------|-------------|
| `id` | integer | - | Si | ID autoincremental |
| `marca` | FK | Si | No | Referencia a Marca |
| `modelo` | FK | Si | No | Referencia a Modelo (debe pertenecer a la marca) |
| `segmento1` | FK | No | No | Segmento principal |
| `segmento2` | FK | No | No | Segmento secundario (diferente a segmento1) |
| `combustible` | FK | Si | No | Tipo de combustible |
| `caja` | FK | Si | No | Tipo de caja |
| `estado` | FK | Si | No | Estado del vehiculo (0km, Usado, etc.) |
| `condicion` | FK | Si | No | Condicion (Excelente, Buen estado, etc.) |
| `moneda` | FK | Si | No | Moneda del precio |
| `vendedor_dueno` | FK | Si | No | Vendedor/dueno del vehiculo |
| `cargado_por` | FK | Auto | No | Usuario que cargo el vehiculo |
| `version` | string(100) | No | No | Version del modelo (ej: "1.6 SE") |
| `patente` | string(10) | Si | Si | Patente unica |
| `anio` | integer | Si | No | Ano del vehiculo (1900-2100) |
| `km` | integer | No | No | Kilometraje (default: 0) |
| `color` | string(50) | Si | No | Color del vehiculo |
| `precio` | decimal(12,2) | Si | No | Precio de venta |
| `porcentaje_financiacion` | decimal(5,2) | No | No | Porcentaje adicional por financiacion |
| `cant_duenos` | integer | No | No | Cantidad de duenos anteriores (default: 1) |
| `vtv` | boolean | No | No | VTV vigente (default: false) |
| `plan_ahorro` | boolean | No | No | Es plan de ahorro (default: false) |
| `reservado` | boolean | No | No | Esta reservado (default: false) |
| `vendido` | boolean | No | No | Fue vendido (default: false) |
| `mostrar_en_web` | boolean | No | No | Mostrar en web publica (default: true) |
| `destacar_en_web` | boolean | No | No | Destacar en web (default: false) |
| `oportunidad` | boolean | No | No | Marcar como oportunidad (default: false) |
| `oportunidad_grupo` | boolean | No | No | Oportunidad de grupo (default: false) |
| `reventa` | boolean | No | No | Es vehiculo para reventa (default: false) |
| `publicado_en_ml` | boolean | No | No | Publicado en MercadoLibre (default: false) |
| `ml_item_id` | string(50) | No | Si | ID en MercadoLibre (MLA...) |
| `ml_estado` | string(20) | No | No | Estado en ML (active, paused, closed) |
| `ml_fecha_sync` | datetime | No | No | Ultima sincronizacion con ML |
| `ml_error` | text | No | No | Ultimo error de sincronizacion |
| `ml_permalink` | url(500) | No | No | Link directo a publicacion ML |
| `comentario_carga` | text | No | No | Notas internas |
| `created_at` | datetime | - | No | Fecha de creacion (auto) |
| `updated_at` | datetime | - | No | Fecha de actualizacion (auto) |
| `deleted_at` | datetime | - | No | Fecha de eliminacion (soft delete) |

## Campos Calculados (solo lectura)

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `titulo` | string | "Marca Modelo Version Anio" |
| `precio_financiado` | decimal | Precio + porcentaje de financiacion |
| `disponible` | boolean | true si no esta vendido, reservado ni eliminado |
| `imagen_principal` | url | URL de imagen principal o primera imagen |
| `cant_imagenes` | integer | Cantidad de imagenes del vehiculo |

---

## Campos de ImagenVehiculo

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `id` | integer | - | ID autoincremental |
| `vehiculo` | FK | Auto | Referencia al vehiculo |
| `imagen` | file | Si | Archivo de imagen |
| `imagen_url` | url | - | URL absoluta de la imagen (solo lectura) |
| `orden` | integer | No | Orden de visualizacion (default: 0) |
| `es_principal` | boolean | No | Imagen principal del vehiculo (default: false) |
| `created_at` | datetime | - | Fecha de subida (auto) |

**Nota:** Al marcar una imagen como `es_principal=true`, automaticamente se desmarca cualquier otra imagen principal del mismo vehiculo.
