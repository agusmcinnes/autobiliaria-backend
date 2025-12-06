"""
Management command para importar vehiculos desde el sistema anterior.

Uso:
    python manage.py importar_vehiculos --csv /ruta/vehiculos.csv
    python manage.py importar_vehiculos --csv /ruta/vehiculos.csv --imagenes /ruta/imagenes/
    python manage.py importar_vehiculos --csv /ruta/vehiculos.csv --dry-run

Formato CSV esperado (primera fila con headers):
    patente,marca,modelo,anio,km,precio,moneda,combustible,caja,estado,condicion,
    vendedor_dni,color,version,vtv,plan_ahorro,mostrar_web,cant_duenos,comentarios

Nota: El vendedor debe existir previamente (crear manualmente o importar antes).
"""

import csv
import os
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.db import transaction
from django.utils import timezone

from apps.vehiculos.models import Vehiculo, ImagenVehiculo
from apps.vendedores.models import Vendedor
from apps.parametros.models import (
    Marca, Modelo, Combustible, Caja, Estado, Condicion, Moneda, Segmento
)
from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Importa vehiculos e imagenes desde el sistema anterior'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            required=True,
            help='Ruta al archivo CSV con datos de vehiculos'
        )
        parser.add_argument(
            '--imagenes',
            type=str,
            default=None,
            help='Ruta a la carpeta con imagenes (subcarpetas por patente)'
        )
        parser.add_argument(
            '--usuario',
            type=str,
            default=None,
            help='Email del usuario que carga los vehiculos (usa el primer admin si no se especifica)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular importacion sin guardar datos'
        )
        parser.add_argument(
            '--skip-errors',
            action='store_true',
            help='Continuar importacion aunque haya errores en algunas filas'
        )

    def handle(self, *args, **options):
        csv_path = options['csv']
        imagenes_path = options.get('imagenes')
        usuario_email = options.get('usuario')
        dry_run = options['dry_run']
        skip_errors = options['skip_errors']

        # Validar archivo CSV
        if not os.path.exists(csv_path):
            raise CommandError(f'Archivo CSV no encontrado: {csv_path}')

        # Validar carpeta de imagenes
        if imagenes_path and not os.path.exists(imagenes_path):
            raise CommandError(f'Carpeta de imagenes no encontrada: {imagenes_path}')

        # Obtener usuario
        usuario = self._get_usuario(usuario_email)
        self.stdout.write(f'Usuario para carga: {usuario.email}')

        # Contadores
        self.stats = {
            'total': 0,
            'creados': 0,
            'actualizados': 0,
            'imagenes': 0,
            'errores': [],
        }

        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write(f'Importando vehiculos desde: {csv_path}')
        if imagenes_path:
            self.stdout.write(f'Carpeta de imagenes: {imagenes_path}')
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: No se guardaran cambios'))
        self.stdout.write('=' * 60)
        self.stdout.write('')

        # Procesar CSV
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, start=2):
                    self.stats['total'] += 1

                    try:
                        if dry_run:
                            self._validar_row(row)
                            self.stats['creados'] += 1
                            self.stdout.write(f'  [OK] Fila {row_num}: {row.get("patente", "?")}')
                        else:
                            with transaction.atomic():
                                vehiculo, created = self._procesar_vehiculo(row, usuario)

                                if created:
                                    self.stats['creados'] += 1
                                    self.stdout.write(
                                        self.style.SUCCESS(f'  [CREADO] {vehiculo.patente}')
                                    )
                                else:
                                    self.stats['actualizados'] += 1
                                    self.stdout.write(f'  [ACTUALIZADO] {vehiculo.patente}')

                                # Importar imagenes
                                if imagenes_path:
                                    imgs = self._importar_imagenes(vehiculo, imagenes_path)
                                    if imgs > 0:
                                        self.stats['imagenes'] += imgs
                                        self.stdout.write(f'    -> {imgs} imagenes importadas')

                    except Exception as e:
                        error_msg = f'Fila {row_num} ({row.get("patente", "?")}): {str(e)}'
                        self.stats['errores'].append(error_msg)
                        self.stdout.write(self.style.ERROR(f'  [ERROR] {error_msg}'))

                        if not skip_errors:
                            raise CommandError(f'Error en fila {row_num}. Use --skip-errors para continuar.')

        except UnicodeDecodeError:
            raise CommandError('Error de codificacion. Asegurate que el CSV este en UTF-8.')

        # Resumen
        self._mostrar_resumen()

    def _get_usuario(self, email):
        """Obtiene el usuario para la carga."""
        if email:
            try:
                return Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                raise CommandError(f'Usuario no encontrado: {email}')

        # Buscar primer admin
        usuario = Usuario.objects.filter(rol='admin', is_active=True).first()
        if not usuario:
            usuario = Usuario.objects.filter(is_superuser=True, is_active=True).first()

        if not usuario:
            raise CommandError('No hay usuarios admin disponibles. Especifica uno con --usuario')

        return usuario

    def _validar_row(self, row):
        """Valida que una fila tenga los datos requeridos (para dry-run)."""
        campos_requeridos = [
            'patente', 'marca', 'modelo', 'anio', 'km',
            'precio', 'moneda', 'combustible', 'caja',
            'estado', 'condicion', 'vendedor_dni', 'color'
        ]

        for campo in campos_requeridos:
            if not row.get(campo, '').strip():
                raise ValueError(f'Campo requerido vacio: {campo}')

        # Validar que existan los parametros
        marca_nombre = row['marca'].strip()
        if not Marca.objects.filter(nombre__iexact=marca_nombre).exists():
            raise ValueError(f'Marca no encontrada: {marca_nombre}')

        modelo_nombre = row['modelo'].strip()
        if not Modelo.objects.filter(nombre__iexact=modelo_nombre).exists():
            raise ValueError(f'Modelo no encontrado: {modelo_nombre}')

        vendedor_dni = row['vendedor_dni'].strip()
        if not Vendedor.objects.filter(dni=vendedor_dni).exists():
            raise ValueError(f'Vendedor no encontrado (DNI: {vendedor_dni})')

    def _procesar_vehiculo(self, row, usuario):
        """Procesa una fila del CSV y crea/actualiza el vehiculo."""

        patente = row['patente'].strip().upper()

        # Buscar parametros
        marca = self._buscar_parametro(Marca, row['marca'], 'Marca')
        modelo = self._buscar_modelo(row['modelo'], marca)
        combustible = self._buscar_parametro(Combustible, row['combustible'], 'Combustible')
        caja = self._buscar_parametro(Caja, row['caja'], 'Caja')
        estado = self._buscar_parametro(Estado, row['estado'], 'Estado')
        condicion = self._buscar_parametro(Condicion, row['condicion'], 'Condicion')
        moneda = self._buscar_parametro(Moneda, row['moneda'], 'Moneda')

        # Buscar vendedor por DNI
        vendedor_dni = row['vendedor_dni'].strip()
        try:
            vendedor = Vendedor.objects.get(dni=vendedor_dni)
        except Vendedor.DoesNotExist:
            raise ValueError(f'Vendedor no encontrado con DNI: {vendedor_dni}')

        # Parsear campos numericos
        try:
            anio = int(row['anio'])
            km = int(row['km'])
            precio = Decimal(row['precio'].replace(',', '.'))
        except (ValueError, InvalidOperation) as e:
            raise ValueError(f'Error en campos numericos: {e}')

        cant_duenos = int(row.get('cant_duenos', 1) or 1)

        # Defaults del vehiculo
        defaults = {
            'marca': marca,
            'modelo': modelo,
            'combustible': combustible,
            'caja': caja,
            'estado': estado,
            'condicion': condicion,
            'moneda': moneda,
            'vendedor_dueno': vendedor,
            'cargado_por': usuario,
            'anio': anio,
            'km': km,
            'precio': precio,
            'color': row['color'].strip(),
            'version': row.get('version', '').strip(),
            'cant_duenos': cant_duenos,
            'vtv': self._parse_bool(row.get('vtv', 'false')),
            'plan_ahorro': self._parse_bool(row.get('plan_ahorro', 'false')),
            'mostrar_en_web': self._parse_bool(row.get('mostrar_web', 'true')),
            'comentario_carga': row.get('comentarios', '').strip(),
        }

        # Segmentos opcionales
        if row.get('segmento1'):
            try:
                defaults['segmento1'] = Segmento.objects.get(
                    nombre__iexact=row['segmento1'].strip()
                )
            except Segmento.DoesNotExist:
                pass  # Ignorar si no existe

        if row.get('segmento2'):
            try:
                defaults['segmento2'] = Segmento.objects.get(
                    nombre__iexact=row['segmento2'].strip()
                )
            except Segmento.DoesNotExist:
                pass

        # Crear o actualizar
        vehiculo, created = Vehiculo.objects.update_or_create(
            patente=patente,
            defaults=defaults
        )

        return vehiculo, created

    def _buscar_parametro(self, modelo_class, nombre, tipo):
        """Busca un parametro por nombre (case insensitive)."""
        nombre = nombre.strip()
        try:
            return modelo_class.objects.get(nombre__iexact=nombre)
        except modelo_class.DoesNotExist:
            raise ValueError(f'{tipo} no encontrado: {nombre}')
        except modelo_class.MultipleObjectsReturned:
            return modelo_class.objects.filter(nombre__iexact=nombre).first()

    def _buscar_modelo(self, nombre, marca):
        """Busca un modelo de vehiculo."""
        nombre = nombre.strip()
        try:
            return Modelo.objects.get(nombre__iexact=nombre, marca=marca)
        except Modelo.DoesNotExist:
            # Intentar sin filtrar por marca
            try:
                return Modelo.objects.get(nombre__iexact=nombre)
            except Modelo.DoesNotExist:
                raise ValueError(f'Modelo no encontrado: {nombre} (marca: {marca.nombre})')
            except Modelo.MultipleObjectsReturned:
                raise ValueError(f'Multiples modelos encontrados: {nombre}. Especifica la marca correcta.')

    def _parse_bool(self, value):
        """Parsea un valor booleano desde string."""
        if isinstance(value, bool):
            return value
        if not value:
            return False
        return str(value).lower().strip() in ('true', '1', 'yes', 'si', 's', 'x')

    def _importar_imagenes(self, vehiculo, imagenes_base_path):
        """Importa imagenes para un vehiculo desde una carpeta."""

        # Buscar carpeta con nombre de patente (mayusculas o minusculas)
        patente_folder = None
        for variant in [vehiculo.patente, vehiculo.patente.lower(), vehiculo.patente.upper()]:
            path = os.path.join(imagenes_base_path, variant)
            if os.path.exists(path) and os.path.isdir(path):
                patente_folder = path
                break

        if not patente_folder:
            return 0

        # Extensiones de imagen soportadas
        extensiones = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp')

        imagenes_importadas = 0
        imagenes_actuales = vehiculo.imagenes.count()

        for archivo in sorted(os.listdir(patente_folder)):
            if not archivo.lower().endswith(extensiones):
                continue

            # Limite de 15 imagenes por vehiculo
            if imagenes_actuales + imagenes_importadas >= 15:
                break

            ruta_imagen = os.path.join(patente_folder, archivo)

            try:
                with open(ruta_imagen, 'rb') as img_file:
                    imagen = ImagenVehiculo(
                        vehiculo=vehiculo,
                        orden=imagenes_importadas,
                        es_principal=(imagenes_importadas == 0 and imagenes_actuales == 0)
                    )
                    imagen.imagen.save(
                        archivo,
                        File(img_file),
                        save=True
                    )
                    imagenes_importadas += 1
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'    ! Error importando imagen {archivo}: {e}')
                )

        return imagenes_importadas

    def _mostrar_resumen(self):
        """Muestra resumen de la importacion."""
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('RESUMEN DE IMPORTACION')
        self.stdout.write('=' * 60)
        self.stdout.write(f'Total procesados: {self.stats["total"]}')
        self.stdout.write(
            self.style.SUCCESS(f'Vehiculos creados: {self.stats["creados"]}')
        )
        self.stdout.write(f'Vehiculos actualizados: {self.stats["actualizados"]}')
        self.stdout.write(f'Imagenes importadas: {self.stats["imagenes"]}')

        if self.stats['errores']:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR(f'Errores: {len(self.stats["errores"])}'))
            for i, error in enumerate(self.stats['errores'][:20], 1):
                self.stdout.write(f'  {i}. {error}')
            if len(self.stats['errores']) > 20:
                self.stdout.write(f'  ... y {len(self.stats["errores"]) - 20} errores mas')

        self.stdout.write('')
