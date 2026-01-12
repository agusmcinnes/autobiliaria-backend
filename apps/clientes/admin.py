from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'dni_cuit',
        'apellido',
        'nombre',
        'telefono',
        'email',
        'activo',
        'created_at',
    )
    list_filter = ('activo', 'created_at')
    search_fields = ('nombre', 'apellido', 'dni_cuit', 'email', 'telefono')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25

    fieldsets = (
        (_('Datos Personales'), {
            'fields': ('nombre', 'apellido', 'dni_cuit')
        }),
        (_('Contacto'), {
            'fields': ('email', 'telefono', 'domicilio')
        }),
        (_('Informacion Adicional'), {
            'fields': ('notas', 'activo'),
            'classes': ('collapse',)
        }),
        (_('Auditoria'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
