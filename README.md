# Autobiliaria - Backend

## Requisitos previos

- Python 3.10+

## Instalacion

### 1. Crear entorno virtual

```bash
cd backend
python -m venv venv
```

### 2. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar el archivo de ejemplo y configurar:

```bash
copy .env.example .env
```

Editar `.env` y agregar una SECRET_KEY.

### 5. Ejecutar migraciones

```bash
python manage.py migrate
```

### 6. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

El servidor estara disponible en: http://127.0.0.1:8000/

## Estructura del proyecto

```
backend/
├── config/          # Configuracion del proyecto Django
├── apps/            # Aplicaciones del proyecto
│   ├── usuarios/
│   ├── vendedores/
│   ├── parametros/
│   ├── vehiculos/
│   └── api/
├── manage.py
├── requirements.txt
└── .env.example
```
