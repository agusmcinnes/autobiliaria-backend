from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Vendedor


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'apellido',
        'dni',
        'email',
        'celular',
        'tiene_cartel',
        'activo',
        'created_at',
    )
    list_filter = (
        'activo',
        'tiene_cartel',
        'created_at',
    )
    search_fields = (
        'nombre',
        'apellido',
        'dni',
        'email',
        'celular',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    fieldsets = (
        (_('Información Personal'), {
            'fields': ('nombre', 'apellido', 'dni')
        }),
        (_('Contacto'), {
            'fields': ('email', 'celular', 'direccion')
        }),
        (_('Estado'), {
            'fields': ('activo', 'tiene_cartel')
        }),
        (_('Comentarios'), {
            'fields': ('comentarios',),
            'classes': ('collapse',)
        }),
        (_('Auditoría'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)
