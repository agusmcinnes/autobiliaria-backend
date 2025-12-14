# API Publicaciones de Vehiculos

Documentacion de endpoints para que clientes publiquen vehiculos para venta.

## Base URL

```
https://api.autobiliaria.cloud/api/publicaciones/
```

## Importante

El endpoint para **crear publicaciones es PUBLICO** - no requiere autenticacion.
Esto permite que los clientes desde la web envien sus vehiculos para revision.

Los demas endpoints (listar, ver, marcar vista/eliminada) requieren autenticacion JWT.

---

## Endpoints Publicos (Sin Auth)

### Obtener tipos de vehiculo

```http
GET /api/publicaciones/tipos-vehiculo/
```

**Respuesta:**

```json
[
  {"value": "auto", "label": "Auto"},
  {"value": "camioneta", "label": "Camioneta"},
  {"value": "camion", "label": "Camion"},
  {"value": "moto", "label": "Moto"}
]
```

---

### Crear publicacion con imagenes

```http
POST /api/publicaciones/
Content-Type: multipart/form-data
```

**Campos:**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `nombre` | string(100) | Si | Nombre completo del cliente |
| `email` | email | Si | Email de contacto |
| `telefono` | string(20) | Si | Telefono/celular |
| `tipo_vehiculo` | string | Si | `auto`, `camioneta`, `camion`, `moto` |
| `marca` | integer | Si | ID de la marca |
| `modelo` | integer | Si | ID del modelo |
| `anio` | integer | Si | Ano del vehiculo (1900-2100) |
| `km` | integer | Si | Kilometraje |
| `imagenes` | file[] | No | Hasta 4 imagenes (multipart) |

**Ejemplo Frontend (React + FormData):**

```javascript
async function enviarPublicacion(data, imagenes) {
  const formData = new FormData();

  // Datos del formulario
  formData.append('nombre', data.nombre);
  formData.append('email', data.email);
  formData.append('telefono', data.telefono);
  formData.append('tipo_vehiculo', data.tipoVehiculo);
  formData.append('marca', data.marcaId);
  formData.append('modelo', data.modeloId);
  formData.append('anio', data.anio);
  formData.append('km', data.km);

  // Imagenes (maximo 4)
  imagenes.forEach((imagen) => {
    formData.append('imagenes', imagen);
  });

  const response = await fetch('https://api.autobiliaria.cloud/api/publicaciones/', {
    method: 'POST',
    body: formData,
    // NO incluir Content-Type - el browser lo setea automaticamente con boundary
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(JSON.stringify(error));
  }

  return response.json();
}
```

**Respuesta Exitosa (201 Created):**

```json
{
  "id": 1,
  "nombre": "Juan Perez",
  "email": "juan@email.com",
  "telefono": "1122334455",
  "tipo_vehiculo": "auto",
  "marca": 5,
  "modelo": 42,
  "anio": 2020,
  "km": 50000
}
```

**Errores de Validacion (400 Bad Request):**

```json
{
  "modelo": ["El modelo \"Focus\" no pertenece a la marca \"Toyota\"."]
}
```

```json
{
  "imagenes": ["Maximo 4 imagenes permitidas."]
}
```

```json
{
  "email": ["Introduzca una direccion de correo electronico valida."],
  "nombre": ["Este campo es requerido."]
}
```

---

## Endpoints Privados (Requieren Auth)

Incluir header:
```
Authorization: Bearer <access_token>
```

### Listar publicaciones

```http
GET /api/publicaciones/
```

**Query Parameters:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `estado` | string | Filtrar por estado (`pendiente`, `vista`, `eliminada`) |
| `pendientes` | boolean | Solo publicaciones pendientes (`true`) |
| `tipo_vehiculo` | string | Filtrar por tipo (`auto`, `camioneta`, etc.) |
| `marca` | integer | Filtrar por ID de marca |
| `modelo` | integer | Filtrar por ID de modelo |
| `fecha_desde` | datetime | Desde fecha (ISO format) |
| `fecha_hasta` | datetime | Hasta fecha (ISO format) |
| `search` | string | Buscar en nombre, email, telefono, marca, modelo |
| `ordering` | string | Ordenar (`created_at`, `-created_at`, `estado`, `nombre`) |

**Ejemplos:**

```bash
# Todas las publicaciones
GET /api/publicaciones/

# Solo pendientes
GET /api/publicaciones/?pendientes=true

# Por tipo de vehiculo
GET /api/publicaciones/?tipo_vehiculo=camioneta

# Buscar por email
GET /api/publicaciones/?search=juan@email.com
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "nombre": "Juan Perez",
    "email": "juan@email.com",
    "telefono": "1122334455",
    "tipo_vehiculo": "auto",
    "tipo_vehiculo_display": "Auto",
    "marca": 5,
    "marca_nombre": "Ford",
    "modelo": 42,
    "modelo_nombre": "Focus",
    "anio": 2020,
    "km": 50000,
    "estado": "pendiente",
    "estado_display": "Pendiente",
    "cant_imagenes": 3,
    "created_at": "2024-12-14T15:30:00Z"
  }
]
```

---

### Obtener detalle

```http
GET /api/publicaciones/{id}/
```

**Respuesta:**

```json
{
  "id": 1,
  "nombre": "Juan Perez",
  "email": "juan@email.com",
  "telefono": "1122334455",
  "tipo_vehiculo": "auto",
  "tipo_vehiculo_display": "Auto",
  "marca": 5,
  "marca_detail": {
    "id": 5,
    "nombre": "Ford",
    "activo": true
  },
  "modelo": 42,
  "modelo_detail": {
    "id": 42,
    "nombre": "Focus",
    "marca": 5,
    "activo": true
  },
  "anio": 2020,
  "km": 50000,
  "estado": "pendiente",
  "estado_display": "Pendiente",
  "notas_staff": "",
  "revisada_por": null,
  "revisada_por_nombre": null,
  "fecha_revision": null,
  "imagenes": [
    {
      "id": 1,
      "imagen": "/media/publicaciones/2024/12/foto1.jpg",
      "imagen_url": "https://api.autobiliaria.cloud/media/publicaciones/2024/12/foto1.jpg",
      "orden": 0,
      "created_at": "2024-12-14T15:30:00Z"
    }
  ],
  "created_at": "2024-12-14T15:30:00Z",
  "updated_at": "2024-12-14T15:30:00Z"
}
```

---

### Marcar como vista

```http
PATCH /api/publicaciones/{id}/marcar-vista/
```

Asigna automaticamente:
- `estado: vista`
- `revisada_por`: usuario actual
- `fecha_revision`: timestamp actual

**Respuesta:** Retorna la publicacion actualizada

---

### Marcar como eliminada

```http
PATCH /api/publicaciones/{id}/marcar-eliminada/
```

**Body (opcional):**

```json
{
  "notas_staff": "Datos incorrectos o spam"
}
```

Asigna automaticamente:
- `estado: eliminada`
- `revisada_por`: usuario actual
- `fecha_revision`: timestamp actual
- `notas_staff`: nota si viene en el request

**Respuesta:** Retorna la publicacion actualizada

---

### Actualizar notas

```http
PATCH /api/publicaciones/{id}/
```

**Body:**

```json
{
  "notas_staff": "Llamado al cliente, confirma datos"
}
```

Solo se puede actualizar: `notas_staff`

---

### Eliminar publicacion (hard delete)

```http
DELETE /api/publicaciones/{id}/
```

**Respuesta:** `204 No Content`

---

## Integracion Frontend

### Formulario de Publicacion (React)

```jsx
import { useState, useRef, useEffect } from 'react';

function FormularioPublicacion({ marcas, onSuccess, onError }) {
  const [loading, setLoading] = useState(false);
  const [modelos, setModelos] = useState([]);
  const [tiposVehiculo, setTiposVehiculo] = useState([]);
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    telefono: '',
    tipoVehiculo: 'auto',
    marcaId: '',
    modeloId: '',
    anio: '',
    km: '',
  });
  const [imagenes, setImagenes] = useState([]);
  const fileInputRef = useRef();

  // Cargar tipos de vehiculo al montar
  useEffect(() => {
    fetch('https://api.autobiliaria.cloud/api/publicaciones/tipos-vehiculo/')
      .then(res => res.json())
      .then(data => setTiposVehiculo(data));
  }, []);

  // Cargar modelos cuando cambia la marca
  useEffect(() => {
    if (formData.marcaId) {
      fetch(`https://api.autobiliaria.cloud/api/parametros/modelos/?marca=${formData.marcaId}`)
        .then(res => res.json())
        .then(data => setModelos(data));
    } else {
      setModelos([]);
    }
  }, [formData.marcaId]);

  const handleImageChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 4) {
      alert('Maximo 4 imagenes');
      return;
    }
    setImagenes(files);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const data = new FormData();
      data.append('nombre', formData.nombre);
      data.append('email', formData.email);
      data.append('telefono', formData.telefono);
      data.append('tipo_vehiculo', formData.tipoVehiculo);
      data.append('marca', formData.marcaId);
      data.append('modelo', formData.modeloId);
      data.append('anio', formData.anio);
      data.append('km', formData.km);

      imagenes.forEach((img) => {
        data.append('imagenes', img);
      });

      const response = await fetch('https://api.autobiliaria.cloud/api/publicaciones/', {
        method: 'POST',
        body: data,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(Object.values(error).flat().join(', '));
      }

      const result = await response.json();
      onSuccess?.(result);

      // Reset form
      setFormData({
        nombre: '', email: '', telefono: '',
        tipoVehiculo: 'auto', marcaId: '', modeloId: '',
        anio: '', km: '',
      });
      setImagenes([]);
      fileInputRef.current.value = '';
    } catch (error) {
      onError?.(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Datos de contacto</h3>
      <input
        type="text"
        placeholder="Nombre completo"
        value={formData.nombre}
        onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
        required
      />
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        required
      />
      <input
        type="tel"
        placeholder="Telefono"
        value={formData.telefono}
        onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
        required
      />

      <h3>Datos del vehiculo</h3>
      <select
        value={formData.tipoVehiculo}
        onChange={(e) => setFormData({ ...formData, tipoVehiculo: e.target.value })}
        required
      >
        {tiposVehiculo.map(tipo => (
          <option key={tipo.value} value={tipo.value}>{tipo.label}</option>
        ))}
      </select>

      <select
        value={formData.marcaId}
        onChange={(e) => setFormData({ ...formData, marcaId: e.target.value, modeloId: '' })}
        required
      >
        <option value="">Seleccionar marca</option>
        {marcas.map(marca => (
          <option key={marca.id} value={marca.id}>{marca.nombre}</option>
        ))}
      </select>

      <select
        value={formData.modeloId}
        onChange={(e) => setFormData({ ...formData, modeloId: e.target.value })}
        required
        disabled={!formData.marcaId}
      >
        <option value="">Seleccionar modelo</option>
        {modelos.map(modelo => (
          <option key={modelo.id} value={modelo.id}>{modelo.nombre}</option>
        ))}
      </select>

      <input
        type="number"
        placeholder="Ano"
        value={formData.anio}
        onChange={(e) => setFormData({ ...formData, anio: e.target.value })}
        min="1900"
        max="2100"
        required
      />
      <input
        type="number"
        placeholder="Kilometraje"
        value={formData.km}
        onChange={(e) => setFormData({ ...formData, km: e.target.value })}
        min="0"
        required
      />

      <h3>Imagenes (max 4)</h3>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={handleImageChange}
      />
      {imagenes.length > 0 && (
        <p>{imagenes.length} imagen(es) seleccionada(s)</p>
      )}

      <button type="submit" disabled={loading}>
        {loading ? 'Enviando...' : 'Publicar Vehiculo'}
      </button>
    </form>
  );
}
```

### Servicio con Axios (para panel admin)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.autobiliaria.cloud/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const publicacionesService = {
  // Publico - no requiere auth
  getTiposVehiculo: () => axios.get('/api/publicaciones/tipos-vehiculo/'),
  crear: (formData) => axios.post('/api/publicaciones/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),

  // Requieren auth
  listar: (params) => api.get('/publicaciones/', { params }),
  obtener: (id) => api.get(`/publicaciones/${id}/`),
  marcarVista: (id) => api.patch(`/publicaciones/${id}/marcar-vista/`),
  marcarEliminada: (id, notas) => api.patch(`/publicaciones/${id}/marcar-eliminada/`, { notas_staff: notas }),
  actualizarNotas: (id, notas) => api.patch(`/publicaciones/${id}/`, { notas_staff: notas }),
  eliminar: (id) => api.delete(`/publicaciones/${id}/`),
};

// Uso - Crear publicacion
const formData = new FormData();
formData.append('nombre', 'Juan');
formData.append('email', 'juan@email.com');
// ... otros campos
formData.append('imagenes', file1);
formData.append('imagenes', file2);

await publicacionesService.crear(formData);

// Uso - Panel admin
const pendientes = await publicacionesService.listar({ pendientes: true });
await publicacionesService.marcarVista(1);
await publicacionesService.marcarEliminada(2, 'Datos incorrectos');
```

---

## Estados de Publicacion

| Valor | Display | Descripcion |
|-------|---------|-------------|
| `pendiente` | Pendiente | Nueva publicacion, sin revisar |
| `vista` | Vista | Revisada por el staff |
| `eliminada` | Eliminada | Marcada como eliminada/descartada |

---

## Tipos de Vehiculo

| Valor | Display |
|-------|---------|
| `auto` | Auto |
| `camioneta` | Camioneta |
| `camion` | Camion |
| `moto` | Moto |

---

## Campos del Modelo

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `id` | integer | ID autoincremental |
| `nombre` | string(100) | Nombre del cliente |
| `email` | email | Email de contacto |
| `telefono` | string(20) | Telefono del cliente |
| `tipo_vehiculo` | string | Tipo de vehiculo |
| `marca` | FK | ID de la marca |
| `modelo` | FK | ID del modelo |
| `anio` | integer | Ano del vehiculo |
| `km` | integer | Kilometraje |
| `estado` | string | Estado de la publicacion |
| `notas_staff` | text | Notas internas del staff |
| `revisada_por` | FK | Usuario que reviso |
| `fecha_revision` | datetime | Cuando fue revisada |
| `created_at` | datetime | Fecha de creacion |
| `updated_at` | datetime | Ultima actualizacion |

## Campos de ImagenPublicacion

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `id` | integer | ID autoincremental |
| `publicacion` | FK | ID de la publicacion |
| `imagen` | ImageField | Archivo de imagen |
| `orden` | integer | Orden de visualizacion |
| `created_at` | datetime | Fecha de creacion |
