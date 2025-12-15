from rest_framework import serializers

from .models import PublicacionVehiculo, ImagenPublicacion
from apps.parametros.serializers import MarcaSerializer, ModeloSerializer


class ImagenPublicacionSerializer(serializers.ModelSerializer):
    """Serializer para imagenes de publicaciones."""
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = ImagenPublicacion
        fields = ['id', 'imagen', 'imagen_url', 'orden', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return None


class PublicacionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear publicaciones desde el frontend.
    Publico, no requiere autenticacion.
    """
    imagenes = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        max_length=4
    )

    class Meta:
        model = PublicacionVehiculo
        fields = [
            'id',
            'nombre',
            'email',
            'telefono',
            'tipo_vehiculo',
            'marca',
            'modelo',
            'anio',
            'km',
            'imagenes',
        ]
        read_only_fields = ['id']

    def validate(self, data):
        """Valida coherencia entre marca y modelo."""
        marca = data.get('marca')
        modelo = data.get('modelo')

        if marca and modelo:
            if modelo.marca_id != marca.id:
                raise serializers.ValidationError({
                    'modelo': f'El modelo "{modelo.nombre}" no pertenece a la marca "{marca.nombre}".'
                })

        return data

    def validate_imagenes(self, value):
        """Valida maximo 4 imagenes."""
        if len(value) > 4:
            raise serializers.ValidationError('Maximo 4 imagenes permitidas.')
        return value

    def create(self, validated_data):
        imagenes_data = validated_data.pop('imagenes', [])
        publicacion = PublicacionVehiculo.objects.create(**validated_data)

        for idx, imagen in enumerate(imagenes_data):
            ImagenPublicacion.objects.create(
                publicacion=publicacion,
                imagen=imagen,
                orden=idx
            )

        return publicacion


class PublicacionListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar publicaciones (staff).
    """
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
    modelo_nombre = serializers.CharField(source='modelo.nombre', read_only=True)
    tipo_vehiculo_display = serializers.CharField(source='get_tipo_vehiculo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    cant_imagenes = serializers.SerializerMethodField()

    class Meta:
        model = PublicacionVehiculo
        fields = [
            'id',
            'nombre',
            'email',
            'telefono',
            'tipo_vehiculo',
            'tipo_vehiculo_display',
            'marca',
            'marca_nombre',
            'modelo',
            'modelo_nombre',
            'anio',
            'km',
            'estado',
            'estado_display',
            'cant_imagenes',
            'created_at',
        ]

    def get_cant_imagenes(self, obj):
        return obj.imagenes.count()


class PublicacionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para detalle de publicacion (staff).
    """
    marca_detail = MarcaSerializer(source='marca', read_only=True)
    modelo_detail = ModeloSerializer(source='modelo', read_only=True)
    tipo_vehiculo_display = serializers.CharField(source='get_tipo_vehiculo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    revisada_por_nombre = serializers.CharField(source='revisada_por.get_full_name', read_only=True)
    imagenes = ImagenPublicacionSerializer(many=True, read_only=True)

    class Meta:
        model = PublicacionVehiculo
        fields = [
            'id',
            # Datos cliente
            'nombre',
            'email',
            'telefono',
            # Datos vehiculo
            'tipo_vehiculo',
            'tipo_vehiculo_display',
            'marca',
            'marca_detail',
            'modelo',
            'modelo_detail',
            'anio',
            'km',
            # Gestion
            'estado',
            'estado_display',
            'notas_staff',
            'revisada_por',
            'revisada_por_nombre',
            'fecha_revision',
            # Imagenes
            'imagenes',
            # Auditoria
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'nombre',
            'email',
            'telefono',
            'tipo_vehiculo',
            'marca',
            'modelo',
            'anio',
            'km',
            'revisada_por',
            'fecha_revision',
            'created_at',
            'updated_at',
        ]


class PublicacionUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar publicaciones (solo notas del staff).
    """
    class Meta:
        model = PublicacionVehiculo
        fields = ['notas_staff']
