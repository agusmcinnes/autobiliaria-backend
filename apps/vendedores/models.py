from django.db import models
from django.utils.translation import gettext_lazy as _


class Vendedor(models.Model):
    """
    Modelo para gestionar vendedores (dueños de vehículos).
    """
    nombre = models.CharField(
        _('nombre'),
        max_length=100
    )
    apellido = models.CharField(
        _('apellido'),
        max_length=100
    )
    email = models.EmailField(
        _('email'),
        unique=True
    )
    direccion = models.CharField(
        _('dirección'),
        max_length=255
    )
    celular = models.CharField(
        _('celular'),
        max_length=20
    )
    dni = models.CharField(
        _('DNI'),
        max_length=20,
        unique=True
    )
    tiene_cartel = models.BooleanField(
        _('tiene cartel'),
        default=False
    )
    activo = models.BooleanField(
        _('activo'),
        default=True
    )
    comentarios = models.TextField(
        _('comentarios'),
        blank=True
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
        ordering = ['-created_at']
        verbose_name = _('Vendedor')
        verbose_name_plural = _('Vendedores')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"
