from django.db import models
from django.utils.translation import gettext_lazy as _


class NotaDiaria(models.Model):
    """Notas diarias generales de la agencia."""

    contenido = models.TextField(_('contenido'))
    autor = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='notas_diarias',
        verbose_name=_('autor')
    )
    fecha = models.DateField(_('fecha'), db_index=True)
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = _('Nota Diaria')
        verbose_name_plural = _('Notas Diarias')
        indexes = [
            models.Index(fields=['fecha', 'created_at']),
        ]

    def __str__(self):
        return f"{self.fecha} - {self.autor}: {self.contenido[:50]}"
