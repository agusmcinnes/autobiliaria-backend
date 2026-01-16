from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO
import sys
import os


class TipoVehiculo(models.TextChoices):
    """Tipos de vehiculos para publicaciones."""
    AUTO = 'auto', 'Auto'
    CAMIONETA = 'camioneta', 'Camioneta'
    CAMION = 'camion', 'Camion'
    MOTO = 'moto', 'Moto'


class EstadoPublicacion(models.TextChoices):
    """Estados de una publicacion."""
    PENDIENTE = 'pendiente', 'Pendiente'
    VISTA = 'vista', 'Vista'
    ELIMINADA = 'eliminada', 'Eliminada'


class PublicacionVehiculo(models.Model):
    """
    Publicaciones de vehiculos enviadas por clientes.
    Requieren aprobacion del staff antes de ser publicadas.
    """

    # ==========================================================================
    # DATOS DEL CLIENTE
    # ==========================================================================
    nombre = models.CharField(
        _('nombre'),
        max_length=100
    )
    email = models.EmailField(
        _('email')
    )
    telefono = models.CharField(
        _('telefono'),
        max_length=20
    )

    # ==========================================================================
    # DATOS DEL VEHICULO
    # ==========================================================================
    tipo_vehiculo = models.CharField(
        _('tipo de vehiculo'),
        max_length=15,
        choices=TipoVehiculo.choices,
        default=TipoVehiculo.AUTO
    )
    marca = models.ForeignKey(
        'parametros.Marca',
        on_delete=models.PROTECT,
        related_name='publicaciones',
        verbose_name=_('marca')
    )
    modelo = models.ForeignKey(
        'parametros.Modelo',
        on_delete=models.PROTECT,
        related_name='publicaciones',
        verbose_name=_('modelo')
    )
    anio = models.PositiveIntegerField(
        _('ano'),
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(2100)
        ]
    )
    km = models.PositiveIntegerField(
        _('kilometraje'),
        default=0
    )

    # ==========================================================================
    # GESTION (STAFF)
    # ==========================================================================
    estado = models.CharField(
        _('estado'),
        max_length=15,
        choices=EstadoPublicacion.choices,
        default=EstadoPublicacion.PENDIENTE
    )
    notas_staff = models.TextField(
        _('notas del staff'),
        blank=True,
        help_text=_('Notas internas para el equipo')
    )
    revisada_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        related_name='publicaciones_revisadas',
        verbose_name=_('revisada por'),
        null=True,
        blank=True
    )
    fecha_revision = models.DateTimeField(
        _('fecha de revision'),
        null=True,
        blank=True
    )

    # ==========================================================================
    # AUDITORIA
    # ==========================================================================
    created_at = models.DateTimeField(
        _('fecha de creacion'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('fecha de actualizacion'),
        auto_now=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Publicacion de Vehiculo')
        verbose_name_plural = _('Publicaciones de Vehiculos')
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.marca.nombre} {self.modelo.nombre}"


class ImagenPublicacion(models.Model):
    """
    Imagenes asociadas a una publicacion.
    Maximo 4 imagenes por publicacion.
    """
    publicacion = models.ForeignKey(
        PublicacionVehiculo,
        on_delete=models.CASCADE,
        related_name='imagenes',
        verbose_name=_('publicacion')
    )
    imagen = models.ImageField(
        _('imagen'),
        upload_to='publicaciones/%Y/%m/',
        help_text=_('Imagen del vehiculo')
    )
    orden = models.PositiveSmallIntegerField(
        _('orden'),
        default=0,
        help_text=_('Orden de visualizacion')
    )
    created_at = models.DateTimeField(
        _('fecha de creacion'),
        auto_now_add=True
    )

    class Meta:
        ordering = ['orden', 'created_at']
        verbose_name = _('Imagen de publicacion')
        verbose_name_plural = _('Imagenes de publicaciones')

    def __str__(self):
        return f"Imagen {self.orden} - {self.publicacion}"

    def save(self, *args, **kwargs):
        # Comprimir imagen antes de guardar (solo si es nueva o cambio)
        if self.imagen and hasattr(self.imagen, 'file'):
            self._compress_image()
        super().save(*args, **kwargs)

    def _compress_image(self):
        """Comprime y redimensiona la imagen a JPEG 80% calidad, max 1920x1080."""
        try:
            img = Image.open(self.imagen)

            # Convertir a RGB si es necesario (RGBA, P -> RGB para JPEG)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Redimensionar si es muy grande (mantiene aspect ratio)
            max_size = (1920, 1080)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Comprimir a JPEG 80%
            output = BytesIO()
            img.save(output, format='JPEG', quality=80, optimize=True)
            output.seek(0)

            # Generar nuevo nombre con extension .jpg
            original_name = os.path.splitext(self.imagen.name)[0]
            new_name = f"{original_name.split('/')[-1]}.jpg"

            # Reemplazar archivo
            self.imagen = InMemoryUploadedFile(
                output,
                'ImageField',
                new_name,
                'image/jpeg',
                sys.getsizeof(output),
                None
            )
        except Exception:
            # Si falla la compresion, guardar imagen original
            pass
