from django.contrib import admin
from django.utils.html import format_html
from .models import MLCredential, MLPublication, MLSyncLog


@admin.register(MLCredential)
class MLCredentialAdmin(admin.ModelAdmin):
    list_display = [
        'ml_nickname',
        'ml_user_id',
        'is_active',
        'is_token_expired_display',
        'expires_at',
        'created_at',
    ]
    list_filter = ['is_active']
    search_fields = ['ml_user_id', 'ml_nickname']
    readonly_fields = [
        'user',
        'ml_user_id',
        'ml_nickname',
        'access_token',
        'refresh_token',
        'expires_at',
        'scope',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Usuario', {
            'fields': ('user', 'ml_user_id', 'ml_nickname')
        }),
        ('Estado', {
            'fields': ('is_active', 'expires_at', 'scope')
        }),
        ('Tokens (solo lectura)', {
            'fields': ('access_token', 'refresh_token'),
            'classes': ('collapse',),
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def is_token_expired_display(self, obj):
        if obj.is_token_expired:
            return format_html('<span style="color: red;">Expirado</span>')
        return format_html('<span style="color: green;">Valido</span>')
    is_token_expired_display.short_description = 'Token'


@admin.register(MLPublication)
class MLPublicationAdmin(admin.ModelAdmin):
    list_display = [
        'ml_item_id',
        'ml_title_short',
        'ml_status_display',
        'ml_price',
        'vehiculo_link',
        'patente_ml',
        'last_synced',
    ]
    list_filter = ['ml_status', 'created_from_system']
    search_fields = ['ml_item_id', 'ml_title', 'patente_ml', 'marca_ml', 'modelo_ml']
    raw_id_fields = ['vehiculo']
    readonly_fields = [
        'ml_item_id',
        'ml_title',
        'ml_status',
        'ml_price',
        'ml_currency',
        'ml_permalink',
        'ml_thumbnail',
        'ml_category_id',
        'ml_listing_type',
        'patente_ml',
        'marca_ml',
        'modelo_ml',
        'anio_ml',
        'km_ml',
        'last_synced',
        'sync_error',
        'created_from_system',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Mercado Libre', {
            'fields': (
                'ml_item_id',
                'ml_title',
                'ml_status',
                'ml_price',
                'ml_currency',
                'ml_permalink',
                'ml_thumbnail',
            )
        }),
        ('Datos del Vehiculo (ML)', {
            'fields': (
                'patente_ml',
                'marca_ml',
                'modelo_ml',
                'anio_ml',
                'km_ml',
            )
        }),
        ('Vinculacion', {
            'fields': ('vehiculo',)
        }),
        ('Sincronizacion', {
            'fields': (
                'last_synced',
                'sync_error',
                'created_from_system',
            )
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def ml_title_short(self, obj):
        return obj.ml_title[:50] + '...' if len(obj.ml_title) > 50 else obj.ml_title
    ml_title_short.short_description = 'Titulo'

    def ml_status_display(self, obj):
        colors = {
            'active': 'green',
            'paused': 'orange',
            'closed': 'red',
        }
        color = colors.get(obj.ml_status, 'gray')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_ml_status_display()
        )
    ml_status_display.short_description = 'Estado'

    def vehiculo_link(self, obj):
        if obj.vehiculo:
            return format_html(
                '<a href="/admin/vehiculos/vehiculo/{}/change/">{}</a>',
                obj.vehiculo.id,
                obj.vehiculo.patente
            )
        return '-'
    vehiculo_link.short_description = 'Vehiculo'


@admin.register(MLSyncLog)
class MLSyncLogAdmin(admin.ModelAdmin):
    list_display = [
        'created_at',
        'action',
        'success_display',
        'publication',
        'vehiculo',
        'user',
    ]
    list_filter = ['action', 'success', 'created_at']
    search_fields = ['publication__ml_item_id', 'vehiculo__patente', 'user__email']
    readonly_fields = [
        'action',
        'publication',
        'vehiculo',
        'user',
        'request_data',
        'response_data',
        'success',
        'error_message',
        'created_at',
    ]
    date_hierarchy = 'created_at'

    def success_display(self, obj):
        if obj.success:
            return format_html('<span style="color: green;">OK</span>')
        return format_html('<span style="color: red;">Error</span>')
    success_display.short_description = 'Resultado'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
