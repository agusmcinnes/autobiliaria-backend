from django.contrib import admin
from .models import NotaDiaria


@admin.register(NotaDiaria)
class NotaDiariaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'autor', 'contenido_corto', 'created_at']
    list_filter = ['fecha', 'autor']
    search_fields = ['contenido', 'autor__first_name', 'autor__last_name']
    date_hierarchy = 'fecha'
    ordering = ['-fecha', '-created_at']

    def contenido_corto(self, obj):
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_corto.short_description = 'Contenido'
