# Integración con Mercado Libre - Información para el Cliente

## ¿Qué se hizo?

Se agregó una nueva sección en el panel de administración que permite **conectar la cuenta de Mercado Libre** de Autobiliaria con el sistema.

### Funcionalidades incluidas:

1. **Importar publicaciones existentes**: Trae todas las publicaciones de vehículos que ya tienen en ML y las muestra en el sistema.

2. **Vinculación automática por patente**: El sistema detecta la patente en las publicaciones de ML y las vincula automáticamente con los vehículos cargados en Autobiliaria.

3. **Publicar desde el sistema**: Pueden publicar un vehículo del inventario directamente a Mercado Libre sin salir del sistema.

4. **Gestionar publicaciones**: Pausar, activar o cerrar publicaciones de ML desde el panel de Autobiliaria.

5. **Ver estadísticas**: Dashboard con cantidad de publicaciones activas, pausadas, vinculadas, etc.

---

## ¿Qué necesitamos de ustedes?

Para que la integración funcione, necesitamos que creen una **aplicación de desarrollador** en Mercado Libre. Es un proceso simple y gratuito:

### Pasos a seguir:

1. **Ingresar a**: https://developers.mercadolibre.com.ar/devcenter

2. **Iniciar sesión** con la cuenta de Mercado Libre de Autobiliaria (la misma donde tienen las publicaciones)

3. **Crear nueva aplicación**:
   - Nombre: `Autobiliaria`
   - Descripción: `Sistema de gestión de vehículos`
   - **Redirect URI**: `https://api-dev.autobiliaria.cloud/api/mercadolibre/auth/callback/`

4. **Enviarnos las credenciales** que les genera:
   - **App ID** (un número largo)
   - **Secret Key** (una clave alfanumérica)

> **Importante**: Estas credenciales son privadas y solo las usamos para conectar el sistema. No las compartan públicamente.

---

## ¿Cómo se usa una vez configurado?

1. En el panel admin, ir a **Mercado Libre** en el menú lateral
2. Click en **"Conectar con Mercado Libre"**
3. Autorizar la aplicación en la página de ML
4. ¡Listo! Ya pueden sincronizar y gestionar publicaciones

---

## Preguntas frecuentes

**¿Tiene algún costo?**
No, crear la aplicación en ML es gratuito.

**¿Es seguro?**
Sí. Usamos el sistema oficial de autenticación de Mercado Libre (OAuth2). En cualquier momento pueden desconectar la cuenta desde el panel.

**¿Qué permisos pide?**
Solo permisos para leer y gestionar las publicaciones de vehículos.

**¿Hay que hacer esto para producción también?**
Sí, cuando pasemos a producción necesitaremos actualizar la URL de redirect. Les avisaremos.

---

## Contacto

Si tienen dudas sobre cómo crear la aplicación en Mercado Libre, avísennos y los guiamos paso a paso.
