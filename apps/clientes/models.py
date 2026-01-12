from django.db import models
from django.utils.translation import gettext_lazy as _


class Cliente(models.Model):
    """
    Modelo para gestionar clientes/compradores de vehiculos.
    Permite reutilizar datos de clientes en multiples reservas.
    """
    nombre = models.CharField(
        _('nombre'),
        max_length=100
    )
    apellido = models.CharField(
        _('apellido'),
        max_length=100
    )
    dni_cuit = models.CharField(
        _('DNI/CUIT'),
        max_length=20,
        unique=True,
        help_text=_('Documento unico de identificacion')
    )
    email = models.EmailField(
        _('email'),
        blank=True,
        default=''
    )
    telefono = models.CharField(
        _('telefono'),
        max_length=50
    )
    domicilio = models.CharField(
        _('domicilio'),
        max_length=300,
        blank=True,
        default=''
    )
    notas = models.TextField(
        _('notas'),
        blank=True,
        help_text=_('Notas internas sobre el cliente')
    )
    activo = models.BooleanField(
        _('activo'),
        default=True
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
        ordering = ['-created_at']
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        indexes = [
            models.Index(fields=['dni_cuit']),
            models.Index(fields=['apellido', 'nombre']),
        ]

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.dni_cuit})"

    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"
