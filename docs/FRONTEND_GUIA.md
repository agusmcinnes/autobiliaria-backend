# Guía para el Desarrollo Frontend - Autobiliaria

## Información General del Proyecto

Autobiliaria es un sistema de gestión para una automotora/concesionaria de vehículos. El backend está desarrollado en Django REST Framework y desplegado en un VPS.

---

## Entornos Disponibles

| Entorno | API URL | Uso |
|---------|---------|-----|
| **Desarrollo** | `https://api-dev.autobiliaria.cloud` | Para desarrollar y probar |
| **Producción** | `https://api.autobiliaria.cloud` | Web pública final |

**Importante:** Siempre desarrollá y probá primero en el entorno de desarrollo.

---

## Estructura del Sistema

El sistema tiene dos partes principales:

### 1. Web Pública (para clientes)
- Listado de vehículos disponibles
- Filtros de búsqueda (marca, modelo, precio, año, etc.)
- Detalle de cada vehículo con galería de imágenes
- Formulario de contacto (opcional)

### 2. Panel de Administración (para el equipo interno)
- Login con JWT
- CRUD de vehículos
- CRUD de vendedores
- Gestión de parámetros (marcas, modelos, etc.)
- Marcar vehículos como vendidos/reservados

---

## Autenticación (JWT)

### Endpoints de Auth

| Método | Endpoint | Descripción | Auth requerida |
|--------|----------|-------------|----------------|
| POST | `/api/auth/login/` | Iniciar sesión | No |
| POST | `/api/auth/refresh/` | Renovar token | No |
| POST | `/api/auth/logout/` | Cerrar sesión | Sí |
| GET | `/api/auth/me/` | Obtener usuario actual | Sí |

### Login

```javascript
// POST https://api-dev.autobiliaria.cloud/api/auth/login/
const response = await fetch('https://api-dev.autobiliaria.cloud/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'admin@admin.com',
    password: 'admin'
  })
});

const data = await response.json();
// {
//   "access": "eyJ0eXAiOiJKV1...",   <- Token de acceso (válido 15 min)
//   "refresh": "eyJ0eXAiOiJKV1..."   <- Token de refresh (válido 1 día)
// }

// Guardar tokens
localStorage.setItem('access_token', data.access);
localStorage.setItem('refresh_token', data.refresh);
```

### Usar Token en Requests

```javascript
const token = localStorage.getItem('access_token');

const response = await fetch('https://api-dev.autobiliaria.cloud/api/vendedores/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### Renovar Token (cuando expire)

```javascript
// El access token expira en 15 minutos
// Cuando recibas un 401, renovar con el refresh token:

const response = await fetch('https://api-dev.autobiliaria.cloud/api/auth/refresh/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    refresh: localStorage.getItem('refresh_token')
  })
});

const data = await response.json();
localStorage.setItem('access_token', data.access);
```

### Logout

```javascript
await fetch('https://api-dev.autobiliaria.cloud/api/auth/logout/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    refresh: localStorage.getItem('refresh_token')
  })
});

localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');
```

### Usuario de prueba (DEV)

```
Email: admin@admin.com
Password: admin
```

---

## Endpoints Públicos (sin autenticación)

Estos endpoints son accesibles sin login, para la web pública:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/` | Info de la API |
| GET | `/api/vehiculos/` | Listar vehículos |
| GET | `/api/vehiculos/{id}/` | Detalle de vehículo |
| GET | `/api/parametros/marcas/` | Listar marcas |
| GET | `/api/parametros/marcas/{id}/` | Detalle de marca (con modelos) |
| GET | `/api/parametros/modelos/` | Listar modelos |
| GET | `/api/parametros/modelos/?marca={id}` | Modelos filtrados por marca |
| GET | `/api/parametros/cajas/` | Listar cajas (Manual/Automática) |
| GET | `/api/parametros/combustibles/` | Listar combustibles |
| GET | `/api/parametros/segmentos/` | Listar segmentos |

---

## API de Vehículos

### Listar Vehículos (PÚBLICO)

```javascript
// GET https://api-dev.autobiliaria.cloud/api/vehiculos/

// Sin filtros - todos los vehículos
const response = await fetch('https://api-dev.autobiliaria.cloud/api/vehiculos/');
const data = await response.json();

// Respuesta paginada:
// {
//   "count": 50,
//   "next": "https://api-dev.autobiliaria.cloud/api/vehiculos/?page=2",
//   "previous": null,
//   "results": [...]
// }
```

### Filtros Disponibles

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `marca` | int | ID de marca |
| `modelo` | int | ID de modelo |
| `combustible` | int | ID de combustible |
| `caja` | int | ID de caja (1=Manual, 2=Automática) |
| `estado` | int | ID de estado (0Km, Usado) |
| `condicion` | int | ID de condición |
| `segmento` | int | ID de segmento |
| `precio_min` | decimal | Precio mínimo |
| `precio_max` | decimal | Precio máximo |
| `anio_min` | int | Año mínimo |
| `anio_max` | int | Año máximo |
| `km_min` | int | Kilometraje mínimo |
| `km_max` | int | Kilometraje máximo |
| `disponible` | bool | Solo disponibles (no vendido/reservado) |
| `mostrar_en_web` | bool | Visible en web |
| `destacar_en_web` | bool | Destacados |
| `oportunidad` | bool | Oportunidades |
| `search` | string | Buscar en patente, marca, modelo |
| `ordering` | string | Ordenar: `precio`, `-precio`, `anio`, `-created_at` |

### Ejemplos de Filtros

```javascript
// Vehículos disponibles para mostrar en web
/api/vehiculos/?disponible=true&mostrar_en_web=true

// Filtrar por marca y rango de precio
/api/vehiculos/?marca=1&precio_min=10000&precio_max=50000

// Buscar "Ford Focus"
/api/vehiculos/?search=ford+focus

// Ordenar por precio de menor a mayor
/api/vehiculos/?ordering=precio

// Ordenar por más recientes
/api/vehiculos/?ordering=-created_at

// Vehículos destacados
/api/vehiculos/?destacar_en_web=true

// SUVs (segmento 1) de 2020 en adelante
/api/vehiculos/?segmento=1&anio_min=2020

// Combinar múltiples filtros
/api/vehiculos/?marca=1&combustible=1&caja=2&precio_max=5000000&ordering=-anio
```

### Respuesta del Listado

```json
{
  "count": 25,
  "next": "https://api-dev.autobiliaria.cloud/api/vehiculos/?page=2",
  "previous": null,
  "results": [
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
      "combustible_nombre": "Nafta",
      "caja_nombre": "Manual",
      "reservado": false,
      "vendido": false,
      "disponible": true,
      "mostrar_en_web": true,
      "destacar_en_web": false,
      "oportunidad": false,
      "imagen_principal": "https://api-dev.autobiliaria.cloud/media/vehiculos/2024/01/foto1.jpg",
      "cant_imagenes": 5,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Detalle de Vehículo (PÚBLICO)

```javascript
// GET https://api-dev.autobiliaria.cloud/api/vehiculos/1/

const response = await fetch('https://api-dev.autobiliaria.cloud/api/vehiculos/1/');
const vehiculo = await response.json();
```

**Respuesta completa:**

```json
{
  "id": 1,
  "titulo": "Ford Focus 1.6 SE 2020",
  "patente": "AB123CD",
  "marca": 1,
  "modelo": 5,
  "marca_detail": {
    "id": 1,
    "nombre": "Ford"
  },
  "modelo_detail": {
    "id": 5,
    "nombre": "Focus"
  },
  "segmento1_detail": {
    "id": 2,
    "nombre": "Sedan"
  },
  "combustible_detail": {
    "id": 1,
    "nombre": "Nafta"
  },
  "caja_detail": {
    "id": 1,
    "nombre": "Manual"
  },
  "estado_detail": {
    "id": 2,
    "nombre": "Usado"
  },
  "condicion_detail": {
    "id": 1,
    "nombre": "Excelente"
  },
  "moneda_detail": {
    "id": 1,
    "nombre": "ARS"
  },
  "version": "1.6 SE",
  "anio": 2020,
  "km": 45000,
  "color": "Gris",
  "precio": "2500000.00",
  "precio_financiado": "2875000.00",
  "porcentaje_financiacion": "15.00",
  "cant_duenos": 1,
  "vtv": true,
  "reservado": false,
  "vendido": false,
  "disponible": true,
  "comentario_carga": "Vehículo en excelente estado",
  "imagenes": [
    {
      "id": 1,
      "imagen_url": "https://api-dev.autobiliaria.cloud/media/vehiculos/2024/01/foto1.jpg",
      "orden": 0,
      "es_principal": true
    },
    {
      "id": 2,
      "imagen_url": "https://api-dev.autobiliaria.cloud/media/vehiculos/2024/01/foto2.jpg",
      "orden": 1,
      "es_principal": false
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Crear Vehículo (requiere auth)

```javascript
// POST https://api-dev.autobiliaria.cloud/api/vehiculos/

const response = await fetch('https://api-dev.autobiliaria.cloud/api/vehiculos/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    marca: 1,              // ID de marca (requerido)
    modelo: 5,             // ID de modelo (requerido)
    combustible: 1,        // ID de combustible (requerido)
    caja: 1,               // ID de caja (requerido)
    estado: 2,             // ID de estado (requerido)
    condicion: 1,          // ID de condición (requerido)
    moneda: 1,             // ID de moneda (requerido)
    vendedor_dueno: 1,     // ID de vendedor (requerido)
    patente: "AB123CD",    // Patente única (requerido)
    anio: 2020,            // Año (requerido)
    color: "Gris",         // Color (requerido)
    precio: "2500000.00",  // Precio (requerido)
    version: "1.6 SE",     // Versión (opcional)
    km: 45000,             // Kilometraje (opcional, default 0)
    cant_duenos: 1,        // Cantidad de dueños (opcional)
    vtv: true,             // VTV vigente (opcional)
    mostrar_en_web: true,  // Mostrar en web (opcional)
    destacar_en_web: false // Destacar (opcional)
  })
});
```

### Actualizar Vehículo (requiere auth)

```javascript
// PATCH https://api-dev.autobiliaria.cloud/api/vehiculos/1/

await fetch('https://api-dev.autobiliaria.cloud/api/vehiculos/1/', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    precio: "2300000.00",
    destacar_en_web: true
  })
});
```

### Subir Imagen (requiere auth)

```javascript
// POST https://api-dev.autobiliaria.cloud/api/vehiculos/1/imagenes/

const formData = new FormData();
formData.append('imagen', fileInput.files[0]);
formData.append('orden', 0);
formData.append('es_principal', true);

await fetch('https://api-dev.autobiliaria.cloud/api/vehiculos/1/imagenes/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
    // NO incluir Content-Type, FormData lo maneja
  },
  body: formData
});
```

### Eliminar Imagen (requiere auth)

```javascript
// DELETE https://api-dev.autobiliaria.cloud/api/vehiculos/1/imagenes/3/

await fetch('https://api-dev.autobiliaria.cloud/api/vehiculos/1/imagenes/3/', {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${token}` }
});
```

### Marcar como Vendido (requiere auth)

```javascript
// PATCH https://api-dev.autobiliaria.cloud/api/vehiculos/1/marcar-vendido/

await fetch('https://api-dev.autobiliaria.cloud/api/vehiculos/1/marcar-vendido/', {
  method: 'PATCH',
  headers: { 'Authorization': `Bearer ${token}` }
});

// Automáticamente pone: vendido=true, reservado=false, mostrar_en_web=false
```

### Marcar/Desmarcar Reservado (requiere auth)

```javascript
// PATCH https://api-dev.autobiliaria.cloud/api/vehiculos/1/marcar-reservado/

await fetch('https://api-dev.autobiliaria.cloud/api/vehiculos/1/marcar-reservado/', {
  method: 'PATCH',
  headers: { 'Authorization': `Bearer ${token}` }
});

// Toggle: si está reservado lo desmarca, si no lo está lo reserva
```

### Eliminar Vehículo (soft delete, requiere auth)

```javascript
// DELETE https://api-dev.autobiliaria.cloud/api/vehiculos/1/

await fetch('https://api-dev.autobiliaria.cloud/api/vehiculos/1/', {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${token}` }
});

// No elimina físicamente, marca deleted_at
```

### Restaurar Vehículo Eliminado (requiere auth)

```javascript
// POST https://api-dev.autobiliaria.cloud/api/vehiculos/1/restaurar/

await fetch('https://api-dev.autobiliaria.cloud/api/vehiculos/1/restaurar/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});
```

---

## API de Parámetros

Los parámetros son los catálogos del sistema (marcas, modelos, combustibles, etc.).

### Endpoints de Parámetros

**Marcas y Modelos son públicos** (para los filtros de la web). El resto requiere autenticación.

| Recurso | Endpoint |
|---------|----------|
| Marcas | `/api/parametros/marcas/` |
| Modelos | `/api/parametros/modelos/` |
| Combustibles | `/api/parametros/combustibles/` |
| Cajas | `/api/parametros/cajas/` |
| Estados | `/api/parametros/estados/` |
| Condiciones | `/api/parametros/condiciones/` |
| Monedas | `/api/parametros/monedas/` |
| Segmentos | `/api/parametros/segmentos/` |
| IVAs | `/api/parametros/ivas/` |
| Localidades | `/api/parametros/localidades/` |

### Listar Marcas

```javascript
const response = await fetch('https://api-dev.autobiliaria.cloud/api/parametros/marcas/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Respuesta:
// [
//   { "id": 1, "nombre": "Ford", "activo": true },
//   { "id": 2, "nombre": "Chevrolet", "activo": true },
//   ...
// ]
```

### Filtrar Modelos por Marca

```javascript
// Obtener modelos de Ford (id=1)
const response = await fetch('https://api-dev.autobiliaria.cloud/api/parametros/modelos/?marca=1', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Respuesta:
// [
//   { "id": 5, "nombre": "Focus", "marca": 1, "marca_nombre": "Ford" },
//   { "id": 6, "nombre": "Fiesta", "marca": 1, "marca_nombre": "Ford" },
//   ...
// ]
```

---

## API de Vendedores

Los vendedores son los dueños de los vehículos (no son usuarios del sistema).

### Listar Vendedores (requiere auth)

```javascript
const response = await fetch('https://api-dev.autobiliaria.cloud/api/vendedores/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Filtros disponibles:
// ?activo=true
// ?tiene_cartel=true
// ?search=juan
```

### Crear Vendedor (requiere auth)

```javascript
await fetch('https://api-dev.autobiliaria.cloud/api/vendedores/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    nombre: "Juan",
    apellido: "Pérez",
    email: "juan@email.com",
    direccion: "Av. Corrientes 1234, CABA",
    celular: "1122334455",
    dni: "12345678",
    tiene_cartel: false,
    comentarios: "Cliente nuevo"
  })
});
```

---

## Estructura Recomendada para el Frontend

### Web Pública

```
/                       → Home con vehículos destacados
/vehiculos              → Listado con filtros
/vehiculos/[id]         → Detalle del vehículo
/contacto               → Formulario de contacto (opcional)
```

### Panel de Administración

```
/admin/login            → Login
/admin/dashboard        → Resumen (cantidad de vehículos, vendidos, etc.)
/admin/vehiculos        → Listado de vehículos (con filtros)
/admin/vehiculos/nuevo  → Crear vehículo
/admin/vehiculos/[id]   → Editar vehículo
/admin/vendedores       → Listado de vendedores
/admin/vendedores/nuevo → Crear vendedor
/admin/parametros       → Gestión de parámetros (opcional)
```

---

## Ejemplo Completo: Servicio de API con Axios

```javascript
// services/api.js
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api-dev.autobiliaria.cloud';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' }
});

// Interceptor para agregar token automáticamente
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para renovar token cuando expire
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_URL}/api/auth/refresh/`, {
          refresh: refreshToken
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh token expiró, redirigir a login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/admin/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Servicios de Auth
export const authService = {
  login: (email, password) => api.post('/api/auth/login/', { email, password }),
  logout: (refresh) => api.post('/api/auth/logout/', { refresh }),
  refresh: (refresh) => api.post('/api/auth/refresh/', { refresh }),
  me: () => api.get('/api/auth/me/')
};

// Servicios de Vehículos
export const vehiculosService = {
  list: (params) => api.get('/api/vehiculos/', { params }),
  get: (id) => api.get(`/api/vehiculos/${id}/`),
  create: (data) => api.post('/api/vehiculos/', data),
  update: (id, data) => api.patch(`/api/vehiculos/${id}/`, data),
  delete: (id) => api.delete(`/api/vehiculos/${id}/`),

  // Imágenes
  uploadImage: (id, formData) => api.post(`/api/vehiculos/${id}/imagenes/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  deleteImage: (vehiculoId, imagenId) => api.delete(`/api/vehiculos/${vehiculoId}/imagenes/${imagenId}/`),

  // Acciones
  marcarVendido: (id) => api.patch(`/api/vehiculos/${id}/marcar-vendido/`),
  marcarReservado: (id) => api.patch(`/api/vehiculos/${id}/marcar-reservado/`),
  restaurar: (id) => api.post(`/api/vehiculos/${id}/restaurar/`)
};

// Servicios de Vendedores
export const vendedoresService = {
  list: (params) => api.get('/api/vendedores/', { params }),
  get: (id) => api.get(`/api/vendedores/${id}/`),
  create: (data) => api.post('/api/vendedores/', data),
  update: (id, data) => api.patch(`/api/vendedores/${id}/`, data),
  delete: (id) => api.delete(`/api/vendedores/${id}/`)
};

// Servicios de Parámetros
export const parametrosService = {
  getMarcas: () => api.get('/api/parametros/marcas/', { params: { activo: true } }),
  getModelos: (marcaId) => api.get('/api/parametros/modelos/', { params: { marca: marcaId, activo: true } }),
  getCombustibles: () => api.get('/api/parametros/combustibles/', { params: { activo: true } }),
  getCajas: () => api.get('/api/parametros/cajas/', { params: { activo: true } }),
  getEstados: () => api.get('/api/parametros/estados/', { params: { activo: true } }),
  getCondiciones: () => api.get('/api/parametros/condiciones/', { params: { activo: true } }),
  getMonedas: () => api.get('/api/parametros/monedas/', { params: { activo: true } }),
  getSegmentos: () => api.get('/api/parametros/segmentos/', { params: { activo: true } })
};

export default api;
```

---

## Ejemplo: Componente de Listado de Vehículos (React)

```jsx
// components/VehiculosList.jsx
import { useState, useEffect } from 'react';
import { vehiculosService, parametrosService } from '../services/api';

export default function VehiculosList() {
  const [vehiculos, setVehiculos] = useState([]);
  const [marcas, setMarcas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    disponible: true,
    mostrar_en_web: true,
    ordering: '-created_at'
  });

  useEffect(() => {
    // Cargar marcas para el filtro
    parametrosService.getMarcas().then(res => setMarcas(res.data));
  }, []);

  useEffect(() => {
    setLoading(true);
    vehiculosService.list(filters)
      .then(res => setVehiculos(res.data.results))
      .finally(() => setLoading(false));
  }, [filters]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value || undefined }));
  };

  if (loading) return <p>Cargando...</p>;

  return (
    <div>
      {/* Filtros */}
      <div className="filters">
        <select onChange={e => handleFilterChange('marca', e.target.value)}>
          <option value="">Todas las marcas</option>
          {marcas.map(m => (
            <option key={m.id} value={m.id}>{m.nombre}</option>
          ))}
        </select>

        <input
          type="number"
          placeholder="Precio máximo"
          onChange={e => handleFilterChange('precio_max', e.target.value)}
        />

        <select onChange={e => handleFilterChange('ordering', e.target.value)}>
          <option value="-created_at">Más recientes</option>
          <option value="precio">Menor precio</option>
          <option value="-precio">Mayor precio</option>
          <option value="-anio">Más nuevos</option>
        </select>
      </div>

      {/* Listado */}
      <div className="vehiculos-grid">
        {vehiculos.map(v => (
          <div key={v.id} className="vehiculo-card">
            <img src={v.imagen_principal} alt={v.titulo} />
            <h3>{v.titulo}</h3>
            <p className="precio">{v.moneda_nombre} {Number(v.precio).toLocaleString()}</p>
            <p>{v.anio} | {v.km?.toLocaleString()} km</p>
            <p>{v.combustible_nombre} | {v.caja_nombre}</p>
            {v.reservado && <span className="badge reservado">Reservado</span>}
            <a href={`/vehiculos/${v.id}`}>Ver detalle</a>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Ejemplo: Formulario de Crear Vehículo (React)

```jsx
// components/VehiculoForm.jsx
import { useState, useEffect } from 'react';
import { vehiculosService, vendedoresService, parametrosService } from '../services/api';

export default function VehiculoForm({ onSuccess }) {
  const [formData, setFormData] = useState({
    marca: '',
    modelo: '',
    combustible: '',
    caja: '',
    estado: '',
    condicion: '',
    moneda: '',
    vendedor_dueno: '',
    patente: '',
    anio: '',
    color: '',
    precio: '',
    version: '',
    km: 0,
    mostrar_en_web: true
  });

  const [parametros, setParametros] = useState({
    marcas: [],
    modelos: [],
    combustibles: [],
    cajas: [],
    estados: [],
    condiciones: [],
    monedas: [],
    vendedores: []
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Cargar parámetros al montar
  useEffect(() => {
    Promise.all([
      parametrosService.getMarcas(),
      parametrosService.getCombustibles(),
      parametrosService.getCajas(),
      parametrosService.getEstados(),
      parametrosService.getCondiciones(),
      parametrosService.getMonedas(),
      vendedoresService.list({ activo: true })
    ]).then(([marcas, combustibles, cajas, estados, condiciones, monedas, vendedores]) => {
      setParametros({
        marcas: marcas.data,
        modelos: [],
        combustibles: combustibles.data,
        cajas: cajas.data,
        estados: estados.data,
        condiciones: condiciones.data,
        monedas: monedas.data,
        vendedores: vendedores.data
      });
    });
  }, []);

  // Cargar modelos cuando cambia la marca
  useEffect(() => {
    if (formData.marca) {
      parametrosService.getModelos(formData.marca)
        .then(res => setParametros(prev => ({ ...prev, modelos: res.data })));
    } else {
      setParametros(prev => ({ ...prev, modelos: [] }));
    }
    setFormData(prev => ({ ...prev, modelo: '' }));
  }, [formData.marca]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await vehiculosService.create(formData);
      onSuccess?.(response.data);
    } catch (err) {
      setError(err.response?.data || 'Error al crear vehículo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{JSON.stringify(error)}</div>}

      <div className="form-group">
        <label>Marca *</label>
        <select name="marca" value={formData.marca} onChange={handleChange} required>
          <option value="">Seleccionar marca</option>
          {parametros.marcas.map(m => (
            <option key={m.id} value={m.id}>{m.nombre}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Modelo *</label>
        <select name="modelo" value={formData.modelo} onChange={handleChange} required disabled={!formData.marca}>
          <option value="">Seleccionar modelo</option>
          {parametros.modelos.map(m => (
            <option key={m.id} value={m.id}>{m.nombre}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Patente *</label>
        <input type="text" name="patente" value={formData.patente} onChange={handleChange} required />
      </div>

      <div className="form-group">
        <label>Año *</label>
        <input type="number" name="anio" value={formData.anio} onChange={handleChange} required min="1900" max="2100" />
      </div>

      <div className="form-group">
        <label>Color *</label>
        <input type="text" name="color" value={formData.color} onChange={handleChange} required />
      </div>

      <div className="form-group">
        <label>Precio *</label>
        <input type="number" name="precio" value={formData.precio} onChange={handleChange} required step="0.01" />
      </div>

      <div className="form-group">
        <label>Moneda *</label>
        <select name="moneda" value={formData.moneda} onChange={handleChange} required>
          <option value="">Seleccionar</option>
          {parametros.monedas.map(m => (
            <option key={m.id} value={m.id}>{m.nombre}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Combustible *</label>
        <select name="combustible" value={formData.combustible} onChange={handleChange} required>
          <option value="">Seleccionar</option>
          {parametros.combustibles.map(c => (
            <option key={c.id} value={c.id}>{c.nombre}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Caja *</label>
        <select name="caja" value={formData.caja} onChange={handleChange} required>
          <option value="">Seleccionar</option>
          {parametros.cajas.map(c => (
            <option key={c.id} value={c.id}>{c.nombre}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Estado *</label>
        <select name="estado" value={formData.estado} onChange={handleChange} required>
          <option value="">Seleccionar</option>
          {parametros.estados.map(e => (
            <option key={e.id} value={e.id}>{e.nombre}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Condición *</label>
        <select name="condicion" value={formData.condicion} onChange={handleChange} required>
          <option value="">Seleccionar</option>
          {parametros.condiciones.map(c => (
            <option key={c.id} value={c.id}>{c.nombre}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Vendedor/Dueño *</label>
        <select name="vendedor_dueno" value={formData.vendedor_dueno} onChange={handleChange} required>
          <option value="">Seleccionar</option>
          {parametros.vendedores.map(v => (
            <option key={v.id} value={v.id}>{v.full_name} - {v.dni}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Versión</label>
        <input type="text" name="version" value={formData.version} onChange={handleChange} placeholder="Ej: 1.6 SE" />
      </div>

      <div className="form-group">
        <label>Kilometraje</label>
        <input type="number" name="km" value={formData.km} onChange={handleChange} min="0" />
      </div>

      <div className="form-group">
        <label>
          <input type="checkbox" name="mostrar_en_web" checked={formData.mostrar_en_web} onChange={handleChange} />
          Mostrar en web
        </label>
      </div>

      <button type="submit" disabled={loading}>
        {loading ? 'Guardando...' : 'Crear Vehículo'}
      </button>
    </form>
  );
}
```

---

## Variables de Entorno

Crear archivo `.env.local` (Next.js) o `.env` (React/Vite):

```bash
# Desarrollo
NEXT_PUBLIC_API_URL=https://api-dev.autobiliaria.cloud

# Producción
NEXT_PUBLIC_API_URL=https://api.autobiliaria.cloud
```

---

## Manejo de Errores Comunes

| Status | Significado | Acción |
|--------|-------------|--------|
| 400 | Datos inválidos | Mostrar errores del campo |
| 401 | No autenticado | Redirigir a login |
| 403 | Sin permisos | Mostrar mensaje |
| 404 | No encontrado | Mostrar página 404 |
| 500 | Error del servidor | Mostrar error genérico |

```javascript
try {
  await vehiculosService.create(data);
} catch (error) {
  if (error.response) {
    switch (error.response.status) {
      case 400:
        // Errores de validación
        // error.response.data = { patente: ["Ya existe"], ... }
        setErrors(error.response.data);
        break;
      case 401:
        // No autenticado
        router.push('/admin/login');
        break;
      default:
        setError('Ocurrió un error. Intenta de nuevo.');
    }
  }
}
```

---

## Datos Cargados en el Sistema

| Parámetro | Cantidad |
|-----------|----------|
| Marcas | ~130 |
| Modelos | ~1500 |
| Segmentos | 43 |
| Combustibles | 5 |
| Cajas | 2 |
| Estados | 3 |
| Condiciones | 6 |
| Monedas | 4 |

---

## CORS

CORS ya está configurado en el backend para aceptar requests desde cualquier origen en desarrollo. En producción, se configurarán los dominios específicos del frontend.

---

## Contacto

Si tenés dudas sobre la API o necesitás algún cambio en el backend, contactá al equipo de backend.

---

## Checklist de Funcionalidades

### Web Pública
- [ ] Home con vehículos destacados
- [ ] Listado de vehículos con filtros
- [ ] Detalle de vehículo con galería de imágenes
- [ ] Búsqueda de vehículos
- [ ] Diseño responsive
- [ ] SEO básico (meta tags)

### Panel de Administración
- [ ] Login/Logout
- [ ] Dashboard con estadísticas
- [ ] Listado de vehículos (con filtros, búsqueda, paginación)
- [ ] Crear vehículo
- [ ] Editar vehículo
- [ ] Subir/eliminar imágenes
- [ ] Marcar vendido/reservado
- [ ] Eliminar vehículo
- [ ] Listado de vendedores
- [ ] Crear/editar vendedor
- [ ] Gestión de parámetros (opcional)
