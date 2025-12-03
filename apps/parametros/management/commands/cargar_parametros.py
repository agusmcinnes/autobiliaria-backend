import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings

from apps.parametros.models import (
    Caja, Combustible, Condicion, Estado, Iva,
    Localidad, Moneda, Segmento, Marca, Modelo
)


class Command(BaseCommand):
    help = 'Carga los parámetros iniciales en la base de datos'

    # Datos fijos
    CAJAS = ['Automática', 'Manual']

    COMBUSTIBLES = ['Diesel', 'Electrico', 'GNC', 'HIBRIDO', 'Nafta']

    CONDICIONES = [
        'Buen estado',
        'CON DETALLES',
        'Con detalles de chapa',
        'CON DETALLES DE GRANIZO',
        'Excelente estado',
        'Muy buen estado',
    ]

    ESTADOS = ['0Km', 'NUEVO', 'Usado']

    IVAS = [
        'Consumidor Final',
        'Exento',
        'Inscripto',
        'No Inscripto',
        'Resp. Monotributo',
    ]

    LOCALIDADES = [
        'A Determinar',
        'Capital Federal',
        'Mar del Plata',
        'Olavarria',
        'San Fernando',
        'Tandil',
        'Ushuaia',
        'Zarate',
    ]

    MONEDAS = ['ARS', 'USD', 'EUROS', 'YENS']

    SEGMENTOS = [
        '(HB) 3 PUERTAS',
        '(HB) 5 puertas',
        '2 Puertas',
        '4X2',
        '4x4',
        '7 plazas',
        'Acoplado',
        'Agro',
        'Autos Competición',
        'Berlina',
        'Bus',
        'Cabriolet',
        'Camión',
        'Camioneta',
        'Colección',
        'Coupe',
        'CUATRICICLO',
        'Familiar',
        'Furgon',
        'Industria',
        'Minibus',
        'Monovolumen',
        'Monovolumen pequeño',
        'MOTO DE AGUA',
        'Moto/Cuatriciclo',
        'Motor Homes',
        'N/D',
        'Náutica',
        'Ómnibus',
        'Pick up cab. simple',
        'Pick up doble cabina',
        'Pick up space cabina',
        'REMOLQUES',
        'Rural',
        'Sedan 4p',
        'Semirremolque',
        'SUV',
        'TAXI',
        'Todo terreno',
        'Trailer',
        'Utilitario',
        'Van-Mini Van',
        'Vans',
    ]

    MARCAS = [
        'Acoplado', 'Alfa Romeo', 'Aston Martin', 'Audi', 'BAIC', 'Bajaj',
        'benelli', 'BETAMOTOR', 'BMOVE', 'BMW', 'Bonano', 'Camper', 'CAN-AM',
        'CASA RODANTE', 'CASILLA', 'Changan', 'Chery', 'Chevrolet', 'Chrysler',
        'Citroen', 'CORVEN', 'Daelim', 'Daewoo', 'Daihatsu', 'DFSK', 'Dodge',
        'DS', 'DUCATI', 'DUKE', 'Ferrari', 'Fiat', 'FOODTRUCK', 'Ford', 'Foton',
        'Geely', 'GMC', 'Great Wall', 'GUERRERO', 'GUZZI', 'HARLEY', 'Haval',
        'Honda', 'Hummer', 'Husqvarna', 'HYOSUNG', 'Hyundai', 'IKA', 'Isuzu',
        'Iveco', 'Jaguar', 'JAWA', 'Jeep', 'JOHN DEERE', 'KAWASAKI', 'KELLER',
        'Kia', 'KTM', 'Kymco', 'Lancia', 'Land Rover', 'LEXUS', 'Lifan', 'Lotus',
        'MACTRAIL', 'Mahindra', 'Mazda', 'Mercedes-Benz', 'Mini', 'Mitsubishi',
        'Mondial', 'Morris', 'MOTOMEL', 'Motorhome', 'MUSTANG', 'Nissan', 'Opel',
        'Peugeot', 'Piaggio', 'Plymouth', 'POLARIS', 'Pontiac', 'Porsche',
        'Proton', 'Ram', 'Rambler', 'Raptor', 'Rastrojero', 'RAUSER', 'Renault',
        'Rolls Royce', 'Rover', 'Royal Enfield', 'Scania', 'Scooter', 'SEA DOO',
        'Seat', 'SEMIRREMOLQUE', 'Shineray', 'SIAM', 'SIAMBRETTA', 'Smart',
        'ssangyong', 'Subaru', 'Suzuki', 'TIBO', 'Toyota', 'VESPA', 'Volkswagen',
        'Volvo', 'Yamaha', 'ZANELLA',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            help='Ruta al archivo CSV con marcas y modelos',
            default=None
        )

    def handle(self, *args, **options):
        self.stdout.write('Cargando parámetros...\n')

        # Cargar parámetros simples
        self._cargar_parametros_simples()

        # Cargar marcas
        self._cargar_marcas()

        # Cargar modelos desde CSV si se proporciona
        csv_path = options.get('csv')
        if csv_path:
            self._cargar_modelos_csv(csv_path)
        else:
            self.stdout.write(
                self.style.WARNING(
                    'No se proporcionó archivo CSV. '
                    'Usa --csv para cargar modelos desde archivo.'
                )
            )

        self.stdout.write(self.style.SUCCESS('\nParámetros cargados exitosamente!'))

    def _cargar_parametros_simples(self):
        """Carga todos los parámetros simples (sin relaciones)"""
        parametros = [
            (Caja, self.CAJAS, 'Cajas'),
            (Combustible, self.COMBUSTIBLES, 'Combustibles'),
            (Condicion, self.CONDICIONES, 'Condiciones'),
            (Estado, self.ESTADOS, 'Estados'),
            (Iva, self.IVAS, 'Condiciones IVA'),
            (Localidad, self.LOCALIDADES, 'Localidades'),
            (Moneda, self.MONEDAS, 'Monedas'),
            (Segmento, self.SEGMENTOS, 'Segmentos'),
        ]

        for modelo, valores, nombre in parametros:
            creados = 0
            for orden, valor in enumerate(valores, 1):
                obj, created = modelo.objects.get_or_create(
                    nombre=valor,
                    defaults={'orden': orden}
                )
                if created:
                    creados += 1
            self.stdout.write(f'  {nombre}: {creados} creados')

    def _cargar_marcas(self):
        """Carga las marcas de vehículos"""
        creados = 0
        for orden, nombre in enumerate(self.MARCAS, 1):
            obj, created = Marca.objects.get_or_create(
                nombre=nombre,
                defaults={'orden': orden}
            )
            if created:
                creados += 1
        self.stdout.write(f'  Marcas: {creados} creadas')

    def _cargar_modelos_csv(self, csv_path):
        """Carga modelos desde archivo CSV"""
        if not os.path.exists(csv_path):
            self.stdout.write(
                self.style.ERROR(f'Archivo no encontrado: {csv_path}')
            )
            return

        modelos_creados = 0
        marcas_no_encontradas = set()

        with open(csv_path, 'r', encoding='latin-1') as f:
            reader = csv.reader(f)

            for row in reader:
                if len(row) < 2:
                    continue

                # Formato: "Editar,Marca  Modelo"
                valor = row[1].strip()

                # Saltar encabezados
                if valor == 'Modelos' or not valor:
                    continue

                # Separar marca y modelo por doble espacio
                partes = valor.split('  ', 1)
                if len(partes) != 2:
                    continue

                marca_nombre = partes[0].strip()
                modelo_nombre = partes[1].strip()

                if not marca_nombre or not modelo_nombre:
                    continue

                # Buscar la marca
                try:
                    marca = Marca.objects.get(nombre__iexact=marca_nombre)
                except Marca.DoesNotExist:
                    # Intentar crear la marca si no existe
                    marca, _ = Marca.objects.get_or_create(
                        nombre=marca_nombre,
                        defaults={'orden': 999}
                    )
                    marcas_no_encontradas.add(marca_nombre)

                # Crear el modelo
                obj, created = Modelo.objects.get_or_create(
                    marca=marca,
                    nombre=modelo_nombre,
                    defaults={'orden': 0}
                )
                if created:
                    modelos_creados += 1

        self.stdout.write(f'  Modelos: {modelos_creados} creados desde CSV')

        if marcas_no_encontradas:
            self.stdout.write(
                self.style.WARNING(
                    f'  Marcas creadas automáticamente: {", ".join(sorted(marcas_no_encontradas))}'
                )
            )
