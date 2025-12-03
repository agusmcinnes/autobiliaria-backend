from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UsuarioManager


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado.
    Usa email como identificador principal en lugar de username.
    """

    class Rol(models.TextChoices):
        ADMIN = 'admin', _('Administrador')
        STAFF = 'staff', _('Staff')

    # Email como identificador principal
    email = models.EmailField(
        _('email'),
        unique=True,
        error_messages={
            'unique': _('Ya existe un usuario con este email.'),
        },
    )

    # Username opcional (para mostrar en UI)
    username = models.CharField(
        _('nombre de usuario'),
        max_length=150,
        blank=True,
        null=True,
    )

    # Campos adicionales
    first_name = models.CharField(_('nombre'), max_length=150)
    last_name = models.CharField(_('apellido'), max_length=150)
    rol = models.CharField(
        _('rol'),
        max_length=10,
        choices=Rol.choices,
        default=Rol.STAFF,
    )

    # Campos de auditoria
    created_at = models.DateTimeField(_('fecha de creacion'), auto_now_add=True)
    updated_at = models.DateTimeField(_('fecha de actualizacion'), auto_now=True)

    # Configuracion del modelo
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UsuarioManager()

    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Retorna nombre completo del usuario."""
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        """Retorna el nombre corto del usuario."""
        return self.first_name

    @property
    def is_admin(self):
        """Verifica si el usuario es administrador."""
        return self.rol == self.Rol.ADMIN or self.is_superuser

    def save(self, *args, **kwargs):
        """Asigna is_staff=True para que puedan acceder al admin."""
        if self.rol in [self.Rol.ADMIN, self.Rol.STAFF]:
            self.is_staff = True
        super().save(*args, **kwargs)
