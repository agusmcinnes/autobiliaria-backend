from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.uploadedfile import InMemoryUploadedFile
from decimal import Decimal
from PIL import Image
from io import BytesIO
import sys
import os


class TipoVehiculo(models.TextChoices):
    """Tipos de vehiculos disponibles."""
    AUTO = 'auto', 'Auto'
    CAMIONETA = 'camioneta', 'Camioneta'
    CAMION = 'camion', 'Camión'
    MOTO = 'moto', 'Moto'


class Vehiculo(models.Model):
    """
    Modelo principal para gestionar vehiculos del inventario.
    Incluye campos para integracion con MercadoLibre.
    """

    # ==========================================================================
    # RELACIONES - Parametros
    # ==========================================================================
    marca = models.ForeignKey(
        'parametros.Marca',
        on_delete=models.PROTECT,
        related_name='vehiculos',
        verbose_name=_('marca')
    )
    modelo = models.ForeignKey(
        'parametros.Modelo',
        on_delete=models.PROTECT,
        related_name='vehiculos',
        verbose_name=_('modelo')
    )
    segmento1 = models.ForeignKey(
        'parametros.Segmento',
        on_delete=models.SET_NULL,
        related_name='vehiculos_segmento1',
        verbose_name=_('segmento principal'),
        null=True,
        blank=True
    )
    segmento2 = models.ForeignKey(
        'parametros.Segmento',
        on_delete=models.SET_NULL,
        related_name='vehiculos_segmento2',
        verbose_name=_('segmento secundario'),
        null=True,
        blank=True
    )
    combustible = models.ForeignKey(
        'parametros.Combustible',
        on_delete=models.PROTECT,
        related_name='vehiculos',
        verbose_name=_('combustible')
    )
    caja = models.ForeignKey(
        'parametros.Caja',
        on_delete=models.PROTECT,
        related_name='vehiculos',
        verbose_name=_('caja')
    )
    estado = models.ForeignKey(
        'parametros.Estado',
        on_delete=models.PROTECT,
        related_name='vehiculos',
        verbose_name=_('estado')
    )
    condicion = models.ForeignKey(
        'parametros.Condicion',
        on_delete=models.PROTECT,
        related_name='vehiculos',
        verbose_name=_('condicion')
    )
    moneda = models.ForeignKey(
        'parametros.Moneda',
        on_delete=models.PROTECT,
        related_name='vehiculos',
        verbose_name=_('moneda')
    )

    # ==========================================================================
    # RELACIONES - Usuarios y Vendedores
    # ==========================================================================
    vendedor_dueno = models.ForeignKey(
        'vendedores.Vendedor',
        on_delete=models.PROTECT,
        related_name='vehiculos',
        verbose_name=_('vendedor/dueno')
    )
    cargado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='vehiculos_cargados',
        verbose_name=_('cargado por')
    )

    # ==========================================================================
    # CAMPOS GENERALES
    # ==========================================================================
    tipo_vehiculo = models.CharField(
        _('tipo de vehiculo'),
        max_length=15,
        choices=TipoVehiculo.choices,
        default=TipoVehiculo.AUTO
    )
    version = models.CharField(
        _('version'),
        max_length=100,
        blank=True,
        help_text=_('Ej: 1.6 SE, 2.0 TDI, Sport')
    )
    patente = models.CharField(
        _('patente'),
        max_length=10,
        unique=True,
        help_text=_('Patente unica del vehiculo')
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
    color = models.CharField(
        _('color'),
        max_length=50
    )
    precio = models.DecimalField(
        _('precio'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    porcentaje_financiacion = models.DecimalField(
        _('porcentaje de financiacion'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal('0')),
            MaxValueValidator(Decimal('100'))
        ],
        help_text=_('Porcentaje adicional por financiacion')
    )
    cant_duenos = models.PositiveSmallIntegerField(
        _('cantidad de duenos'),
        default=1,
        validators=[MinValueValidator(1)]
    )

    # ==========================================================================
    # CAMPOS BOOLEANOS - Estado del vehiculo
    # ==========================================================================
    vtv = models.BooleanField(
        _('VTV vigente'),
        default=False
    )
    plan_ahorro = models.BooleanField(
        _('plan de ahorro'),
        default=False
    )
    reservado = models.BooleanField(
        _('reservado'),
        default=False
    )
    vendido = models.BooleanField(
        _('vendido'),
        default=False
    )

    # ==========================================================================
    # CAMPOS BOOLEANOS - Visibilidad web
    # ==========================================================================
    mostrar_en_web = models.BooleanField(
        _('mostrar en web'),
        default=True
    )
    destacar_en_web = models.BooleanField(
        _('destacar en web'),
        default=False
    )
    oportunidad = models.BooleanField(
        _('oportunidad'),
        default=False,
        help_text=_('Marcar como oportunidad de compra')
    )
    oportunidad_grupo = models.BooleanField(
        _('oportunidad de grupo'),
        default=False
    )
    reventa = models.BooleanField(
        _('reventa'),
        default=False,
        help_text=_('Es un vehiculo para reventa')
    )

    # ==========================================================================
    # MERCADOLIBRE - Tracking de sincronizacion
    # ==========================================================================
    publicado_en_ml = models.BooleanField(
        _('publicado en MercadoLibre'),
        default=False
    )
    ml_item_id = models.CharField(
        _('ID MercadoLibre'),
        max_length=50,
        null=True,
        blank=True,
        unique=True,
        help_text=_('ID del item en MercadoLibre (MLA...)')
    )
    ml_estado = models.CharField(
        _('estado en MercadoLibre'),
        max_length=20,
        blank=True,
        default='',
        help_text=_('active, paused, closed, etc.')
    )
    ml_fecha_sync = models.DateTimeField(
        _('ultima sincronizacion ML'),
        null=True,
        blank=True
    )
    ml_error = models.TextField(
        _('ultimo error ML'),
        blank=True,
        default='',
        help_text=_('Ultimo error de sincronizacion con ML')
    )
    ml_permalink = models.URLField(
        _('URL en MercadoLibre'),
        max_length=500,
        blank=True,
        default='',
        help_text=_('Link directo a la publicacion')
    )

    # ==========================================================================
    # OTROS CAMPOS
    # ==========================================================================
    comentario_carga = models.TextField(
        _('comentarios de carga'),
        blank=True,
        help_text=_('Notas internas sobre el vehiculo')
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
    deleted_at = models.DateTimeField(
        _('fecha de eliminacion'),
        null=True,
        blank=True,
        help_text=_('Soft delete - null significa activo')
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Vehiculo')
        verbose_name_plural = _('Vehiculos')
        indexes = [
            models.Index(fields=['patente']),
            models.Index(fields=['marca', 'modelo']),
            models.Index(fields=['vendido', 'reservado']),
            models.Index(fields=['mostrar_en_web']),
            models.Index(fields=['ml_item_id']),
            models.Index(fields=['deleted_at']),
        ]

    def __str__(self):
        return f"{self.marca.nombre} {self.modelo.nombre} ({self.patente})"

    @property
    def titulo(self):
        """Genera titulo para listados y ML."""
        base = f"{self.marca.nombre} {self.modelo.nombre}"
        if self.version:
            base = f"{base} {self.version}"
        return f"{base} {self.anio}"

    @property
    def precio_financiado(self):
        """Calcula precio con financiacion si aplica."""
        if self.porcentaje_financiacion:
            adicional = self.precio * (self.porcentaje_financiacion / 100)
            return self.precio + adicional
        return self.precio

    @property
    def is_deleted(self):
        """Verifica si el vehiculo fue eliminado (soft delete)."""
        return self.deleted_at is not None

    @property
    def disponible(self):
        """Verifica si el vehiculo esta disponible para venta."""
        return not self.vendido and not self.reservado and not self.is_deleted

    def soft_delete(self):
        """Marca el vehiculo como eliminado."""
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at', 'updated_at'])

    def restore(self):
        """Restaura un vehiculo eliminado."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at', 'updated_at'])


class ImagenVehiculo(models.Model):
    """
    Imagenes asociadas a un vehiculo.
    Maximo 15 imagenes por vehiculo.
    """
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='imagenes',
        verbose_name=_('vehiculo')
    )
    imagen = models.ImageField(
        _('imagen'),
        upload_to='vehiculos/%Y/%m/',
        help_text=_('Imagen del vehiculo')
    )
    orden = models.PositiveSmallIntegerField(
        _('orden'),
        default=0,
        help_text=_('Orden de visualizacion')
    )
    es_principal = models.BooleanField(
        _('es imagen principal'),
        default=False
    )
    created_at = models.DateTimeField(
        _('fecha de creacion'),
        auto_now_add=True
    )

    class Meta:
        ordering = ['orden', 'created_at']
        verbose_name = _('Imagen de vehiculo')
        verbose_name_plural = _('Imagenes de vehiculos')

    def __str__(self):
        return f"Imagen {self.orden} - {self.vehiculo.patente}"

    def save(self, *args, **kwargs):
        # Comprimir imagen antes de guardar (solo si es nueva o cambio)
        if self.imagen and hasattr(self.imagen, 'file'):
            self._compress_image()

        # Si es principal, quitar el flag de otras imagenes del mismo vehiculo
        if self.es_principal:
            ImagenVehiculo.objects.filter(
                vehiculo=self.vehiculo,
                es_principal=True
            ).exclude(pk=self.pk).update(es_principal=False)
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
