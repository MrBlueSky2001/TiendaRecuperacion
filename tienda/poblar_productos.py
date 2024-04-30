import os
import random

import django
from django.conf import settings
from tienda.models import Marca, Producto
from PIL import Image

def generar_modelo(nombre_producto):
    # Genera un modelo aleatorio basado en el nombre del producto
    prefix = random.choice(["Sport", "Turbo", "GT", "Racing", "Classic", "Luxury", "Speed", "Super", "Power", "Adventure"])
    suffix = random.choice(["X", "S", "GT", "RS", "LX", "GTX", "XL", "XT"])
    return f"{prefix} {nombre_producto} {suffix}"

def generar_precio(nombre_producto):
    # Genera un precio aleatorio basado en el tipo de producto
    precios_base = {
        "Sedan": random.uniform(10000.0, 80000.0),
        "Hatchback": random.uniform(15000.0, 70000.0),
        "SUV": random.uniform(20000.0, 100000.0),
        "Truck": random.uniform(25000.0, 120000.0),
        "Sports Car": random.uniform(30000.0, 150000.0),
        "Convertible": random.uniform(35000.0, 200000.0),
        "Luxury Car": random.uniform(50000.0, 300000.0),
    }
    return round(precios_base.get(nombre_producto, random.uniform(10000.0, 200000.0)), 2)

def generar_imagen_path(nombre_producto):
    # Genera la ruta de la imagen basada en el nombre del producto
    switch_imagenes = {
        "sedan": "sedan.jpg",
        "hatchback": "hatchback.jpg",
        "suv": "suv.jpg",
        "truck": "truck.jpg",
        "sports car": "sports_car.jpg",
        "convertible": "convertible.jpg",
        "luxury car": "luxury_car.jpg",
    }
    nombre_producto_lower = nombre_producto.lower()
    nombre_archivo = switch_imagenes.get(nombre_producto_lower, "noProductos.jpg")

    # Usa la configuración de settings para obtener la ruta relativa del directorio media
    ruta_subdirectorio_media = os.path.join("img", nombre_archivo)

    return os.path.join(settings.MEDIA_ROOT, ruta_subdirectorio_media).replace("\\", "/")

# Lista de productos de coches con modelos, precios e imágenes más aleatorios
productos_coches = [
    {"nombre": "Sedan"},
    {"nombre": "Hatchback"},
    {"nombre": "SUV"},
    {"nombre": "Truck"},
    {"nombre": "Sports Car"},
    {"nombre": "Convertible"},
    {"nombre": "Luxury Car"},
]

# Marcas específicas disponibles
marcas_disponibles = ["Toyota", "Ford", "Chevrolet", "BMW", "Mercedes-Benz", "Audi", "Honda"]

# Cantidad mínima de productos a crear
cantidad_productos_deseada = 100
productos_creados = 0

# Intenta crear al menos 100 productos de coches
while productos_creados < cantidad_productos_deseada:
    # Selecciona una marca aleatoria de las disponibles
    marca_aleatoria = Marca.objects.get(nombre=random.choice(marcas_disponibles))

    # Selecciona un producto aleatorio de la lista
    producto_aleatorio = random.choice(productos_coches)

    # Verifica si ya existe un producto con el mismo nombre y modelo
    nombre_producto = producto_aleatorio["nombre"]
    modelo_aleatorio = generar_modelo(nombre_producto)

    producto_existente = Producto.objects.filter(nombre=nombre_producto, modelo=modelo_aleatorio).first()

    if producto_existente:
        # Si el producto ya existe, omite la creación de uno nuevo y pasa al siguiente ciclo
        print(f'Producto con nombre "{nombre_producto}" y modelo "{modelo_aleatorio}" ya existe. No se creó duplicado.')
    else:
        # Crea el producto con valores aleatorios
        precio_aleatorio = generar_precio(nombre_producto)
        imagen_path = generar_imagen_path(nombre_producto)

        # Crea la imagen y guarda el producto
        imagen = Image.open(imagen_path)

        Producto.objects.create(
            marca=marca_aleatoria,
            nombre=nombre_producto,
            modelo=modelo_aleatorio,
            unidades=random.randint(1, 50),
            precio=precio_aleatorio,
            vip=random.choice([True, False]),
            image=imagen_path
        )
        print(
            f'Se ha creado el producto "{nombre_producto}" con modelo "{modelo_aleatorio}", precio ${precio_aleatorio}" y imagen en "{imagen_path}".')
        productos_creados += 1

print(f'Se han creado y guardado al menos {cantidad_productos_deseada} productos de coches en la base de datos.')