from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import PublicacionVehiculo, ImagenPublicacion, EstadoPublicacion


class ImagenPublicacionInline(admin.TabularInline):
    model = ImagenPublicacion
    extra = 0
    max_num = 4
    fields = ('imagen', 'orden')
    readonly_fields = ('created_at',)


@admin.register(PublicacionVehiculo)
class PublicacionVehiculoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'email',
        'vehiculo_display',
        'estado_badge',
        'cant_imagenes',
        'created_at',
    )
    list_filter = (
        'estado',
        'tipo_vehiculo',
        'marca',
        'created_at',
    )
    search_fields = (
        'nombre',
        'email',
        'telefono',
        'marca__nombre',
        'modelo__nombre',
    )
    raw_id_fields = ('marca', 'modelo')
    readonly_fields = (
        'revisada_por',
        'fecha_revision',
        'created_at',
        'updated_at',
    )
    inlines = [ImagenPublicacionInline]

    def get_readonly_fields(self, request, obj=None):
        """Campos editables al crear, readonly al editar."""
        if obj:  # Editando
            return (
                'nombre', 'email', 'telefono',
                'tipo_vehiculo', 'marca', 'modelo', 'anio', 'km',
                'revisada_por', 'fecha_revision',
                'created_at', 'updated_at',
            )
        # Creando
        return ('revisada_por', 'fecha_revision', 'created_at', 'updated_at')

    fieldsets = (
        (_('Datos del Cliente'), {
            'fields': ('nombre', 'email', 'telefono')
        }),
        (_('Datos del Vehiculo'), {
            'fields': ('tipo_vehiculo', 'marca', 'modelo', 'anio', 'km')
        }),
        (_('Gestion'), {
            'fields': ('estado', 'notas_staff')
        }),
        (_('Auditoria'), {
            'fields': (
                'revisada_por',
                'fecha_revision',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'

    actions = ['marcar_como_vistas', 'marcar_como_eliminadas']

    def vehiculo_display(self, obj):
        return f"{obj.marca.nombre} {obj.modelo.nombre} {obj.anio}"
    vehiculo_display.short_description = _('Vehiculo')

    def estado_badge(self, obj):
        colors = {
            'pendiente': '#f59e0b',  # Naranja
            'vista': '#3b82f6',      # Azul
            'eliminada': '#ef4444',  # Rojo
        }
        color = colors.get(obj.estado, '#6b7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = _('Estado')

    def cant_imagenes(self, obj):
        return obj.imagenes.count()
    cant_imagenes.short_description = _('Imagenes')

    def save_model(self, request, obj, form, change):
        """Asigna el usuario que revisa si cambia el estado."""
        if change:
            old_obj = PublicacionVehiculo.objects.get(pk=obj.pk)
            if old_obj.estado != obj.estado and obj.estado != EstadoPublicacion.PENDIENTE:
                obj.revisada_por = request.user
                obj.fecha_revision = timezone.now()
        super().save_model(request, obj, form, change)

    @admin.action(description=_('Marcar como vistas'))
    def marcar_como_vistas(self, request, queryset):
        count = queryset.update(
            estado=EstadoPublicacion.VISTA,
            revisada_por=request.user,
            fecha_revision=timezone.now()
        )
        self.message_user(request, f'{count} publicaciones marcadas como vistas.')

    @admin.action(description=_('Marcar como eliminadas'))
    def marcar_como_eliminadas(self, request, queryset):
        count = queryset.update(
            estado=EstadoPublicacion.ELIMINADA,
            revisada_por=request.user,
            fecha_revision=timezone.now()
        )
        self.message_user(request, f'{count} publicaciones marcadas como eliminadas.')


@admin.register(ImagenPublicacion)
class ImagenPublicacionAdmin(admin.ModelAdmin):
    list_display = ('publicacion', 'orden', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('publicacion__nombre', 'publicacion__email')
    readonly_fields = ('created_at',)
