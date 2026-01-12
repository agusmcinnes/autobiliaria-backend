from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Reserva, FormaPago, GastoAdministrativo, NotaReserva


class FormaPagoInline(admin.TabularInline):
    model = FormaPago
    extra = 0
    fields = ('tipo', 'monto', 'notas', 'created_at')
    readonly_fields = ('created_at',)


class GastoAdministrativoInline(admin.TabularInline):
    model = GastoAdministrativo
    extra = 0
    fields = ('concepto', 'monto', 'tipo_cuenta', 'fecha')
    readonly_fields = ('created_at',)


class NotaReservaInline(admin.TabularInline):
    model = NotaReserva
    extra = 0
    fields = ('contenido', 'autor', 'created_at')
    readonly_fields = ('autor', 'created_at')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        'numero_reserva',
        'tipo_operacion_color',
        'estado_display',
        'cliente',
        'vehiculo_display',
        'precio_venta',
        'vendedor_1',
        'fecha_entrega_pactada',
        'created_at',
    )
    list_filter = (
        'tipo_operacion',
        'estado',
        'entregado',
        'transferido',
        'vendedor_1',
        'created_at',
    )
    search_fields = (
        'numero_reserva',
        'cliente__nombre',
        'cliente__apellido',
        'cliente__dni_cuit',
        'vehiculo__patente',
        'dominio',
    )
    readonly_fields = (
        'numero_reserva',
        'creada_por',
        'created_at',
        'updated_at',
        'total_operacion_display',
    )
    autocomplete_fields = (
        'vehiculo',
        'cliente',
        'propietario_anterior',
        'vendedor_1',
        'vendedor_2',
        'gestor_supervisor',
        'moneda',
    )
    inlines = [FormaPagoInline, GastoAdministrativoInline, NotaReservaInline]

    fieldsets = (
        (_('Identificacion'), {
            'fields': ('numero_reserva', 'tipo_operacion', 'estado')
        }),
        (_('Vehiculo y Cliente'), {
            'fields': ('vehiculo', 'cliente')
        }),
        (_('Datos Usados'), {
            'fields': ('dominio', 'propietario_anterior'),
            'classes': ('collapse',),
        }),
        (_('Datos 0KM'), {
            'fields': ('numero_chasis', 'proveedor', 'costo_patentamiento', 'costo_flete'),
            'classes': ('collapse',),
        }),
        (_('Costos'), {
            'fields': (
                'precio_venta', 'moneda',
                'comision_vendedor', 'comision_comprador',
                'gestion_credito', 'gastos_transferencia', 'impuestos',
                'otros_gastos', 'descripcion_otros_gastos',
                'observaciones_costos',
                'total_operacion_display',
            )
        }),
        (_('Administrativo'), {
            'fields': (
                'fecha_entrega_pactada', 'vendedor_1', 'vendedor_2',
                'gestor_supervisor'
            )
        }),
        (_('Estado de Operacion'), {
            'fields': ('entregado', 'transferido', 'a_reestructurar')
        }),
        (_('Auditoria'), {
            'fields': ('creada_por', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ('-created_at',)
    list_per_page = 25

    def tipo_operacion_color(self, obj):
        colores = {
            'used': '#3B82F6',      # Azul
            'new': '#EF4444',       # Rojo
            'external': '#F59E0B',  # Amarillo
        }
        color = colores.get(obj.tipo_operacion, '#9E9E9E')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_tipo_operacion_display()
        )
    tipo_operacion_color.short_description = _('Tipo')

    def estado_display(self, obj):
        colores = {
            'pending': '#F59E0B',
            'delivered': '#10B981',
            'cancelled': '#EF4444',
            'cancelled_lost_deposit': '#991B1B',
            'restructuring': '#8B5CF6',
        }
        color = colores.get(obj.estado, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: 500;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_display.short_description = _('Estado')

    def vehiculo_display(self, obj):
        if obj.vehiculo:
            return obj.vehiculo.titulo
        return '-'
    vehiculo_display.short_description = _('Vehiculo')

    def total_operacion_display(self, obj):
        return f"${obj.total_operacion:,.2f}"
    total_operacion_display.short_description = _('Total Operacion')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creada_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(FormaPago)
class FormaPagoAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'tipo', 'monto', 'created_at')
    list_filter = ('tipo', 'created_at')
    search_fields = ('reserva__numero_reserva',)
    ordering = ('-created_at',)


@admin.register(GastoAdministrativo)
class GastoAdministrativoAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'concepto', 'monto', 'tipo_cuenta', 'fecha')
    list_filter = ('tipo_cuenta', 'created_at')
    search_fields = ('reserva__numero_reserva', 'concepto')
    ordering = ('-created_at',)


@admin.register(NotaReserva)
class NotaReservaAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'autor', 'contenido_truncado', 'created_at')
    list_filter = ('autor', 'created_at')
    search_fields = ('reserva__numero_reserva', 'contenido')
    ordering = ('-created_at',)

    def contenido_truncado(self, obj):
        if len(obj.contenido) > 50:
            return f"{obj.contenido[:50]}..."
        return obj.contenido
    contenido_truncado.short_description = _('Contenido')
