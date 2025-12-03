# API Parametros

Documentacion de endpoints para los catalogos/parametros del sistema (marcas, modelos, combustibles, etc).

## Base URL

```
http://localhost:8000/api/parametros/
```

## Autenticacion

Todos los endpoints requieren autenticacion JWT. Incluir el header:

```
Authorization: Bearer <access_token>
```

## Endpoints Disponibles

| Recurso | URL | Descripcion |
|---------|-----|-------------|
| Cajas | `/api/parametros/cajas/` | Tipos de caja (Automatica, Manual) |
| Combustibles | `/api/parametros/combustibles/` | Tipos de combustible |
| Condiciones | `/api/parametros/condiciones/` | Condicion del vehiculo |
| Estados | `/api/parametros/estados/` | Estado comercial (0Km, Usado) |
| IVAs | `/api/parametros/ivas/` | Condicion ante IVA |
| Localidades | `/api/parametros/localidades/` | Ciudades/localidades |
| Marcas | `/api/parametros/marcas/` | Marcas de vehiculos |
| Modelos | `/api/parametros/modelos/` | Modelos de vehiculos |
| Monedas | `/api/parametros/monedas/` | Tipos de moneda |
| Segmentos | `/api/parametros/segmentos/` | Segmentos de vehiculos |

---

## Operaciones CRUD

Todos los parametros soportan las mismas operaciones:

### Listar

```http
GET /api/parametros/{recurso}/
```

**Query Parameters:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `activo` | boolean | Filtrar por estado activo |
| `search` | string | Buscar por nombre |
| `ordering` | string | Ordenar (`nombre`, `-nombre`, `orden`, `-created_at`) |

**Ejemplo:**

```bash
# Listar todas las marcas activas
curl -X GET "http://localhost:8000/api/parametros/marcas/?activo=true" \
  -H "Authorization: Bearer <token>"

# Buscar marcas
curl -X GET "http://localhost:8000/api/parametros/marcas/?search=ford" \
  -H "Authorization: Bearer <token>"
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "nombre": "Ford",
    "activo": true,
    "orden": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### Crear

```http
POST /api/parametros/{recurso}/
```

**Body:**

```json
{
  "nombre": "Nuevo Valor",
  "activo": true,
  "orden": 0
}
```

**Campos:**

| Campo | Tipo | Requerido | Default | Descripcion |
|-------|------|-----------|---------|-------------|
| `nombre` | string | Si | - | Nombre del parametro |
| `activo` | boolean | No | true | Estado activo |
| `orden` | integer | No | 0 | Orden de visualizacion |

**Ejemplo:**

```bash
curl -X POST http://localhost:8000/api/parametros/localidades/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Cordoba", "orden": 5}'
```

---

### Obtener detalle

```http
GET /api/parametros/{recurso}/{id}/
```

**Ejemplo:**

```bash
curl -X GET http://localhost:8000/api/parametros/marcas/1/ \
  -H "Authorization: Bearer <token>"
```

**Respuesta (Marca con modelos anidados):**

```json
{
  "id": 1,
  "nombre": "Ford",
  "activo": true,
  "orden": 1,
  "modelos": [
    {"id": 1, "nombre": "Focus", "activo": true, "orden": 0},
    {"id": 2, "nombre": "Fiesta", "activo": true, "orden": 0}
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### Actualizar

```http
PUT /api/parametros/{recurso}/{id}/
PATCH /api/parametros/{recurso}/{id}/
```

**Ejemplo:**

```bash
# Actualizar parcial
curl -X PATCH http://localhost:8000/api/parametros/cajas/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"orden": 2}'

# Desactivar
curl -X PATCH http://localhost:8000/api/parametros/marcas/5/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"activo": false}'
```

---

### Eliminar

```http
DELETE /api/parametros/{recurso}/{id}/
```

**Ejemplo:**

```bash
curl -X DELETE http://localhost:8000/api/parametros/localidades/10/ \
  -H "Authorization: Bearer <token>"
```

**Respuesta:** `204 No Content`

---

## Modelos (Caso Especial)

Los modelos tienen una relacion con marcas:

### Listar modelos

```http
GET /api/parametros/modelos/
```

**Query Parameters adicionales:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `marca` | integer | Filtrar por ID de marca |

**Ejemplo:**

```bash
# Listar modelos de Ford (id=1)
curl -X GET "http://localhost:8000/api/parametros/modelos/?marca=1" \
  -H "Authorization: Bearer <token>"
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "nombre": "Focus",
    "marca": 1,
    "marca_nombre": "Ford",
    "activo": true,
    "orden": 0,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### Crear modelo

```http
POST /api/parametros/modelos/
```

**Body:**

```json
{
  "nombre": "Mustang",
  "marca": 1,
  "activo": true,
  "orden": 0
}
```

---

## Valores Cargados

### Cajas (2)
- Automatica
- Manual

### Combustibles (5)
- Diesel
- Electrico
- GNC
- HIBRIDO
- Nafta

### Condiciones (6)
- Buen estado
- CON DETALLES
- Con detalles de chapa
- CON DETALLES DE GRANIZO
- Excelente estado
- Muy buen estado

### Estados (3)
- 0Km
- NUEVO
- Usado

### IVAs (5)
- Consumidor Final
- Exento
- Inscripto
- No Inscripto
- Resp. Monotributo

### Localidades (8)
- A Determinar
- Capital Federal
- Mar del Plata
- Olavarria
- San Fernando
- Tandil
- Ushuaia
- Zarate

### Monedas (4)
- ARS
- USD
- EUROS
- YENS

### Segmentos (43)
- SUV, Sedan 4p, Pick up doble cabina, Camioneta, 4x4, etc.

### Marcas (~130)
- Ford, Chevrolet, Toyota, Volkswagen, Fiat, Renault, etc.

### Modelos (~440)
- Relacionados a cada marca

---

## Comando de Carga

Para cargar/recargar los parametros iniciales:

```bash
# Solo parametros fijos (sin CSV)
docker-compose exec backend python manage.py cargar_parametros

# Con modelos desde CSV
docker-compose exec backend python manage.py cargar_parametros --csv /app/automan.csv
```

---

## Integracion con Frontend

### Ejemplo con Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Interceptor para token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Servicios de parametros
export const parametrosService = {
  // Generico para cualquier parametro
  list: (tipo, params = {}) => api.get(`/parametros/${tipo}/`, { params }),
  get: (tipo, id) => api.get(`/parametros/${tipo}/${id}/`),
  create: (tipo, data) => api.post(`/parametros/${tipo}/`, data),
  update: (tipo, id, data) => api.patch(`/parametros/${tipo}/${id}/`, data),
  delete: (tipo, id) => api.delete(`/parametros/${tipo}/${id}/`),

  // Helpers especificos
  getMarcas: (params) => api.get('/parametros/marcas/', { params }),
  getModelos: (marcaId) => api.get('/parametros/modelos/', { params: { marca: marcaId } }),
  getCombustibles: () => api.get('/parametros/combustibles/'),
  getEstados: () => api.get('/parametros/estados/'),
};

// Uso
const marcas = await parametrosService.getMarcas({ activo: true });
const modelos = await parametrosService.getModelos(1); // Modelos de Ford
```

### Ejemplo React - Select de Marca/Modelo

```javascript
import { useState, useEffect } from 'react';
import { parametrosService } from './api';

function MarcaModeloSelect({ onSelect }) {
  const [marcas, setMarcas] = useState([]);
  const [modelos, setModelos] = useState([]);
  const [marcaId, setMarcaId] = useState('');
  const [modeloId, setModeloId] = useState('');

  // Cargar marcas al montar
  useEffect(() => {
    parametrosService.getMarcas({ activo: true })
      .then(res => setMarcas(res.data));
  }, []);

  // Cargar modelos cuando cambia la marca
  useEffect(() => {
    if (marcaId) {
      parametrosService.getModelos(marcaId)
        .then(res => setModelos(res.data));
    } else {
      setModelos([]);
    }
    setModeloId('');
  }, [marcaId]);

  return (
    <div>
      <select value={marcaId} onChange={e => setMarcaId(e.target.value)}>
        <option value="">Seleccionar marca</option>
        {marcas.map(m => (
          <option key={m.id} value={m.id}>{m.nombre}</option>
        ))}
      </select>

      <select
        value={modeloId}
        onChange={e => {
          setModeloId(e.target.value);
          onSelect({ marca: marcaId, modelo: e.target.value });
        }}
        disabled={!marcaId}
      >
        <option value="">Seleccionar modelo</option>
        {modelos.map(m => (
          <option key={m.id} value={m.id}>{m.nombre}</option>
        ))}
      </select>
    </div>
  );
}
```

---

## Errores Comunes

### 400 Bad Request

```json
{
  "nombre": ["Este campo es requerido."]
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
