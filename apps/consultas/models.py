from django.db import models
from django.utils.translation import gettext_lazy as _


class Consulta(models.Model):
    """
    Modelo para gestionar consultas y reservas de clientes sobre vehiculos.
    """

    class TipoConsulta(models.TextChoices):
        CONSULTA = 'consulta', _('Consulta')
        RESERVA = 'reserva', _('Reserva')

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
    mensaje = models.TextField(
        _('mensaje')
    )

    # ==========================================================================
    # TIPO Y VEHICULO
    # ==========================================================================
    tipo = models.CharField(
        _('tipo'),
        max_length=10,
        choices=TipoConsulta.choices,
        default=TipoConsulta.CONSULTA
    )
    vehiculo = models.ForeignKey(
        'vehiculos.Vehiculo',
        on_delete=models.CASCADE,
        related_name='consultas',
        verbose_name=_('vehiculo')
    )

    # ==========================================================================
    # GESTION (STAFF)
    # ==========================================================================
    leida = models.BooleanField(
        _('leida'),
        default=False
    )
    atendida = models.BooleanField(
        _('atendida'),
        default=False
    )
    notas_staff = models.TextField(
        _('notas del staff'),
        blank=True,
        help_text=_('Notas internas para seguimiento')
    )
    atendida_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultas_atendidas',
        verbose_name=_('atendida por')
    )
    fecha_atendida = models.DateTimeField(
        _('fecha atendida'),
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
        verbose_name = _('Consulta')
        verbose_name_plural = _('Consultas')
        indexes = [
            models.Index(fields=['vehiculo']),
            models.Index(fields=['tipo']),
            models.Index(fields=['leida', 'atendida']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.nombre} - {self.vehiculo.patente}"

    def marcar_leida(self):
        """Marca la consulta como leida."""
        if not self.leida:
            self.leida = True
            self.save(update_fields=['leida', 'updated_at'])

    def marcar_atendida(self, usuario=None):
        """Marca la consulta como atendida."""
        from django.utils import timezone
        self.atendida = True
        self.leida = True
        self.atendida_por = usuario
        self.fecha_atendida = timezone.now()
        self.save(update_fields=[
            'atendida', 'leida', 'atendida_por',
            'fecha_atendida', 'updated_at'
        ])
