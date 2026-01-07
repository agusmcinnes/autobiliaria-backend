from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class MLCredential(models.Model):
    """
    Almacena credenciales OAuth2 de Mercado Libre.
    Se vincula a un usuario del sistema para identificar quien autorizo.
    """
    user = models.OneToOneField(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='ml_credential',
        verbose_name=_('usuario')
    )
    ml_user_id = models.CharField(
        _('ID de usuario ML'),
        max_length=50,
        help_text=_('ID numerico del usuario en Mercado Libre')
    )
    ml_nickname = models.CharField(
        _('nickname ML'),
        max_length=100,
        blank=True,
        default='',
        help_text=_('Nombre de usuario en Mercado Libre')
    )
    access_token = models.TextField(
        _('access token'),
        help_text=_('Token de acceso OAuth2 (expira en 6 horas)')
    )
    refresh_token = models.TextField(
        _('refresh token'),
        help_text=_('Token para renovar (expira en 6 meses, un solo uso)')
    )
    expires_at = models.DateTimeField(
        _('expira en'),
        help_text=_('Fecha/hora de expiracion del access token')
    )
    scope = models.CharField(
        _('scope'),
        max_length=500,
        blank=True,
        default='',
        help_text=_('Permisos otorgados: read, write, offline_access')
    )
    is_active = models.BooleanField(
        _('activo'),
        default=True,
        help_text=_('False si los tokens fueron invalidados')
    )
    created_at = models.DateTimeField(
        _('fecha de conexion'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('ultima actualizacion'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Credencial de Mercado Libre')
        verbose_name_plural = _('Credenciales de Mercado Libre')

    def __str__(self):
        return f"ML Credential - {self.ml_nickname or self.ml_user_id}"

    @property
    def is_token_expired(self):
        """Verifica si el access token esta expirado."""
        return timezone.now() >= self.expires_at

    @property
    def needs_refresh(self):
        """Verifica si el token necesita renovarse (30 min antes de expirar)."""
        from datetime import timedelta
        buffer_time = self.expires_at - timedelta(minutes=30)
        return timezone.now() >= buffer_time


class MLPublicationStatus(models.TextChoices):
    """Estados posibles de una publicacion en ML."""
    ACTIVE = 'active', _('Activa')
    PAUSED = 'paused', _('Pausada')
    CLOSED = 'closed', _('Cerrada')
    UNDER_REVIEW = 'under_review', _('En revision')
    INACTIVE = 'inactive', _('Inactiva')


class MLPublication(models.Model):
    """
    Representa una publicacion de Mercado Libre.
    Puede estar vinculada a un vehiculo del sistema o no.
    """
    # Vinculacion con vehiculo local (opcional)
    vehiculo = models.ForeignKey(
        'vehiculos.Vehiculo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ml_publications',
        verbose_name=_('vehiculo vinculado'),
        help_text=_('Vehiculo del sistema asociado a esta publicacion')
    )

    # Datos de Mercado Libre
    ml_item_id = models.CharField(
        _('ID de item ML'),
        max_length=50,
        unique=True,
        help_text=_('ID unico de la publicacion en ML (ej: MLA123456789)')
    )
    ml_title = models.CharField(
        _('titulo en ML'),
        max_length=255,
        help_text=_('Titulo de la publicacion en Mercado Libre')
    )
    ml_status = models.CharField(
        _('estado en ML'),
        max_length=20,
        choices=MLPublicationStatus.choices,
        default=MLPublicationStatus.ACTIVE
    )
    ml_price = models.DecimalField(
        _('precio en ML'),
        max_digits=12,
        decimal_places=2,
        help_text=_('Precio publicado en Mercado Libre')
    )
    ml_currency = models.CharField(
        _('moneda'),
        max_length=3,
        default='ARS',
        help_text=_('Codigo de moneda (ARS, USD)')
    )
    ml_permalink = models.URLField(
        _('link de publicacion'),
        max_length=500,
        help_text=_('URL directa a la publicacion en ML')
    )
    ml_thumbnail = models.URLField(
        _('imagen principal'),
        max_length=500,
        blank=True,
        default='',
        help_text=_('URL de la imagen principal en ML')
    )
    ml_category_id = models.CharField(
        _('categoria ML'),
        max_length=20,
        blank=True,
        default='',
        help_text=_('ID de categoria en ML (ej: MLA1744)')
    )
    ml_listing_type = models.CharField(
        _('tipo de publicacion'),
        max_length=50,
        blank=True,
        default='',
        help_text=_('gold_special, gold_pro, gold, silver, etc.')
    )

    # Datos del vehiculo extraidos de ML (para matching)
    patente_ml = models.CharField(
        _('patente detectada'),
        max_length=10,
        blank=True,
        default='',
        db_index=True,
        help_text=_('Patente extraida del titulo/atributos para matching')
    )
    marca_ml = models.CharField(
        _('marca en ML'),
        max_length=100,
        blank=True,
        default=''
    )
    modelo_ml = models.CharField(
        _('modelo en ML'),
        max_length=100,
        blank=True,
        default=''
    )
    anio_ml = models.PositiveIntegerField(
        _('ano en ML'),
        null=True,
        blank=True
    )
    km_ml = models.PositiveIntegerField(
        _('km en ML'),
        null=True,
        blank=True
    )

    # Sincronizacion
    last_synced = models.DateTimeField(
        _('ultima sincronizacion'),
        help_text=_('Ultima vez que se sincronizo con ML')
    )
    sync_error = models.TextField(
        _('error de sincronizacion'),
        blank=True,
        default='',
        help_text=_('Ultimo error al sincronizar')
    )
    created_from_system = models.BooleanField(
        _('creada desde el sistema'),
        default=False,
        help_text=_('True si fue publicada desde autobiliaria, False si se importo')
    )

    # Auditoria
    created_at = models.DateTimeField(
        _('fecha de importacion'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('fecha de actualizacion'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Publicacion de Mercado Libre')
        verbose_name_plural = _('Publicaciones de Mercado Libre')
        ordering = ['-last_synced']
        indexes = [
            models.Index(fields=['ml_item_id']),
            models.Index(fields=['patente_ml']),
            models.Index(fields=['ml_status']),
            models.Index(fields=['vehiculo']),
        ]

    def __str__(self):
        return f"{self.ml_item_id} - {self.ml_title[:50]}"

    @property
    def is_linked(self):
        """Verifica si esta vinculada a un vehiculo del sistema."""
        return self.vehiculo is not None

    @property
    def is_active(self):
        """Verifica si la publicacion esta activa en ML."""
        return self.ml_status == MLPublicationStatus.ACTIVE


class MLSyncLog(models.Model):
    """
    Log de sincronizaciones con Mercado Libre.
    Permite tracking de operaciones y debugging.
    """
    class ActionType(models.TextChoices):
        IMPORT = 'import', _('Importar publicaciones')
        CREATE = 'create', _('Crear publicacion')
        UPDATE = 'update', _('Actualizar publicacion')
        PAUSE = 'pause', _('Pausar publicacion')
        ACTIVATE = 'activate', _('Activar publicacion')
        CLOSE = 'close', _('Cerrar publicacion')
        REFRESH_TOKEN = 'refresh_token', _('Renovar token')

    action = models.CharField(
        _('accion'),
        max_length=20,
        choices=ActionType.choices
    )
    publication = models.ForeignKey(
        MLPublication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sync_logs',
        verbose_name=_('publicacion')
    )
    vehiculo = models.ForeignKey(
        'vehiculos.Vehiculo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ml_sync_logs',
        verbose_name=_('vehiculo')
    )
    user = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ml_sync_logs',
        verbose_name=_('usuario')
    )
    request_data = models.JSONField(
        _('datos enviados'),
        null=True,
        blank=True,
        help_text=_('JSON enviado a la API de ML')
    )
    response_data = models.JSONField(
        _('respuesta'),
        null=True,
        blank=True,
        help_text=_('JSON recibido de la API de ML')
    )
    success = models.BooleanField(
        _('exitoso'),
        default=False
    )
    error_message = models.TextField(
        _('mensaje de error'),
        blank=True,
        default=''
    )
    created_at = models.DateTimeField(
        _('fecha'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Log de sincronizacion ML')
        verbose_name_plural = _('Logs de sincronizacion ML')
        ordering = ['-created_at']

    def __str__(self):
        status = 'OK' if self.success else 'ERROR'
        return f"{self.get_action_display()} - {status} - {self.created_at}"
