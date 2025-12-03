# API Vendedores

Documentacion de endpoints para la gestion de vendedores (duenos de vehiculos).

## Base URL

```
http://localhost:8000/api/vendedores/
```

## Autenticacion

Todos los endpoints requieren autenticacion JWT. Incluir el header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Listar vendedores

```http
GET /api/vendedores/
```

**Query Parameters:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `activo` | boolean | Filtrar por estado activo (`true`/`false`) |
| `tiene_cartel` | boolean | Filtrar por tiene cartel (`true`/`false`) |
| `search` | string | Buscar en nombre, apellido, dni, email |
| `ordering` | string | Ordenar por campo (`nombre`, `-nombre`, `apellido`, `-created_at`) |

**Ejemplo:**

```bash
# Listar todos
curl -X GET http://localhost:8000/api/vendedores/ \
  -H "Authorization: Bearer <token>"

# Filtrar activos con cartel
curl -X GET "http://localhost:8000/api/vendedores/?activo=true&tiene_cartel=true" \
  -H "Authorization: Bearer <token>"

# Buscar por nombre
curl -X GET "http://localhost:8000/api/vendedores/?search=juan" \
  -H "Authorization: Bearer <token>"

# Ordenar por nombre
curl -X GET "http://localhost:8000/api/vendedores/?ordering=nombre" \
  -H "Authorization: Bearer <token>"
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "nombre": "Juan",
    "apellido": "Perez",
    "full_name": "Juan Perez",
    "email": "juan@email.com",
    "celular": "1122334455",
    "dni": "12345678",
    "tiene_cartel": true,
    "activo": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### Crear vendedor

```http
POST /api/vendedores/
```

**Body:**

```json
{
  "nombre": "Juan",
  "apellido": "Perez",
  "email": "juan@email.com",
  "direccion": "Av. Corrientes 1234, CABA",
  "celular": "1122334455",
  "dni": "12345678",
  "tiene_cartel": false,
  "activo": true,
  "comentarios": "Cliente referido por Maria"
}
```

**Campos requeridos:** `nombre`, `apellido`, `email`, `direccion`, `celular`, `dni`

**Campos opcionales:** `tiene_cartel` (default: false), `activo` (default: true), `comentarios`

**Ejemplo:**

```bash
curl -X POST http://localhost:8000/api/vendedores/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan",
    "apellido": "Perez",
    "email": "juan@email.com",
    "direccion": "Av. Corrientes 1234, CABA",
    "celular": "1122334455",
    "dni": "12345678"
  }'
```

**Respuesta (201 Created):**

```json
{
  "id": 1,
  "nombre": "Juan",
  "apellido": "Perez",
  "full_name": "Juan Perez",
  "email": "juan@email.com",
  "direccion": "Av. Corrientes 1234, CABA",
  "celular": "1122334455",
  "dni": "12345678",
  "tiene_cartel": false,
  "activo": true,
  "comentarios": "",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### Obtener vendedor

```http
GET /api/vendedores/{id}/
```

**Ejemplo:**

```bash
curl -X GET http://localhost:8000/api/vendedores/1/ \
  -H "Authorization: Bearer <token>"
```

**Respuesta:**

```json
{
  "id": 1,
  "nombre": "Juan",
  "apellido": "Perez",
  "full_name": "Juan Perez",
  "email": "juan@email.com",
  "direccion": "Av. Corrientes 1234, CABA",
  "celular": "1122334455",
  "dni": "12345678",
  "tiene_cartel": false,
  "activo": true,
  "comentarios": "",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### Actualizar vendedor (completo)

```http
PUT /api/vendedores/{id}/
```

Requiere enviar todos los campos.

**Ejemplo:**

```bash
curl -X PUT http://localhost:8000/api/vendedores/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Carlos",
    "apellido": "Perez",
    "email": "juancarlos@email.com",
    "direccion": "Av. Santa Fe 5678, CABA",
    "celular": "1199887766",
    "dni": "12345678",
    "tiene_cartel": true,
    "activo": true,
    "comentarios": "Actualizado"
  }'
```

---

### Actualizar vendedor (parcial)

```http
PATCH /api/vendedores/{id}/
```

Permite actualizar solo algunos campos.

**Ejemplo:**

```bash
# Actualizar solo el celular
curl -X PATCH http://localhost:8000/api/vendedores/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"celular": "1199887766"}'

# Marcar como inactivo
curl -X PATCH http://localhost:8000/api/vendedores/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"activo": false}'

# Actualizar tiene_cartel
curl -X PATCH http://localhost:8000/api/vendedores/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"tiene_cartel": true}'
```

---

### Eliminar vendedor

```http
DELETE /api/vendedores/{id}/
```

Elimina el vendedor de la base de datos (hard delete).

**Ejemplo:**

```bash
curl -X DELETE http://localhost:8000/api/vendedores/1/ \
  -H "Authorization: Bearer <token>"
```

**Respuesta:** `204 No Content`

---

## Errores Comunes

### 400 Bad Request

```json
{
  "email": ["vendedor with this email already exists."],
  "dni": ["vendedor with this DNI already exists."]
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

---

## Integracion con Frontend

### Ejemplo con Fetch (JavaScript)

```javascript
const API_URL = 'http://localhost:8000/api';

// Obtener token del storage
const token = localStorage.getItem('access_token');

// Headers comunes
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${token}`
};

// Listar vendedores
async function getVendedores(filters = {}) {
  const params = new URLSearchParams(filters);
  const response = await fetch(`${API_URL}/vendedores/?${params}`, { headers });
  return response.json();
}

// Crear vendedor
async function createVendedor(data) {
  const response = await fetch(`${API_URL}/vendedores/`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data)
  });
  return response.json();
}

// Obtener vendedor por ID
async function getVendedor(id) {
  const response = await fetch(`${API_URL}/vendedores/${id}/`, { headers });
  return response.json();
}

// Actualizar vendedor
async function updateVendedor(id, data) {
  const response = await fetch(`${API_URL}/vendedores/${id}/`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(data)
  });
  return response.json();
}

// Eliminar vendedor
async function deleteVendedor(id) {
  const response = await fetch(`${API_URL}/vendedores/${id}/`, {
    method: 'DELETE',
    headers
  });
  return response.ok;
}
```

### Ejemplo con Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para agregar token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Servicios
export const vendedoresService = {
  // Listar con filtros opcionales
  list: (params) => api.get('/vendedores/', { params }),

  // Obtener por ID
  get: (id) => api.get(`/vendedores/${id}/`),

  // Crear
  create: (data) => api.post('/vendedores/', data),

  // Actualizar parcial
  update: (id, data) => api.patch(`/vendedores/${id}/`, data),

  // Eliminar
  delete: (id) => api.delete(`/vendedores/${id}/`)
};

// Uso
const vendedores = await vendedoresService.list({ activo: true });
const vendedor = await vendedoresService.create({ nombre: 'Juan', ... });
```

### Ejemplo React Hook

```javascript
import { useState, useEffect } from 'react';
import { vendedoresService } from './api';

function useVendedores(filters = {}) {
  const [vendedores, setVendedores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchVendedores = async () => {
      try {
        setLoading(true);
        const { data } = await vendedoresService.list(filters);
        setVendedores(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchVendedores();
  }, [JSON.stringify(filters)]);

  return { vendedores, loading, error };
}

// Uso en componente
function VendedoresList() {
  const { vendedores, loading, error } = useVendedores({ activo: true });

  if (loading) return <p>Cargando...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <ul>
      {vendedores.map(v => (
        <li key={v.id}>{v.full_name} - {v.dni}</li>
      ))}
    </ul>
  );
}
```

---

## Campos del Modelo

| Campo | Tipo | Requerido | Unico | Descripcion |
|-------|------|-----------|-------|-------------|
| `id` | integer | - | Si | ID autoincremental |
| `nombre` | string(100) | Si | No | Nombre del vendedor |
| `apellido` | string(100) | Si | No | Apellido del vendedor |
| `email` | email | Si | Si | Email de contacto |
| `direccion` | string(255) | Si | No | Direccion completa |
| `celular` | string(20) | Si | No | Numero de celular |
| `dni` | string(20) | Si | Si | Documento de identidad |
| `tiene_cartel` | boolean | No | No | Si tiene cartel de venta |
| `activo` | boolean | No | No | Si esta activo en el sistema |
| `comentarios` | text | No | No | Notas adicionales |
| `created_at` | datetime | - | No | Fecha de creacion (auto) |
| `updated_at` | datetime | - | No | Fecha de actualizacion (auto) |
