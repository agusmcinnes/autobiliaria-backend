"""
Management command para migrar imágenes locales a Cloudflare R2.

Uso:
    python manage.py migrar_imagenes_r2           # Migra todo
    python manage.py migrar_imagenes_r2 --dry-run # Solo muestra qué haría
    python manage.py migrar_imagenes_r2 --only-vehiculos  # Solo vehículos
    python manage.py migrar_imagenes_r2 --only-publicaciones  # Solo publicaciones
"""

import os
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.conf import settings
from apps.vehiculos.models import ImagenVehiculo
from apps.publicaciones.models import ImagenPublicacion


class Command(BaseCommand):
    help = 'Migra imágenes locales a Cloudflare R2'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra qué haría sin ejecutar cambios',
        )
        parser.add_argument(
            '--only-vehiculos',
            action='store_true',
            help='Solo migrar imágenes de vehículos',
        )
        parser.add_argument(
            '--only-publicaciones',
            action='store_true',
            help='Solo migrar imágenes de publicaciones',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        only_vehiculos = options['only_vehiculos']
        only_publicaciones = options['only_publicaciones']

        # Verificar que R2 está configurado
        if not getattr(settings, 'USE_R2_STORAGE', False):
            self.stdout.write(
                self.style.ERROR('USE_R2_STORAGE no está habilitado. Configurá las variables de R2 primero.')
            )
            return

        if dry_run:
            self.stdout.write(self.style.WARNING('=== MODO DRY-RUN (no se harán cambios) ===\n'))

        total_migradas = 0
        total_errores = 0

        # Migrar imágenes de vehículos
        if not only_publicaciones:
            migradas, errores = self._migrar_imagenes_vehiculos(dry_run)
            total_migradas += migradas
            total_errores += errores

        # Migrar imágenes de publicaciones
        if not only_vehiculos:
            migradas, errores = self._migrar_imagenes_publicaciones(dry_run)
            total_migradas += migradas
            total_errores += errores

        # Resumen
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'Migración completada:'))
        self.stdout.write(f'  - Imágenes migradas: {total_migradas}')
        self.stdout.write(f'  - Errores: {total_errores}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\nEsto fue un dry-run. Ejecutá sin --dry-run para aplicar cambios.'))

    def _migrar_imagenes_vehiculos(self, dry_run):
        """Migra imágenes de ImagenVehiculo a R2."""
        self.stdout.write('\n--- Migrando imágenes de VEHÍCULOS ---')

        imagenes = ImagenVehiculo.objects.all()
        total = imagenes.count()
        migradas = 0
        errores = 0

        self.stdout.write(f'Total de imágenes a procesar: {total}')

        for i, img in enumerate(imagenes, 1):
            try:
                resultado = self._migrar_imagen(img, 'imagen', dry_run)
                if resultado:
                    migradas += 1
                    self.stdout.write(f'  [{i}/{total}] OK: {img.imagen.name}')
                else:
                    self.stdout.write(f'  [{i}/{total}] SKIP: {img.imagen.name} (ya está en R2 o no existe)')
            except Exception as e:
                errores += 1
                self.stdout.write(self.style.ERROR(f'  [{i}/{total}] ERROR: {img.imagen.name} - {str(e)}'))

        return migradas, errores

    def _migrar_imagenes_publicaciones(self, dry_run):
        """Migra imágenes de ImagenPublicacion a R2."""
        self.stdout.write('\n--- Migrando imágenes de PUBLICACIONES ---')

        imagenes = ImagenPublicacion.objects.all()
        total = imagenes.count()
        migradas = 0
        errores = 0

        self.stdout.write(f'Total de imágenes a procesar: {total}')

        for i, img in enumerate(imagenes, 1):
            try:
                resultado = self._migrar_imagen(img, 'imagen', dry_run)
                if resultado:
                    migradas += 1
                    self.stdout.write(f'  [{i}/{total}] OK: {img.imagen.name}')
                else:
                    self.stdout.write(f'  [{i}/{total}] SKIP: {img.imagen.name} (ya está en R2 o no existe)')
            except Exception as e:
                errores += 1
                self.stdout.write(self.style.ERROR(f'  [{i}/{total}] ERROR: {img.imagen.name} - {str(e)}'))

        return migradas, errores

    def _migrar_imagen(self, instance, field_name, dry_run):
        """
        Migra una imagen individual de almacenamiento local a R2.

        Retorna True si se migró, False si se saltó.
        """
        field = getattr(instance, field_name)

        if not field:
            return False

        # Ruta del archivo local
        local_path = os.path.join(settings.MEDIA_ROOT, field.name)

        # Verificar si el archivo local existe
        if not os.path.exists(local_path):
            # Puede que ya esté en R2
            return False

        if dry_run:
            return True

        # Leer el archivo local
        with open(local_path, 'rb') as f:
            file_content = f.read()

        # Guardar en R2 (el default_storage ahora es S3)
        # Usamos el mismo nombre/ruta para mantener consistencia
        saved_name = default_storage.save(field.name,
            __import__('django.core.files.base', fromlist=['ContentFile']).ContentFile(file_content)
        )

        # Actualizar el campo en el modelo (sin disparar la compresión)
        # Usamos update() para evitar el save() que comprimiría de nuevo
        instance.__class__.objects.filter(pk=instance.pk).update(**{field_name: saved_name})

        return True
