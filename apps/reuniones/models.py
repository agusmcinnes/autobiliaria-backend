from django.db import models
from django.utils.translation import gettext_lazy as _


class Reunion(models.Model):
    """
    Modelo para gestionar reuniones/citas con compradores y vendedores.
    """

    class Ubicacion(models.TextChoices):
        FALUCHO = 'falucho', _('Falucho')
        PLAYA_GRANDE = 'playa_grande', _('Playa Grande')

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', _('Pendiente')
        COMPLETADA = 'completada', _('Completada')
        CANCELADA = 'cancelada', _('Cancelada')

    # ==========================================================================
    # CAMPOS PRINCIPALES
    # ==========================================================================
    fecha = models.DateField(
        _('fecha'),
        help_text=_('Fecha de la reunion')
    )
    hora = models.TimeField(
        _('hora'),
        help_text=_('Hora de la reunion')
    )
    ubicacion = models.CharField(
        _('ubicacion'),
        max_length=20,
        choices=Ubicacion.choices,
        default=Ubicacion.FALUCHO
    )

    # ==========================================================================
    # PARTICIPANTES
    # ==========================================================================
    coordinador = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='reuniones_coordinadas',
        verbose_name=_('coordinador'),
        help_text=_('Usuario que coordina la reunion')
    )
    comprador_nombre = models.CharField(
        _('nombre del comprador'),
        max_length=100
    )

    # Vendedor: sistema hibrido (FK o texto libre)
    vendedor = models.ForeignKey(
        'vendedores.Vendedor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reuniones',
        verbose_name=_('vendedor'),
        help_text=_('Vendedor registrado en el sistema')
    )
    vendedor_texto = models.CharField(
        _('vendedor (texto)'),
        max_length=100,
        blank=True,
        help_text=_('Nombre del vendedor si no esta registrado')
    )

    # ==========================================================================
    # VEHICULO RELACIONADO
    # ==========================================================================
    vehiculo = models.ForeignKey(
        'vehiculos.Vehiculo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reuniones',
        verbose_name=_('vehiculo'),
        help_text=_('Vehiculo relacionado con la reunion')
    )

    # ==========================================================================
    # ESTADO Y NOTAS
    # ==========================================================================
    estado = models.CharField(
        _('estado'),
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )
    notas = models.TextField(
        _('notas'),
        blank=True,
        help_text=_('Notas adicionales sobre la reunion')
    )

    # ==========================================================================
    # AUDITORIA
    # ==========================================================================
    creada_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='reuniones_creadas',
        verbose_name=_('creada por')
    )
    created_at = models.DateTimeField(
        _('fecha de creacion'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('fecha de actualizacion'),
        auto_now=True
    )

    class Meta:
        ordering = ['fecha', 'hora']
        verbose_name = _('Reunion')
        verbose_name_plural = _('Reuniones')
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['fecha', 'hora']),
            models.Index(fields=['ubicacion']),
            models.Index(fields=['estado']),
            models.Index(fields=['coordinador']),
            models.Index(fields=['vendedor']),
            models.Index(fields=['vehiculo']),
        ]

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.comprador_nombre} ({self.get_ubicacion_display()})"

    @property
    def vendedor_display(self):
        """Retorna el nombre del vendedor (FK o texto libre)."""
        if self.vendedor:
            return f"{self.vendedor.nombre} {self.vendedor.apellido}"
        return self.vendedor_texto or "Sin asignar"

    @property
    def vehiculo_display(self):
        """Retorna informacion del vehiculo si existe."""
        if self.vehiculo:
            return f"{self.vehiculo.titulo} ({self.vehiculo.patente})"
        return None

    def marcar_completada(self):
        """Marca la reunion como completada."""
        self.estado = self.Estado.COMPLETADA
        self.save(update_fields=['estado', 'updated_at'])

    def marcar_cancelada(self):
        """Marca la reunion como cancelada."""
        self.estado = self.Estado.CANCELADA
        self.save(update_fields=['estado', 'updated_at'])
