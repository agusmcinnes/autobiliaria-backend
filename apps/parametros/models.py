from django.db import models
from django.utils.translation import gettext_lazy as _


class ParametroBase(models.Model):
    """
    Modelo base abstracto para todos los parámetros/catálogos.
    """
    nombre = models.CharField(
        _('nombre'),
        max_length=100
    )
    activo = models.BooleanField(
        _('activo'),
        default=True
    )
    orden = models.PositiveIntegerField(
        _('orden'),
        default=0,
        help_text=_('Orden de visualización')
    )
    created_at = models.DateTimeField(
        _('fecha de creación'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('fecha de actualización'),
        auto_now=True
    )

    class Meta:
        abstract = True
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class Caja(ParametroBase):
    """Tipos de caja de cambios: Automática, Manual"""

    class Meta(ParametroBase.Meta):
        verbose_name = _('Caja')
        verbose_name_plural = _('Cajas')


class Combustible(ParametroBase):
    """Tipos de combustible: Diesel, Nafta, GNC, etc."""

    class Meta(ParametroBase.Meta):
        verbose_name = _('Combustible')
        verbose_name_plural = _('Combustibles')


class Condicion(ParametroBase):
    """Estado/condición del vehículo: Excelente, Buen estado, etc."""

    class Meta(ParametroBase.Meta):
        verbose_name = _('Condición')
        verbose_name_plural = _('Condiciones')


class Estado(ParametroBase):
    """Estado comercial: 0Km, Usado, Nuevo"""

    class Meta(ParametroBase.Meta):
        verbose_name = _('Estado')
        verbose_name_plural = _('Estados')


class Iva(ParametroBase):
    """Condición ante IVA: Consumidor Final, Inscripto, etc."""

    class Meta(ParametroBase.Meta):
        verbose_name = _('Condición IVA')
        verbose_name_plural = _('Condiciones IVA')


class Localidad(ParametroBase):
    """Localidades/ciudades disponibles"""

    class Meta(ParametroBase.Meta):
        verbose_name = _('Localidad')
        verbose_name_plural = _('Localidades')


class Moneda(ParametroBase):
    """Monedas: ARS, USD, EUROS, YENS"""

    class Meta(ParametroBase.Meta):
        verbose_name = _('Moneda')
        verbose_name_plural = _('Monedas')


class Segmento(ParametroBase):
    """Segmentos de vehículos: SUV, Sedan, Pick up, etc."""

    class Meta(ParametroBase.Meta):
        verbose_name = _('Segmento')
        verbose_name_plural = _('Segmentos')


class Marca(ParametroBase):
    """Marcas de vehículos: Ford, Chevrolet, Toyota, etc."""

    class Meta(ParametroBase.Meta):
        verbose_name = _('Marca')
        verbose_name_plural = _('Marcas')


class Modelo(ParametroBase):
    """Modelos de vehículos, relacionados a una marca"""
    marca = models.ForeignKey(
        Marca,
        on_delete=models.CASCADE,
        related_name='modelos',
        verbose_name=_('marca')
    )

    class Meta(ParametroBase.Meta):
        verbose_name = _('Modelo')
        verbose_name_plural = _('Modelos')

    def __str__(self):
        return f"{self.marca.nombre} {self.nombre}"
