"""
Management command para renovar el token de MercadoLibre proactivamente.

Uso:
    python manage.py refresh_ml_token

Este comando debe ejecutarse periódicamente con cron (cada 4 horas recomendado)
para mantener el token de ML siempre fresco y evitar desconexiones.
"""
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.integraciones.mercadolibre.models import MLCredential, MLSyncLog
from apps.integraciones.mercadolibre.services import MLClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Renueva el token de MercadoLibre si está próximo a expirar'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar renovación aunque el token no esté próximo a expirar',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)

        self.stdout.write(f"[{timezone.now()}] Iniciando verificación de token ML...")

        try:
            # Obtener credencial activa
            credential = MLCredential.objects.filter(is_active=True).first()

            if not credential:
                self.stdout.write(
                    self.style.WARNING('No hay credenciales activas de ML')
                )
                return

            self.stdout.write(f"Credencial encontrada: {credential.ml_nickname}")
            self.stdout.write(f"Token expira en: {credential.expires_at}")
            self.stdout.write(f"Necesita refresh: {credential.needs_refresh}")
            self.stdout.write(f"Token expirado: {credential.is_token_expired}")

            # Verificar si necesita renovación o si se fuerza
            if not credential.needs_refresh and not force:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Token todavía válido. Expira en: {credential.expires_at}'
                    )
                )
                return

            if force:
                self.stdout.write(self.style.WARNING('Forzando renovación de token...'))

            # Crear cliente (esto automáticamente renueva si es necesario)
            try:
                client = MLClient(credential)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creando cliente ML: {e}')
                )
                logger.error(f"Error en refresh_ml_token command: {e}")
                return

            # Refrescar desde BD para obtener nuevos valores
            credential.refresh_from_db()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Token renovado exitosamente. Nueva expiración: {credential.expires_at}'
                )
            )
            logger.info(f"Token ML renovado por cron. Expira: {credential.expires_at}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error inesperado: {e}')
            )
            logger.exception(f"Error inesperado en refresh_ml_token command: {e}")

            # Registrar error en log
            MLSyncLog.objects.create(
                action=MLSyncLog.ActionType.REFRESH_TOKEN,
                success=False,
                error_message=f"Error en comando refresh_ml_token: {str(e)}"
            )
