from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.urls import path
from django import forms

from .models import Vehiculo, ImagenVehiculo
from apps.parametros.models import Modelo


class VehiculoAdminForm(forms.ModelForm):
    """Form que filtra modelos segun la marca seleccionada."""

    class Meta:
        model = Vehiculo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Obtener marca_id del POST data o de la instancia existente
        marca_id = None

        if self.data.get('marca'):
            # POST request (guardando o cambiando)
            try:
                marca_id = int(self.data.get('marca'))
            except (ValueError, TypeError):
                pass
        elif self.instance and self.instance.pk:
            # Editando un vehiculo existente
            marca_id = self.instance.marca_id

        # Filtrar modelos segun la marca
        if marca_id:
            self.fields['modelo'].queryset = Modelo.objects.filter(
                marca_id=marca_id, activo=True
            ).order_by('nombre')
        else:
            # Sin marca seleccionada, mostrar vacio
            self.fields['modelo'].queryset = Modelo.objects.none()


class ImagenVehiculoInline(admin.TabularInline):
    model = ImagenVehiculo
    extra = 1
    max_num = 15
    fields = ('imagen', 'orden', 'es_principal')
    readonly_fields = ('created_at',)


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    form = VehiculoAdminForm
    list_display = (
        'patente',
        'titulo_display',
        'anio',
        'precio_display',
        'estado',
        'estado_venta',
        'mostrar_en_web',
        'publicado_en_ml',
        'created_at',
    )
    list_filter = (
        'vendido',
        'reservado',
        'mostrar_en_web',
        'publicado_en_ml',
        'marca',
        'estado',
        'combustible',
        'caja',
        'oportunidad',
        'deleted_at',
    )
    search_fields = (
        'patente',
        'marca__nombre',
        'modelo__nombre',
        'version',
        'vendedor_dueno__nombre',
        'vendedor_dueno__apellido',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'deleted_at',
        'cargado_por',
        'ml_item_id',
        'ml_estado',
        'ml_fecha_sync',
        'ml_error',
        'ml_permalink',
    )
    autocomplete_fields = (
        'marca',
        'segmento1',
        'segmento2',
        'combustible',
        'caja',
        'estado',
        'condicion',
        'moneda',
        'vendedor_dueno',
    )
    # modelo se filtra dinamicamente segun la marca seleccionada via AJAX
    inlines = [ImagenVehiculoInline]

    class Media:
        js = ('admin/js/vehiculo_admin.js',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'ajax/modelos/',
                self.admin_site.admin_view(self.ajax_modelos),
                name='vehiculo_ajax_modelos'
            ),
        ]
        return custom_urls + urls

    def ajax_modelos(self, request):
        """Endpoint AJAX para obtener modelos filtrados por marca."""
        marca_id = request.GET.get('marca_id')
        if not marca_id:
            return JsonResponse({'modelos': []})

        modelos = Modelo.objects.filter(
            marca_id=marca_id,
            activo=True
        ).order_by('nombre').values('id', 'nombre')

        return JsonResponse({'modelos': list(modelos)})

    fieldsets = (
        (_('Identificacion'), {
            'fields': ('patente', 'marca', 'modelo', 'version', 'anio', 'color')
        }),
        (_('Segmentos'), {
            'fields': ('segmento1', 'segmento2'),
            'classes': ('collapse',)
        }),
        (_('Caracteristicas'), {
            'fields': ('combustible', 'caja', 'estado', 'condicion', 'km', 'cant_duenos', 'vtv')
        }),
        (_('Precio'), {
            'fields': ('precio', 'moneda', 'porcentaje_financiacion')
        }),
        (_('Propietario'), {
            'fields': ('vendedor_dueno', 'cargado_por')
        }),
        (_('Estado de Venta'), {
            'fields': ('reservado', 'vendido', 'plan_ahorro', 'reventa')
        }),
        (_('Visibilidad Web'), {
            'fields': ('mostrar_en_web', 'destacar_en_web', 'oportunidad', 'oportunidad_grupo')
        }),
        (_('MercadoLibre'), {
            'fields': (
                'publicado_en_ml', 'ml_item_id', 'ml_estado',
                'ml_fecha_sync', 'ml_error', 'ml_permalink'
            ),
            'classes': ('collapse',)
        }),
        (_('Comentarios'), {
            'fields': ('comentario_carga',),
            'classes': ('collapse',)
        }),
        (_('Auditoria'), {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ('-created_at',)
    list_per_page = 25

    def titulo_display(self, obj):
        return obj.titulo
    titulo_display.short_description = _('Vehiculo')

    def precio_display(self, obj):
        return f"{obj.moneda.nombre} {obj.precio:,.2f}"
    precio_display.short_description = _('Precio')

    def estado_venta(self, obj):
        if obj.vendido:
            return format_html('<span style="color: green;">Vendido</span>')
        if obj.reservado:
            return format_html('<span style="color: orange;">Reservado</span>')
        if obj.is_deleted:
            return format_html('<span style="color: red;">Eliminado</span>')
        return format_html('<span style="color: blue;">Disponible</span>')
    estado_venta.short_description = _('Estado Venta')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.cargado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(ImagenVehiculo)
class ImagenVehiculoAdmin(admin.ModelAdmin):
    list_display = ('vehiculo', 'orden', 'es_principal', 'created_at')
    list_filter = ('es_principal', 'created_at')
    search_fields = ('vehiculo__patente',)
    readonly_fields = ('created_at',)
