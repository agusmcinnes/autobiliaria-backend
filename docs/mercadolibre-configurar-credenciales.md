# Configurar Credenciales de Mercado Libre

## Requisitos previos

El cliente debe haberte enviado:
- **App ID** (número largo, ej: `1234567890123456`)
- **Secret Key** (clave alfanumérica, ej: `AbCdEfGhIjKlMnOp...`)

---

## Pasos a seguir

### 1. Conectar al servidor

```bash
ssh root@92.112.177.217
```

### 2. Editar el archivo de variables de entorno

**Para DEV:**
```bash
nano /home/deploy/autobiliaria/dev/.env.dev
```

**Para PROD:**
```bash
nano /home/deploy/autobiliaria/prod/.env.prod
```

### 3. Buscar y completar las variables de ML

Buscar estas líneas (ya existen en el archivo):

```bash
ML_APP_ID=
ML_SECRET_KEY=
```

Reemplazar con los valores del cliente:

```bash
ML_APP_ID=1234567890123456
ML_SECRET_KEY=AbCdEfGhIjKlMnOpQrStUvWxYz123456
```

Guardar con `Ctrl+O`, `Enter`, `Ctrl+X`

### 4. Reiniciar el contenedor

**Para DEV:**
```bash
cd /home/deploy/autobiliaria/dev
docker compose -f docker-compose.dev.yml restart
```

**Para PROD:**
```bash
cd /home/deploy/autobiliaria/prod
docker compose -f docker-compose.prod.yml restart
```

### 5. Verificar que funcione

```bash
# Ver logs (no debería haber errores)
docker logs autobiliaria-backend-prod --tail 20
```

---

## Probar la conexión

1. Ir al panel admin: https://admin.autobiliaria.cloud/admin/mercadolibre
2. Click en **"Conectar con Mercado Libre"**
3. Autorizar la aplicación en la página de ML
4. Debería redirigir de vuelta al panel con estado "Conectado"

---

## Troubleshooting

### Error "redirect_uri inválida"
- Verificar que en la app de ML (developers.mercadolibre.com.ar) el Redirect URI sea exactamente:
  - DEV: `https://api-dev.autobiliaria.cloud/api/mercadolibre/auth/callback/`
  - PROD: `https://api.autobiliaria.cloud/api/mercadolibre/auth/callback/`

### Error "client_id inválido"
- Verificar que `ML_APP_ID` esté bien copiado (sin espacios extra)

### Error "Tenemos un problema" en ML
- Las credenciales están mal o la app no está activa en ML
- Pedirle al cliente que verifique el estado de su app en el Dev Center

---

## Resumen rápido (copy-paste)

```bash
# Conectar
ssh root@92.112.177.217

# Editar (cambiar dev/prod según corresponda)
nano /home/deploy/autobiliaria/prod/.env.prod

# Agregar los valores reales en:
# ML_APP_ID=xxx
# ML_SECRET_KEY=xxx

# Reiniciar
cd /home/deploy/autobiliaria/prod
docker compose -f docker-compose.prod.yml restart

# Verificar
docker logs autobiliaria-backend-prod --tail 20
```
