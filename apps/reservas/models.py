from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class TipoOperacion(models.TextChoices):
    """Tipos de operacion con colores asociados."""
    USED = 'used', _('Reserva Usado')           # Azul
    NEW = 'new', _('Reserva 0KM')               # Rojo
    EXTERNAL = 'external', _('Operacion Externa')  # Amarillo


class EstadoReserva(models.TextChoices):
    """Estados posibles de una reserva."""
    PENDING = 'pending', _('No entregado')
    DELIVERED = 'delivered', _('Entregado')
    CANCELLED = 'cancelled', _('Anulado')
    CANCELLED_LOST_DEPOSIT = 'cancelled_lost_deposit', _('Anulado con perdida de sena')
    RESTRUCTURING = 'restructuring', _('A reestructurar')


class Reserva(models.Model):
    """
    Modelo principal para gestionar reservas/operaciones de venta.
    Soporta 3 tipos: Usados, 0KM, y Operaciones Externas.
    """

    # ==========================================================================
    # TIPO Y ESTADO
    # ==========================================================================
    tipo_operacion = models.CharField(
        _('tipo de operacion'),
        max_length=15,
        choices=TipoOperacion.choices,
        help_text=_('USED=Azul, NEW=Rojo, EXTERNAL=Amarillo')
    )
    estado = models.CharField(
        _('estado'),
        max_length=25,
        choices=EstadoReserva.choices,
        default=EstadoReserva.PENDING
    )
    numero_reserva = models.CharField(
        _('numero de reserva'),
        max_length=20,
        unique=True,
        editable=False,
        help_text=_('Generado automaticamente: RES-YYYY-XXXXX')
    )

    # ==========================================================================
    # VEHICULO RELACIONADO (Opcional para EXTERNAL)
    # ==========================================================================
    vehiculo = models.ForeignKey(
        'vehiculos.Vehiculo',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='reservas',
        verbose_name=_('vehiculo'),
        help_text=_('Requerido para USED y NEW. Opcional para EXTERNAL.')
    )

    # ==========================================================================
    # CLIENTE
    # ==========================================================================
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='reservas',
        verbose_name=_('cliente')
    )

    # ==========================================================================
    # DATOS ESPECIFICOS PARA USADOS (USED)
    # ==========================================================================
    dominio = models.CharField(
        _('dominio/patente'),
        max_length=10,
        blank=True,
        help_text=_('Patente del vehiculo usado')
    )
    propietario_anterior = models.ForeignKey(
        'vendedores.Vendedor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservas_como_propietario',
        verbose_name=_('propietario anterior'),
        help_text=_('Dueno anterior del vehiculo usado')
    )

    # ==========================================================================
    # DATOS ESPECIFICOS PARA 0KM (NEW)
    # ==========================================================================
    numero_chasis = models.CharField(
        _('numero de chasis'),
        max_length=50,
        blank=True,
        help_text=_('VIN/Chasis para vehiculos 0km')
    )
    proveedor = models.CharField(
        _('proveedor'),
        max_length=200,
        blank=True,
        help_text=_('Proveedor/Concesionario de origen')
    )
    costo_patentamiento = models.DecimalField(
        _('costo patentamiento'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    costo_flete = models.DecimalField(
        _('costo flete'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )

    # ==========================================================================
    # ESTRUCTURA DE COSTOS/PRECIOS
    # ==========================================================================
    precio_venta = models.DecimalField(
        _('precio venta base'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    moneda = models.ForeignKey(
        'parametros.Moneda',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='reservas',
        verbose_name=_('moneda')
    )
    comision_vendedor = models.DecimalField(
        _('comision vendedor'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text=_('Comision que paga el vendedor/dueno')
    )
    comision_comprador = models.DecimalField(
        _('comision comprador'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text=_('Comision que paga el comprador')
    )
    gestion_credito = models.DecimalField(
        _('gestion de credito'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    gastos_transferencia = models.DecimalField(
        _('gastos transferencia'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text=_('Transferencia para usados')
    )
    impuestos = models.DecimalField(
        _('impuestos'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    otros_gastos = models.DecimalField(
        _('otros gastos'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    descripcion_otros_gastos = models.TextField(
        _('descripcion otros gastos'),
        blank=True
    )
    observaciones_costos = models.TextField(
        _('observaciones de costos'),
        blank=True,
        help_text=_('Ej: "Se cierra precio en dolares billete"')
    )

    # ==========================================================================
    # DATOS ADMINISTRATIVOS
    # ==========================================================================
    fecha_entrega_pactada = models.DateField(
        _('fecha entrega pactada'),
        null=True,
        blank=True
    )
    vendedor_1 = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='reservas_vendedor_1',
        verbose_name=_('vendedor principal'),
        help_text=_('Usuario de Autobiliaria que realizo la venta')
    )
    vendedor_2 = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservas_vendedor_2',
        verbose_name=_('vendedor secundario'),
        help_text=_('Para comisiones compartidas')
    )
    gestor_supervisor = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservas_supervisadas',
        verbose_name=_('gestor/supervisor')
    )

    # ==========================================================================
    # CHECKBOXES DE ESTADO
    # ==========================================================================
    entregado = models.BooleanField(
        _('entregado'),
        default=False
    )
    transferido = models.BooleanField(
        _('transferido'),
        default=False,
        help_text=_('Transferencia de dominio realizada')
    )
    a_reestructurar = models.BooleanField(
        _('a reestructurar'),
        default=False
    )

    # ==========================================================================
    # AUDITORIA
    # ==========================================================================
    creada_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='reservas_creadas',
        verbose_name=_('creada por')
    )
    created_at = models.DateTimeField(
        _('fecha de creacion'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('fecha de actualizacion'),
        auto_now=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Reserva')
        verbose_name_plural = _('Reservas')
        indexes = [
            models.Index(fields=['numero_reserva']),
            models.Index(fields=['tipo_operacion']),
            models.Index(fields=['estado']),
            models.Index(fields=['vehiculo']),
            models.Index(fields=['cliente']),
            models.Index(fields=['vendedor_1']),
            models.Index(fields=['fecha_entrega_pactada']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.numero_reserva} - {self.cliente.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.numero_reserva:
            self.numero_reserva = self._generar_numero_reserva()
        super().save(*args, **kwargs)

    def _generar_numero_reserva(self):
        """Genera numero unico: RES-2024-00001"""
        year = timezone.now().year
        last = Reserva.objects.filter(
            numero_reserva__startswith=f'RES-{year}-'
        ).order_by('-numero_reserva').first()

        if last:
            last_num = int(last.numero_reserva.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f'RES-{year}-{new_num:05d}'

    @property
    def total_operacion(self):
        """Calcula el total de la operacion."""
        return (
            self.precio_venta +
            self.comision_vendedor +
            self.comision_comprador +
            self.gestion_credito +
            self.gastos_transferencia +
            self.costo_patentamiento +
            self.costo_flete +
            self.impuestos +
            self.otros_gastos
        )

    @property
    def total_pagado(self):
        """Calcula el total pagado sumando todas las formas de pago."""
        return sum(fp.monto for fp in self.formas_pago.all())

    @property
    def saldo_pendiente(self):
        """Calcula el saldo pendiente de pago."""
        return self.total_operacion - self.total_pagado

    @property
    def porcentaje_pagado(self):
        """Calcula el porcentaje pagado."""
        if self.total_operacion == 0:
            return Decimal('0')
        return (self.total_pagado / self.total_operacion) * 100

    @property
    def color_operacion(self):
        """Retorna el color asociado al tipo de operacion."""
        colores = {
            TipoOperacion.USED: 'blue',
            TipoOperacion.NEW: 'red',
            TipoOperacion.EXTERNAL: 'yellow',
        }
        return colores.get(self.tipo_operacion, 'gray')


class TipoFormaPago(models.TextChoices):
    """Tipos de forma de pago disponibles."""
    DEPOSIT = 'deposit', _('Sena')
    CASH = 'cash', _('Efectivo')
    CHECK = 'check', _('Cheque')
    PROMISSORY_NOTE = 'promissory_note', _('Pagare')
    CREDIT = 'credit', _('Credito Bancario')
    TRADE_IN = 'trade_in', _('Permuta/Auto entrega')


class FormaPago(models.Model):
    """
    Formas de pago asociadas a una reserva.
    Una reserva puede tener multiples formas de pago (combinables).
    """
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='formas_pago',
        verbose_name=_('reserva')
    )
    tipo = models.CharField(
        _('tipo'),
        max_length=20,
        choices=TipoFormaPago.choices
    )
    monto = models.DecimalField(
        _('monto'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # ==========================================================================
    # CAMPOS PARA CHEQUE
    # ==========================================================================
    cheque_numero = models.CharField(
        _('numero de cheque'),
        max_length=50,
        blank=True
    )
    cheque_banco = models.CharField(
        _('banco'),
        max_length=100,
        blank=True
    )
    cheque_fecha_vencimiento = models.DateField(
        _('fecha vencimiento'),
        null=True,
        blank=True
    )

    # ==========================================================================
    # CAMPOS PARA CREDITO BANCARIO
    # ==========================================================================
    credito_banco = models.CharField(
        _('banco del credito'),
        max_length=100,
        blank=True
    )
    credito_cuotas = models.PositiveIntegerField(
        _('cantidad de cuotas'),
        null=True,
        blank=True
    )
    credito_valor_cuota = models.DecimalField(
        _('valor de cuota'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    credito_valor_acreditado = models.DecimalField(
        _('valor acreditado'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Monto que el banco acredita neto')
    )

    # ==========================================================================
    # CAMPOS PARA PERMUTA/AUTO ENTREGA
    # ==========================================================================
    permuta_marca = models.CharField(
        _('marca del auto entrega'),
        max_length=100,
        blank=True
    )
    permuta_modelo = models.CharField(
        _('modelo del auto entrega'),
        max_length=100,
        blank=True
    )
    permuta_anio = models.PositiveIntegerField(
        _('ano del auto entrega'),
        null=True,
        blank=True
    )
    permuta_km = models.PositiveIntegerField(
        _('kilometraje del auto entrega'),
        null=True,
        blank=True
    )
    permuta_patente = models.CharField(
        _('patente del auto entrega'),
        max_length=10,
        blank=True
    )
    permuta_es_stock = models.BooleanField(
        _('es para stock'),
        default=True,
        help_text=_('True=Stock 100%%, False=50%% valor')
    )
    permuta_vehiculo = models.ForeignKey(
        'vehiculos.Vehiculo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permutas',
        verbose_name=_('vehiculo de permuta'),
        help_text=_('Si el auto entrega se ingresa al sistema')
    )

    # ==========================================================================
    # CAMPOS PARA SENA/DEPOSITO
    # ==========================================================================
    sena_fecha = models.DateField(
        _('fecha de sena'),
        null=True,
        blank=True
    )
    sena_recibida_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='senas_recibidas',
        verbose_name=_('recibida por')
    )

    # ==========================================================================
    # AUDITORIA
    # ==========================================================================
    notas = models.TextField(
        _('notas'),
        blank=True
    )
    created_at = models.DateTimeField(
        _('fecha de creacion'),
        auto_now_add=True
    )

    class Meta:
        ordering = ['tipo', 'created_at']
        verbose_name = _('Forma de Pago')
        verbose_name_plural = _('Formas de Pago')

    def __str__(self):
        return f"{self.get_tipo_display()} - ${self.monto:,.2f}"


class TipoCuentaGasto(models.TextChoices):
    """A quien corresponde el gasto."""
    CLIENTE = 'cliente', _('A cuenta del cliente')
    ADMINISTRACION = 'administracion', _('A cuenta administracion')


class GastoAdministrativo(models.Model):
    """
    Gastos administrativos para operaciones EXTERNAL (gestoria pura).
    Separa gastos a cuenta del cliente vs a cuenta de administracion.
    """
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='gastos_administrativos',
        verbose_name=_('reserva')
    )
    concepto = models.CharField(
        _('concepto'),
        max_length=200,
        help_text=_('Ej: Arancel, Formulario 08, Verificacion Policial')
    )
    monto = models.DecimalField(
        _('monto'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    tipo_cuenta = models.CharField(
        _('tipo de cuenta'),
        max_length=15,
        choices=TipoCuentaGasto.choices,
        default=TipoCuentaGasto.CLIENTE
    )
    fecha = models.DateField(
        _('fecha del gasto'),
        null=True,
        blank=True
    )
    metodo_pago = models.CharField(
        _('metodo de pago'),
        max_length=50,
        blank=True,
        help_text=_('Ej: Efectivo, Transferencia')
    )
    created_at = models.DateTimeField(
        _('fecha de creacion'),
        auto_now_add=True
    )

    class Meta:
        ordering = ['tipo_cuenta', 'created_at']
        verbose_name = _('Gasto Administrativo')
        verbose_name_plural = _('Gastos Administrativos')

    def __str__(self):
        return f"{self.concepto} - ${self.monto:,.2f} ({self.get_tipo_cuenta_display()})"


class NotaReserva(models.Model):
    """
    Historial de notas/seguimiento de una reserva.
    """
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='notas',
        verbose_name=_('reserva')
    )
    contenido = models.TextField(
        _('contenido')
    )
    autor = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='notas_reservas',
        verbose_name=_('autor')
    )
    created_at = models.DateTimeField(
        _('fecha'),
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Nota de Reserva')
        verbose_name_plural = _('Notas de Reserva')

    def __str__(self):
        return f"Nota de {self.autor.get_full_name()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
