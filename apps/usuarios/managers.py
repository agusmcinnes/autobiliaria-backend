from django.contrib.auth.models import BaseUserManager


class UsuarioManager(BaseUserManager):
    """
    Manager personalizado para el modelo Usuario.
    Usa email como identificador unico en lugar de username.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Crea y guarda un usuario regular con email y password.
        """
        if not email:
            raise ValueError('El email es obligatorio')

        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crea y guarda un superusuario con email y password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('rol', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
