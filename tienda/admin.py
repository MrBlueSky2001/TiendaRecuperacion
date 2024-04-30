from django.contrib import admin
from .models import *
admin.site.register(Compra)
admin.site.register(Producto)
admin.site.register(Marca)
admin.site.register(Cliente)
admin.site.register(Direccion)
admin.site.register(TarjetaDePago)
admin.site.register(Valoracion)
admin.site.register(ProductoCompra)