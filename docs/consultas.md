# API Consultas

Documentacion de endpoints para consultas y reservas de vehiculos.

## Base URL

```
https://api.autobiliaria.cloud/api/consultas/
```

## Importante

El endpoint para **crear consultas es PUBLICO** - no requiere autenticacion.
Esto permite que los clientes desde la web envien consultas/reservas sin estar logueados.

Los demas endpoints (listar, ver, actualizar, eliminar) requieren autenticacion JWT.

---

## Endpoints Publicos (Sin Auth)

### Crear consulta/reserva

```http
POST /api/consultas/
```

**Body:**

```json
{
  "nombre": "Juan Perez",
  "email": "juan@email.com",
  "telefono": "1122334455",
  "mensaje": "Hola, estoy interesado en este vehiculo. Cuando puedo verlo?",
  "tipo": "consulta",
  "vehiculo": 5
}
```

**Campos:**

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `nombre` | string(100) | Si | Nombre completo del cliente |
| `email` | email | Si | Email de contacto |
| `telefono` | string(20) | Si | Telefono/celular |
| `mensaje` | text | Si | Mensaje o consulta |
| `tipo` | string | Si | `consulta` o `reserva` |
| `vehiculo` | integer | Si | ID del vehiculo |

**Ejemplo Frontend (Fetch):**

```javascript
async function enviarConsulta(data) {
  const response = await fetch('https://api.autobiliaria.cloud/api/consultas/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      nombre: data.nombre,
      email: data.email,
      telefono: data.telefono,
      mensaje: data.mensaje,
      tipo: 'consulta',  // o 'reserva'
      vehiculo: data.vehiculoId
    })
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
  "mensaje": "Hola, estoy interesado en este vehiculo...",
  "tipo": "consulta",
  "vehiculo": 5
}
```

**Errores de Validacion (400 Bad Request):**

```json
{
  "vehiculo": ["El vehiculo no esta disponible."]
}
```

```json
{
  "vehiculo": ["El vehiculo ya fue vendido."]
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

### Listar consultas

```http
GET /api/consultas/
```

**Query Parameters:**

| Parametro | Tipo | Descripcion |
|-----------|------|-------------|
| `tipo` | string | Filtrar por tipo (`consulta` o `reserva`) |
| `vehiculo` | integer | Filtrar por ID de vehiculo |
| `leida` | boolean | Filtrar por leidas (`true`/`false`) |
| `atendida` | boolean | Filtrar por atendidas (`true`/`false`) |
| `pendientes` | boolean | Solo consultas no atendidas (`true`) |
| `fecha_desde` | datetime | Desde fecha (ISO format) |
| `fecha_hasta` | datetime | Hasta fecha (ISO format) |
| `search` | string | Buscar en nombre, email, telefono, patente |
| `ordering` | string | Ordenar (`created_at`, `-created_at`, `tipo`) |

**Ejemplos:**

```bash
# Todas las consultas
GET /api/consultas/

# Solo reservas pendientes
GET /api/consultas/?tipo=reserva&pendientes=true

# Consultas de un vehiculo especifico
GET /api/consultas/?vehiculo=5

# Consultas no leidas
GET /api/consultas/?leida=false

# Buscar por email
GET /api/consultas/?search=juan@email.com
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "nombre": "Juan Perez",
    "email": "juan@email.com",
    "telefono": "1122334455",
    "tipo": "consulta",
    "tipo_display": "Consulta",
    "vehiculo": 5,
    "vehiculo_titulo": "Ford Focus 1.6 SE 2020",
    "vehiculo_patente": "AB123CD",
    "leida": false,
    "atendida": false,
    "created_at": "2024-12-14T15:30:00Z"
  }
]
```

---

### Obtener detalle

```http
GET /api/consultas/{id}/
```

**Respuesta:**

```json
{
  "id": 1,
  "nombre": "Juan Perez",
  "email": "juan@email.com",
  "telefono": "1122334455",
  "mensaje": "Hola, estoy interesado en este vehiculo...",
  "tipo": "consulta",
  "tipo_display": "Consulta",
  "vehiculo": 5,
  "vehiculo_titulo": "Ford Focus 1.6 SE 2020",
  "vehiculo_patente": "AB123CD",
  "leida": true,
  "atendida": false,
  "notas_staff": "",
  "atendida_por": null,
  "atendida_por_nombre": null,
  "fecha_atendida": null,
  "created_at": "2024-12-14T15:30:00Z",
  "updated_at": "2024-12-14T15:30:00Z"
}
```

---

### Marcar como leida

```http
PATCH /api/consultas/{id}/marcar-leida/
```

**Respuesta:** Retorna la consulta actualizada con `leida: true`

---

### Marcar como atendida

```http
PATCH /api/consultas/{id}/marcar-atendida/
```

Asigna automaticamente:
- `atendida: true`
- `leida: true`
- `atendida_por`: usuario actual
- `fecha_atendida`: timestamp actual

**Respuesta:**

```json
{
  "id": 1,
  "leida": true,
  "atendida": true,
  "atendida_por": 1,
  "atendida_por_nombre": "Admin Usuario",
  "fecha_atendida": "2024-12-14T16:00:00Z",
  ...
}
```

---

### Actualizar notas

```http
PATCH /api/consultas/{id}/
```

**Body:**

```json
{
  "notas_staff": "Llamado el 14/12, queda en venir el sabado a las 10hs"
}
```

Solo se pueden actualizar: `leida`, `atendida`, `notas_staff`

---

### Eliminar consulta

```http
DELETE /api/consultas/{id}/
```

**Respuesta:** `204 No Content`

---

## Integracion Frontend

### Formulario de Consulta (React)

```jsx
import { useState } from 'react';

function FormularioConsulta({ vehiculoId, onSuccess, onError }) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    telefono: '',
    mensaje: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('https://api.autobiliaria.cloud/api/consultas/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          tipo: 'consulta',
          vehiculo: vehiculoId,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(Object.values(error).flat().join(', '));
      }

      const data = await response.json();
      onSuccess?.(data);
      setFormData({ nombre: '', email: '', telefono: '', mensaje: '' });
    } catch (error) {
      onError?.(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
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
      <textarea
        placeholder="Tu mensaje..."
        value={formData.mensaje}
        onChange={(e) => setFormData({ ...formData, mensaje: e.target.value })}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Enviando...' : 'Enviar Consulta'}
      </button>
    </form>
  );
}
```

### Boton de Reserva (React)

```jsx
function BotonReserva({ vehiculoId }) {
  const [showModal, setShowModal] = useState(false);

  const handleReserva = async (formData) => {
    const response = await fetch('https://api.autobiliaria.cloud/api/consultas/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...formData,
        tipo: 'reserva',  // <- Diferencia con consulta
        vehiculo: vehiculoId,
      }),
    });

    if (!response.ok) throw new Error('Error al reservar');
    return response.json();
  };

  return (
    <>
      <button onClick={() => setShowModal(true)}>
        Reservar Vehiculo
      </button>
      {showModal && (
        <ModalReserva
          onSubmit={handleReserva}
          onClose={() => setShowModal(false)}
        />
      )}
    </>
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

export const consultasService = {
  // Publico - no requiere auth
  crear: (data) => axios.post('/api/consultas/', data),

  // Requieren auth
  listar: (params) => api.get('/consultas/', { params }),
  obtener: (id) => api.get(`/consultas/${id}/`),
  marcarLeida: (id) => api.patch(`/consultas/${id}/marcar-leida/`),
  marcarAtendida: (id) => api.patch(`/consultas/${id}/marcar-atendida/`),
  actualizarNotas: (id, notas) => api.patch(`/consultas/${id}/`, { notas_staff: notas }),
  eliminar: (id) => api.delete(`/consultas/${id}/`),
};

// Uso
await consultasService.crear({
  nombre: 'Juan',
  email: 'juan@email.com',
  telefono: '1122334455',
  mensaje: 'Quiero info',
  tipo: 'consulta',
  vehiculo: 5,
});

const pendientes = await consultasService.listar({ pendientes: true });
await consultasService.marcarAtendida(1);
```

---

## Tipos de Consulta

| Valor | Display | Descripcion |
|-------|---------|-------------|
| `consulta` | Consulta | Consulta general sobre el vehiculo |
| `reserva` | Reserva | Solicitud de reserva del vehiculo |

---

## Campos del Modelo

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `id` | integer | ID autoincremental |
| `nombre` | string(100) | Nombre del cliente |
| `email` | email | Email de contacto |
| `telefono` | string(20) | Telefono del cliente |
| `mensaje` | text | Mensaje/consulta |
| `tipo` | string | `consulta` o `reserva` |
| `vehiculo` | FK | ID del vehiculo consultado |
| `leida` | boolean | Si fue leida por staff |
| `atendida` | boolean | Si fue atendida |
| `notas_staff` | text | Notas internas del staff |
| `atendida_por` | FK | Usuario que la atendio |
| `fecha_atendida` | datetime | Cuando fue atendida |
| `created_at` | datetime | Fecha de creacion |
| `updated_at` | datetime | Ultima actualizacion |
