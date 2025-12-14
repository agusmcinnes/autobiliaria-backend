from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Consulta


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'email',
        'tipo_badge',
        'vehiculo_link',
        'estado_badge',
        'created_at',
    )
    list_filter = (
        'tipo',
        'leida',
        'atendida',
        'created_at',
    )
    search_fields = (
        'nombre',
        'email',
        'telefono',
        'vehiculo__patente',
        'vehiculo__marca__nombre',
    )
    raw_id_fields = ('vehiculo',)

    def get_readonly_fields(self, request, obj=None):
        """Campos editables al crear, readonly al editar."""
        if obj:  # Editando
            return (
                'nombre', 'email', 'telefono', 'mensaje',
                'tipo', 'vehiculo', 'created_at', 'updated_at',
                'atendida_por', 'fecha_atendida',
            )
        # Creando
        return ('created_at', 'updated_at', 'atendida_por', 'fecha_atendida')

    fieldsets = (
        (_('Datos del Cliente'), {
            'fields': ('nombre', 'email', 'telefono', 'mensaje')
        }),
        (_('Consulta'), {
            'fields': ('tipo', 'vehiculo')
        }),
        (_('Gestion'), {
            'fields': ('leida', 'atendida', 'notas_staff')
        }),
        (_('Auditoria'), {
            'fields': (
                'atendida_por',
                'fecha_atendida',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'

    def tipo_badge(self, obj):
        color = '#3b82f6' if obj.tipo == 'consulta' else '#8b5cf6'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_tipo_display()
        )
    tipo_badge.short_description = _('Tipo')

    def vehiculo_link(self, obj):
        return format_html(
            '<a href="/admin/vehiculos/vehiculo/{}/change/">{}</a>',
            obj.vehiculo.id,
            obj.vehiculo.patente
        )
    vehiculo_link.short_description = _('Vehiculo')

    def estado_badge(self, obj):
        if obj.atendida:
            return format_html(
                '<span style="color: #22c55e; font-weight: bold;">Atendida</span>'
            )
        if obj.leida:
            return format_html(
                '<span style="color: #f59e0b; font-weight: bold;">Leida</span>'
            )
        return format_html(
            '<span style="color: #ef4444; font-weight: bold;">Nueva</span>'
        )
    estado_badge.short_description = _('Estado')

    def save_model(self, request, obj, form, change):
        """Asigna el usuario que atiende si se marca como atendida."""
        if change and obj.atendida and not obj.atendida_por:
            from django.utils import timezone
            obj.atendida_por = request.user
            obj.fecha_atendida = timezone.now()
        super().save_model(request, obj, form, change)
