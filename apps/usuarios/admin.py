from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuracion del admin para el modelo Usuario.
    """

    # Campos a mostrar en la lista
    list_display = ('email', 'username', 'first_name', 'last_name', 'rol', 'is_active', 'created_at')
    list_filter = ('rol', 'is_active', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-created_at',)

    # Campos en el formulario de edicion
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informacion personal'), {'fields': ('username', 'first_name', 'last_name')}),
        (_('Rol y permisos'), {
            'fields': ('rol', 'is_active', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Fechas importantes'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    # Campos en el formulario de creacion
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'rol'),
        }),
    )

    # Campos de solo lectura
    readonly_fields = ('created_at', 'updated_at', 'last_login')
