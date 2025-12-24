from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Reunion


@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    list_display = [
        'fecha',
        'hora',
        'ubicacion',
        'coordinador',
        'comprador_nombre',
        'vendedor_display',
        'vehiculo',
        'estado',
        'created_at',
    ]
    list_filter = [
        'fecha',
        'ubicacion',
        'estado',
        'coordinador',
    ]
    search_fields = [
        'comprador_nombre',
        'vendedor_texto',
        'vendedor__nombre',
        'vendedor__apellido',
        'vehiculo__patente',
        'notas',
    ]
    date_hierarchy = 'fecha'
    ordering = ['-fecha', '-hora']
    readonly_fields = ['created_at', 'updated_at', 'creada_por']

    fieldsets = (
        (_('Fecha y Lugar'), {
            'fields': ('fecha', 'hora', 'ubicacion')
        }),
        (_('Participantes'), {
            'fields': ('coordinador', 'comprador_nombre', 'vendedor', 'vendedor_texto')
        }),
        (_('Vehiculo'), {
            'fields': ('vehiculo',)
        }),
        (_('Estado'), {
            'fields': ('estado', 'notas')
        }),
        (_('Auditoria'), {
            'fields': ('creada_por', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creada_por = request.user
        super().save_model(request, obj, form, change)

    def vendedor_display(self, obj):
        return obj.vendedor_display
    vendedor_display.short_description = _('Vendedor')
