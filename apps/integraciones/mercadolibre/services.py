"""
Servicios para la integracion con Mercado Libre API.
"""
import re
import logging
import requests
from datetime import timedelta
from decimal import Decimal
from typing import Optional, Dict, List, Any, Tuple

from django.conf import settings
from django.utils import timezone

from .models import MLCredential, MLPublication, MLSyncLog, MLPublicationStatus

logger = logging.getLogger(__name__)


class MLAPIError(Exception):
    """Error de la API de Mercado Libre."""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class MLClient:
    """
    Cliente para la API de Mercado Libre.
    Maneja autenticacion, renovacion de tokens y llamadas a la API.
    """
    BASE_URL = "https://api.mercadolibre.com"
    AUTH_URL = "https://auth.mercadolibre.com.ar"

    # Categorias de vehiculos en Argentina (MLA)
    VEHICLE_CATEGORIES = {
        'auto': 'MLA1744',       # Autos y Camionetas
        'camioneta': 'MLA1744',  # Autos y Camionetas
        'moto': 'MLA1763',       # Motos
        'camion': 'MLA1753',     # Camiones
    }

    def __init__(self, credential: MLCredential):
        """
        Inicializa el cliente con credenciales.
        Renueva el token automaticamente si es necesario.
        """
        self.credential = credential
        self._ensure_valid_token()

    def _ensure_valid_token(self) -> None:
        """Verifica y renueva el token si es necesario."""
        if self.credential.needs_refresh:
            self._refresh_token()

    def _refresh_token(self) -> bool:
        """
        Renueva el access_token usando el refresh_token.
        Retorna True si fue exitoso.
        """
        logger.info(f"Iniciando refresh de token ML para user {self.credential.ml_user_id}")
        logger.info(f"Token actual expira en: {self.credential.expires_at}")

        try:
            response = requests.post(
                f"{self.BASE_URL}/oauth/token",
                data={
                    'grant_type': 'refresh_token',
                    'client_id': settings.ML_APP_ID,
                    'client_secret': settings.ML_SECRET_KEY,
                    'refresh_token': self.credential.refresh_token,
                }
            )

            if response.status_code == 200:
                data = response.json()
                old_expires = self.credential.expires_at
                self.credential.access_token = data['access_token']
                self.credential.refresh_token = data['refresh_token']
                self.credential.expires_at = timezone.now() + timedelta(seconds=data['expires_in'])
                self.credential.save()

                # Log exitoso
                MLSyncLog.objects.create(
                    action=MLSyncLog.ActionType.REFRESH_TOKEN,
                    success=True,
                    response_data={
                        'old_expires_at': str(old_expires),
                        'new_expires_at': str(self.credential.expires_at),
                        'expires_in': data['expires_in'],
                    }
                )
                logger.info(f"Token ML renovado exitosamente para user {self.credential.ml_user_id}")
                logger.info(f"Nuevo token expira en: {self.credential.expires_at}")
                return True
            else:
                error_data = response.json() if response.content else {}
                error_msg = f"HTTP {response.status_code}: {error_data.get('message', 'Unknown error')}"

                # Errores específicos de ML que indican token inválido/revocado
                error_code = error_data.get('error', '')
                if error_code in ['invalid_grant', 'invalid_token'] or response.status_code == 400:
                    logger.error(f"Token de ML invalidado/revocado. Se requiere reconexión manual.")
                    self.credential.is_active = False
                    self.credential.save()
                else:
                    # Para otros errores, no desactivar inmediatamente
                    logger.warning(f"Error temporal renovando token ML, no se desactiva: {error_msg}")

                MLSyncLog.objects.create(
                    action=MLSyncLog.ActionType.REFRESH_TOKEN,
                    success=False,
                    response_data=error_data,
                    error_message=error_msg
                )
                logger.error(f"Error renovando token ML: {error_data}")
                return False

        except requests.RequestException as e:
            logger.exception(f"Error de conexion renovando token ML: {e}")
            # No desactivar por errores de red temporales
            MLSyncLog.objects.create(
                action=MLSyncLog.ActionType.REFRESH_TOKEN,
                success=False,
                error_message=f"Error de conexión: {str(e)}"
            )
            return False

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Realiza una peticion a la API de ML.
        Maneja autenticacion y errores comunes.
        """
        if not self.credential.is_active:
            raise MLAPIError("Credenciales de ML inactivas. Debe reconectar la cuenta.")

        self._ensure_valid_token()

        url = f"{self.BASE_URL}{endpoint}"
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.credential.access_token}'

        try:
            response = requests.request(method, url, headers=headers, **kwargs)

            if response.status_code == 401:
                # Token invalido, intentar renovar una vez
                if self._refresh_token():
                    headers['Authorization'] = f'Bearer {self.credential.access_token}'
                    response = requests.request(method, url, headers=headers, **kwargs)
                else:
                    raise MLAPIError("Token expirado y no se pudo renovar", 401)

            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                raise MLAPIError(
                    error_data.get('message', f'Error HTTP {response.status_code}'),
                    response.status_code,
                    error_data
                )

            return response.json() if response.content else {}

        except requests.RequestException as e:
            raise MLAPIError(f"Error de conexion: {str(e)}")

    # =========================================================================
    # METODOS DE USUARIO
    # =========================================================================

    def get_user_info(self) -> Dict:
        """Obtiene informacion del usuario de ML."""
        return self._request('GET', f'/users/{self.credential.ml_user_id}')

    def get_user_quota(self) -> List[Dict]:
        """
        Obtiene el quota de publicaciones del usuario por marketplace.
        Retorna lista con quota por site_id (MLA, MLB, etc).
        """
        return self._request('GET', '/marketplace/users/cap')

    # =========================================================================
    # METODOS DE ITEMS/PUBLICACIONES
    # =========================================================================

    def get_user_items(self, status: str = None, offset: int = 0, limit: int = 50) -> Dict:
        """
        Obtiene las publicaciones del usuario.

        Args:
            status: Filtrar por estado (active, paused, closed)
            offset: Para paginacion
            limit: Cantidad por pagina (max 50)
        """
        params = {
            'offset': offset,
            'limit': min(limit, 50),
        }
        if status:
            params['status'] = status

        return self._request(
            'GET',
            f'/users/{self.credential.ml_user_id}/items/search',
            params=params
        )

    def get_all_user_items(self, status: str = None) -> List[str]:
        """
        Obtiene TODOS los IDs de items del usuario (maneja paginacion).
        Retorna lista de IDs.
        """
        all_items = []
        offset = 0
        limit = 50

        while True:
            result = self.get_user_items(status=status, offset=offset, limit=limit)
            items = result.get('results', [])
            all_items.extend(items)

            total = result.get('paging', {}).get('total', 0)
            if offset + limit >= total:
                break
            offset += limit

        return all_items

    def get_item_details(self, item_id: str) -> Dict:
        """Obtiene detalles completos de un item."""
        return self._request('GET', f'/items/{item_id}')

    def get_items_details_batch(self, item_ids: List[str]) -> List[Dict]:
        """
        Obtiene detalles de multiples items en una sola llamada.
        ML permite hasta 20 items por llamada.
        """
        results = []
        # Procesar en batches de 20
        for i in range(0, len(item_ids), 20):
            batch = item_ids[i:i+20]
            ids_param = ','.join(batch)
            response = self._request('GET', '/items', params={'ids': ids_param})
            if isinstance(response, list):
                results.extend(response)
        return results

    def create_item(self, payload: Dict) -> Dict:
        """
        Crea una nueva publicacion en ML.

        Args:
            payload: Datos de la publicacion segun formato ML
        """
        return self._request('POST', '/items', json=payload)

    def update_item(self, item_id: str, payload: Dict) -> Dict:
        """Actualiza una publicacion existente."""
        return self._request('PUT', f'/items/{item_id}', json=payload)

    def update_item_status(self, item_id: str, status: str) -> Dict:
        """
        Cambia el estado de una publicacion.

        Args:
            item_id: ID de la publicacion
            status: 'active', 'paused', o 'closed'
        """
        return self._request('PUT', f'/items/{item_id}', json={'status': status})

    def pause_item(self, item_id: str) -> Dict:
        """Pausa una publicacion."""
        return self.update_item_status(item_id, 'paused')

    def activate_item(self, item_id: str) -> Dict:
        """Reactiva una publicacion pausada."""
        return self.update_item_status(item_id, 'active')

    def close_item(self, item_id: str) -> Dict:
        """Cierra definitivamente una publicacion."""
        return self.update_item_status(item_id, 'closed')

    # =========================================================================
    # METODOS DE CATEGORIAS Y ATRIBUTOS
    # =========================================================================

    def get_category_attributes(self, category_id: str) -> Dict:
        """Obtiene los atributos requeridos/opcionales de una categoria."""
        return self._request('GET', f'/categories/{category_id}/attributes')

    def predict_category(self, title: str) -> Dict:
        """
        Predice la categoria basada en el titulo.
        Util para obtener categoria_id correcta.
        """
        return self._request(
            'GET',
            '/sites/MLA/domain_discovery/search',
            params={'q': title}
        )


class MLSyncService:
    """
    Servicio de sincronizacion entre autobiliaria y Mercado Libre.
    Maneja importacion, matching y publicacion de vehiculos.
    """

    def __init__(self, credential: MLCredential):
        self.credential = credential
        self.client = MLClient(credential)

    # =========================================================================
    # EXTRACCION DE PATENTE
    # =========================================================================

    @staticmethod
    def extract_patente(title: str, attributes: List[Dict] = None) -> str:
        """
        Extrae patente del titulo o atributos de ML.
        Soporta formato viejo (ABC123) y nuevo (AB123CD).
        """
        attributes = attributes or []

        # Buscar en atributos primero
        for attr in attributes:
            attr_id = attr.get('id', '').upper()
            if attr_id in ['LICENSE_PLATE', 'VEHICLE_LICENSE_PLATE', 'PLATE']:
                value = attr.get('value_name', '') or attr.get('value_id', '')
                if value:
                    return MLSyncService.normalize_patente(value)

        # Patrones de patente argentina
        patterns = [
            r'\b([A-Z]{2}\s?\d{3}\s?[A-Z]{2})\b',  # Nuevo: AA 123 BB o AA123BB
            r'\b([A-Z]{3}\s?\d{3})\b',              # Viejo: ABC 123 o ABC123
        ]

        title_upper = title.upper()
        for pattern in patterns:
            match = re.search(pattern, title_upper)
            if match:
                return MLSyncService.normalize_patente(match.group(1))

        return ''

    @staticmethod
    def normalize_patente(patente: str) -> str:
        """Normaliza patente: sin espacios ni guiones, mayusculas."""
        return re.sub(r'[\s\-]', '', patente).upper()

    @staticmethod
    def extract_vehicle_attributes(item: Dict) -> Dict:
        """
        Extrae atributos del vehiculo desde los datos de ML.
        """
        attributes = item.get('attributes', [])
        result = {
            'marca': '',
            'modelo': '',
            'anio': None,
            'km': None,
        }

        attr_mapping = {
            'BRAND': 'marca',
            'MODEL': 'modelo',
            'VEHICLE_YEAR': 'anio',
            'KILOMETERS': 'km',
        }

        for attr in attributes:
            attr_id = attr.get('id', '')
            value = attr.get('value_name', '')

            if attr_id in attr_mapping:
                key = attr_mapping[attr_id]
                if key in ['anio', 'km']:
                    # Convertir a numero
                    try:
                        result[key] = int(re.sub(r'\D', '', str(value)))
                    except (ValueError, TypeError):
                        pass
                else:
                    result[key] = value

        return result

    # =========================================================================
    # QUOTA DE PUBLICACIONES
    # =========================================================================

    def get_quota(self, site_id: str = 'MLA') -> Dict:
        """
        Obtiene información de quota de publicaciones para un marketplace.

        Args:
            site_id: ID del marketplace (MLA=Argentina, MLB=Brasil, etc.)

        Returns:
            Dict con quota, total_items, available y site_id
        """
        try:
            data = self.client.get_user_quota()
            # data es una lista, buscar el marketplace solicitado
            for site_quota in data:
                if site_quota.get('site_id') == site_id:
                    quota = site_quota.get('quota', 0)
                    total_items = site_quota.get('total_items', 0)
                    return {
                        'quota': quota,
                        'total_items': total_items,
                        'available': quota - total_items,
                        'site_id': site_id
                    }
            # Si no se encuentra el site_id, retornar valores por defecto
            return {
                'quota': 0,
                'total_items': 0,
                'available': 0,
                'site_id': site_id
            }
        except MLAPIError as e:
            logger.error(f"Error obteniendo quota de ML: {e}")
            raise

    # =========================================================================
    # SINCRONIZACION DE PUBLICACIONES
    # =========================================================================

    def sync_publications(self, user=None) -> Tuple[int, int, int]:
        """
        Sincroniza todas las publicaciones de ML con el sistema.

        Returns:
            Tuple (importadas, actualizadas, vinculadas)
        """
        from apps.vehiculos.models import Vehiculo

        imported = 0
        updated = 0
        linked = 0

        try:
            # Obtener todos los IDs de items
            item_ids = self.client.get_all_user_items()
            logger.info(f"Encontradas {len(item_ids)} publicaciones en ML")

            # Obtener detalles en batches
            items_details = self.client.get_items_details_batch(item_ids)

            for item_data in items_details:
                # Algunos items vienen con estructura {code, body}
                if 'body' in item_data:
                    item = item_data.get('body', {})
                else:
                    item = item_data

                if not item or not item.get('id'):
                    continue

                try:
                    publication, created = self._sync_single_item(item, user)
                    if created:
                        imported += 1
                    else:
                        updated += 1

                    # Intentar vincular si no esta vinculada
                    if not publication.vehiculo and publication.patente_ml:
                        vehiculo = Vehiculo.objects.filter(
                            patente__iexact=publication.patente_ml,
                            deleted_at__isnull=True
                        ).first()
                        if vehiculo:
                            publication.vehiculo = vehiculo
                            publication.save(update_fields=['vehiculo', 'updated_at'])
                            linked += 1
                            logger.info(f"Publicacion {publication.ml_item_id} vinculada a vehiculo {vehiculo.patente}")

                except Exception as e:
                    logger.error(f"Error procesando item {item.get('id')}: {e}")
                    continue

            # Log de sincronizacion
            MLSyncLog.objects.create(
                action=MLSyncLog.ActionType.IMPORT,
                user=user,
                success=True,
                response_data={
                    'imported': imported,
                    'updated': updated,
                    'linked': linked,
                    'total_items': len(item_ids),
                }
            )

        except MLAPIError as e:
            MLSyncLog.objects.create(
                action=MLSyncLog.ActionType.IMPORT,
                user=user,
                success=False,
                error_message=str(e),
                response_data=e.response_data
            )
            raise

        return imported, updated, linked

    def _sync_single_item(self, item: Dict, user=None) -> Tuple[MLPublication, bool]:
        """
        Sincroniza un item individual.

        Returns:
            Tuple (publication, created)
        """
        ml_item_id = item.get('id')
        attributes = self.extract_vehicle_attributes(item)
        patente = self.extract_patente(item.get('title', ''), item.get('attributes', []))

        defaults = {
            'ml_title': item.get('title', '')[:255],
            'ml_status': item.get('status', 'active'),
            'ml_price': Decimal(str(item.get('price', 0))),
            'ml_currency': item.get('currency_id', 'ARS'),
            'ml_permalink': item.get('permalink', ''),
            'ml_thumbnail': item.get('thumbnail', ''),
            'ml_category_id': item.get('category_id', ''),
            'ml_listing_type': item.get('listing_type_id', ''),
            'patente_ml': patente,
            'marca_ml': attributes.get('marca', ''),
            'modelo_ml': attributes.get('modelo', ''),
            'anio_ml': attributes.get('anio'),
            'km_ml': attributes.get('km'),
            'last_synced': timezone.now(),
            'sync_error': '',
        }

        publication, created = MLPublication.objects.update_or_create(
            ml_item_id=ml_item_id,
            defaults=defaults
        )

        return publication, created

    # =========================================================================
    # PUBLICACION DE VEHICULOS
    # =========================================================================

    def build_item_payload(self, vehiculo, custom_title: str = None, doors: str = None) -> Dict:
        """
        Construye el payload para crear una publicacion en ML desde un vehiculo.

        Args:
            vehiculo: Instancia de Vehiculo
            custom_title: Titulo personalizado opcional
            doors: Cantidad de puertas (opcional, default segun tipo)
        """
        # Obtener URLs de imagenes (max 15)
        pictures = []
        for img in vehiculo.imagenes.order_by('orden')[:15]:
            if img.imagen:
                # Asegurar URL absoluta
                img_url = img.imagen.url
                if not img_url.startswith('http'):
                    img_url = f"{settings.MEDIA_BASE_URL}{img_url}"
                pictures.append({'source': img_url})

        # Mapear tipo de vehiculo a categoria ML
        category_id = MLClient.VEHICLE_CATEGORIES.get(
            vehiculo.tipo_vehiculo,
            'MLA1744'  # Default: Autos
        )

        # Determinar condicion
        condition = 'new' if vehiculo.estado.nombre == '0Km' else 'used'

        # Mapear transmision
        transmission_map = {
            'automatica': 'Automática',
            'manual': 'Manual',
            'secuencial': 'Secuencial',
        }
        transmission = transmission_map.get(
            vehiculo.caja.nombre.lower(),
            vehiculo.caja.nombre
        )

        # Usar titulo personalizado o generar uno por defecto
        title = custom_title if custom_title else vehiculo.titulo

        # Agregar patente en titulo si no esta
        if vehiculo.patente.upper() not in title.upper():
            title = f"{title} - {vehiculo.patente}"

        # Determinar cantidad de puertas (usar parametro o default segun tipo)
        if not doors:
            doors_map = {
                'auto': '4',
                'camioneta': '4',
                'camion': '2',
                'moto': '0',
            }
            doors = doors_map.get(vehiculo.tipo_vehiculo, '4')

        # Version/Trim del vehiculo
        trim = vehiculo.version if vehiculo.version else f"{vehiculo.marca.nombre} {vehiculo.modelo.nombre}"

        payload = {
            "title": title,
            "category_id": category_id,
            "price": float(vehiculo.precio),
            "currency_id": vehiculo.moneda.codigo if hasattr(vehiculo.moneda, 'codigo') else 'ARS',
            "available_quantity": 1,
            "buying_mode": "classified",
            "listing_type_id": "silver",  # Tipo segun cupo disponible de la cuenta
            "condition": condition,
            "pictures": pictures,
            "location": {
                "country": {"id": "AR"},
                "state": {"id": "AR-B"},  # Buenos Aires
                "city": {"name": "Mar del Plata"},
            },
            "attributes": [
                {"id": "BRAND", "value_name": vehiculo.marca.nombre},
                {"id": "MODEL", "value_name": vehiculo.modelo.nombre},
                {"id": "TRIM", "value_name": trim},
                {"id": "DOORS", "value_name": doors},
                {"id": "VEHICLE_YEAR", "value_name": str(vehiculo.anio)},
                {"id": "KILOMETERS", "value_name": f"{vehiculo.km} km"},
                {"id": "FUEL_TYPE", "value_name": vehiculo.combustible.nombre},
                {"id": "TRANSMISSION", "value_name": transmission},
                {"id": "COLOR", "value_name": vehiculo.color},
            ],
        }

        return payload

    def publish_vehicle(self, vehiculo, user=None, custom_title: str = None, doors: str = None) -> MLPublication:
        """
        Publica un vehiculo en Mercado Libre.

        Args:
            vehiculo: Instancia de Vehiculo
            user: Usuario que realiza la accion
            custom_title: Titulo personalizado opcional
            doors: Cantidad de puertas (2, 3, 4, 5)

        Returns:
            MLPublication creada
        """
        # Verificar que no este ya publicado
        if vehiculo.ml_item_id:
            existing = MLPublication.objects.filter(ml_item_id=vehiculo.ml_item_id).first()
            if existing:
                raise MLAPIError(f"El vehiculo ya tiene una publicacion activa: {vehiculo.ml_item_id}")

        payload = self.build_item_payload(vehiculo, custom_title=custom_title, doors=doors)

        try:
            result = self.client.create_item(payload)

            # Crear registro de publicacion
            publication = MLPublication.objects.create(
                vehiculo=vehiculo,
                ml_item_id=result['id'],
                ml_title=result.get('title', vehiculo.titulo),
                ml_status=result.get('status', 'active'),
                ml_price=Decimal(str(result.get('price', vehiculo.precio))),
                ml_currency=result.get('currency_id', 'ARS'),
                ml_permalink=result.get('permalink', ''),
                ml_thumbnail=result.get('thumbnail', ''),
                ml_category_id=result.get('category_id', ''),
                ml_listing_type=result.get('listing_type_id', ''),
                patente_ml=vehiculo.patente,
                marca_ml=vehiculo.marca.nombre,
                modelo_ml=vehiculo.modelo.nombre,
                anio_ml=vehiculo.anio,
                km_ml=vehiculo.km,
                last_synced=timezone.now(),
                created_from_system=True,
            )

            # Actualizar vehiculo
            vehiculo.publicado_en_ml = True
            vehiculo.ml_item_id = result['id']
            vehiculo.ml_estado = result.get('status', 'active')
            vehiculo.ml_permalink = result.get('permalink', '')
            vehiculo.ml_fecha_sync = timezone.now()
            vehiculo.ml_error = ''
            vehiculo.save()

            # Log
            MLSyncLog.objects.create(
                action=MLSyncLog.ActionType.CREATE,
                publication=publication,
                vehiculo=vehiculo,
                user=user,
                request_data=payload,
                response_data=result,
                success=True,
            )

            logger.info(f"Vehiculo {vehiculo.patente} publicado en ML: {result['id']}")
            return publication

        except MLAPIError as e:
            vehiculo.ml_error = str(e)
            vehiculo.ml_fecha_sync = timezone.now()
            vehiculo.save(update_fields=['ml_error', 'ml_fecha_sync', 'updated_at'])

            MLSyncLog.objects.create(
                action=MLSyncLog.ActionType.CREATE,
                vehiculo=vehiculo,
                user=user,
                request_data=payload,
                response_data=e.response_data,
                success=False,
                error_message=str(e),
            )
            raise

    def update_publication_status(
        self,
        publication: MLPublication,
        status: str,
        user=None
    ) -> MLPublication:
        """
        Actualiza el estado de una publicacion en ML.

        Args:
            publication: Publicacion a actualizar
            status: Nuevo estado ('active', 'paused', 'closed')
            user: Usuario que realiza la accion
        """
        action_map = {
            'active': MLSyncLog.ActionType.ACTIVATE,
            'paused': MLSyncLog.ActionType.PAUSE,
            'closed': MLSyncLog.ActionType.CLOSE,
        }

        try:
            result = self.client.update_item_status(publication.ml_item_id, status)

            publication.ml_status = status
            publication.last_synced = timezone.now()
            publication.sync_error = ''
            publication.save()

            # Actualizar vehiculo vinculado si existe
            if publication.vehiculo:
                publication.vehiculo.ml_estado = status
                publication.vehiculo.ml_fecha_sync = timezone.now()
                publication.vehiculo.ml_error = ''
                if status == 'closed':
                    publication.vehiculo.publicado_en_ml = False
                publication.vehiculo.save()

            MLSyncLog.objects.create(
                action=action_map.get(status, MLSyncLog.ActionType.UPDATE),
                publication=publication,
                vehiculo=publication.vehiculo,
                user=user,
                request_data={'status': status},
                response_data=result,
                success=True,
            )

            return publication

        except MLAPIError as e:
            publication.sync_error = str(e)
            publication.save(update_fields=['sync_error', 'updated_at'])

            MLSyncLog.objects.create(
                action=action_map.get(status, MLSyncLog.ActionType.UPDATE),
                publication=publication,
                vehiculo=publication.vehiculo,
                user=user,
                request_data={'status': status},
                response_data=e.response_data,
                success=False,
                error_message=str(e),
            )
            raise


def get_ml_auth_url(state: str = None) -> str:
    """
    Genera la URL para iniciar el flujo OAuth2 de Mercado Libre.

    Args:
        state: Valor aleatorio para prevenir CSRF
    """
    import secrets
    state = state or secrets.token_urlsafe(32)

    params = {
        'response_type': 'code',
        'client_id': settings.ML_APP_ID,
        'redirect_uri': settings.ML_REDIRECT_URI,
        'state': state,
    }

    query_string = '&'.join(f"{k}={v}" for k, v in params.items())
    return f"https://auth.mercadolibre.com.ar/authorization?{query_string}", state


def exchange_code_for_token(code: str) -> Dict:
    """
    Intercambia el codigo de autorizacion por tokens.

    Args:
        code: Codigo recibido en el callback OAuth2

    Returns:
        Dict con access_token, refresh_token, user_id, etc.
    """
    response = requests.post(
        'https://api.mercadolibre.com/oauth/token',
        data={
            'grant_type': 'authorization_code',
            'client_id': settings.ML_APP_ID,
            'client_secret': settings.ML_SECRET_KEY,
            'code': code,
            'redirect_uri': settings.ML_REDIRECT_URI,
        }
    )

    if response.status_code != 200:
        error_data = response.json() if response.content else {}
        raise MLAPIError(
            error_data.get('message', f'Error HTTP {response.status_code}'),
            response.status_code,
            error_data
        )

    return response.json()
