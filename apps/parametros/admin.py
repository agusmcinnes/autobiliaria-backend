from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    Caja, Combustible, Condicion, Estado, Iva,
    Localidad, Moneda, Segmento, Marca, Modelo
)


class ParametroBaseAdmin(admin.ModelAdmin):
    """Admin base para todos los parámetros"""
    list_display = ('nombre', 'orden', 'activo', 'created_at')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    list_editable = ('orden', 'activo')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('orden', 'nombre')


@admin.register(Caja)
class CajaAdmin(ParametroBaseAdmin):
    pass


@admin.register(Combustible)
class CombustibleAdmin(ParametroBaseAdmin):
    pass


@admin.register(Condicion)
class CondicionAdmin(ParametroBaseAdmin):
    pass


@admin.register(Estado)
class EstadoAdmin(ParametroBaseAdmin):
    pass


@admin.register(Iva)
class IvaAdmin(ParametroBaseAdmin):
    pass


@admin.register(Localidad)
class LocalidadAdmin(ParametroBaseAdmin):
    pass


@admin.register(Moneda)
class MonedaAdmin(ParametroBaseAdmin):
    pass


@admin.register(Segmento)
class SegmentoAdmin(ParametroBaseAdmin):
    pass


class ModeloInline(admin.TabularInline):
    model = Modelo
    extra = 1
    fields = ('nombre', 'orden', 'activo')


@admin.register(Marca)
class MarcaAdmin(ParametroBaseAdmin):
    inlines = [ModeloInline]


@admin.register(Modelo)
class ModeloAdmin(ParametroBaseAdmin):
    list_display = ('nombre', 'marca', 'orden', 'activo', 'created_at')
    list_filter = ('activo', 'marca')
    search_fields = ('nombre', 'marca__nombre')
    autocomplete_fields = ('marca',)

    def get_search_results(self, request, queryset, search_term):
        """
        Filtra modelos por marca cuando se usa desde VehiculoAdmin.
        El parametro 'marca' viene en el request cuando se selecciona una marca primero.
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        # Obtener marca_id del request (enviado por el JS del admin)
        marca_id = request.GET.get('marca')
        if marca_id:
            queryset = queryset.filter(marca_id=marca_id)

        return queryset, use_distinct
