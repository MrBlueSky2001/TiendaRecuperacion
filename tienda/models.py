import uuid
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# Cuidado con el orden de las clases porque al formar dependencias si una clase no existe no puede relacionarse con otra

class Marca(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.nombre}"


class Cliente(models.Model):
    vip = models.BooleanField()
    saldo = models.DecimalField(decimal_places=2, max_digits=10)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} {self.vip} {self.saldo}"


class Producto(models.Model):
    marca = models.ForeignKey(
        Marca,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    nombre = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50, unique=True)
    unidades = models.IntegerField()
    precio = models.DecimalField(decimal_places=2, max_digits=10)
    vip = models.BooleanField()
    image = models.ImageField(null=False, upload_to="img/", default='img/empty.png', max_length=255)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "productos"

    def __str__(self):
        return f"{self.marca} {self.nombre} {self.modelo} {self.unidades} {self.precio} {self.vip}"


class TarjetaDePago(models.Model):
    TIPO_CHOICES = (
        (1, 'VISA'),
        (2, 'MASTERCARD'),
        (3, 'AMERICAN EXPRESS'),
    )
    numero = models.IntegerField()
    tipo = models.IntegerField(choices=TIPO_CHOICES, default=1)
    titular = models.CharField(max_length=100)
    fecha_caducidad = models.DateField()
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    class Meta:
        ordering = ["tipo"]
        verbose_name_plural = "tarjetas"

    def __str__(self):
        return f"{self.numero} {self.titular} {self.tipo} {self.fecha_caducidad}"


class Direccion(models.Model):
    tipo_via = models.CharField(max_length=50)
    nombre = models.CharField(max_length=100)
    numero = models.IntegerField()
    envio = models.BooleanField()
    facturacion = models.BooleanField()
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    class Meta:
        verbose_name_plural = "direcciones"

    def __str__(self):
        return f"{self.tipo_via} {self.nombre} {self.numero}"


class Compra(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    fecha = models.DateField()
    importe = models.DecimalField(decimal_places=2, max_digits=10)
    iva = models.DecimalField(decimal_places=2, max_digits=5)
    direccion_envio = models.ForeignKey(
        Direccion,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='direccion_envio'
    )
    direccion_facturacion = models.ForeignKey(
        Direccion,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='direccion_facturacion'
    )
    metodo_pago = models.ForeignKey(
        TarjetaDePago,
        on_delete=models.SET_NULL,
        blank=False,
        null=True
    )

    class Meta:
        ordering = ["fecha"]
        verbose_name_plural = "compras"

    def __str__(self):
        return f"{self.cliente}{self.fecha} {self.importe} {self.iva}"

class ProductoCompra(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        blank=False,
        null=True
    )
    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    unidades = models.IntegerField()
    precio = models.DecimalField(decimal_places=2, max_digits=10)

    class Meta:
        verbose_name_plural = "Productos compra"

        def __str__(self):
            return f"{self.producto} {self.compra} {self.unidades} {self.precio}"

class Valoracion(models.Model):
    PUNTUACION_CHOICES = (
        (1, '1 estrella'),
        (2, '2 estrellas'),
        (3, '3 estrellas'),
        (4, '4 estrellas'),
        (5, '5 estrellas'),
    )

    puntuacion = models.IntegerField(choices=PUNTUACION_CHOICES)
    comentario = models.TextField(blank=True)
    productocompra = models.OneToOneField(ProductoCompra, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Valoraciones"
        permissions = [
            ("can_edit_commentary", "Can edit commentaries of any user")
        ]

    def __str__(self):
        return f"{self.puntuacion} {self.comentario} {self.productocompra}"
