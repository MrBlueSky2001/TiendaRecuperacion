from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

from .views import *

urlpatterns = [
    path('', views.welcome, name='welcome'),

    path('tienda/', views.welcome, name='tienda'),

# Flujo de trabajo del admin:
# En primera instancia el admin verá el base.html con el block de listado_productos_compra.html
# Pulsamos en "Gestión de productos" y nos conducirá a "listado_productos.html". Ahí podremos editar (editar_producto.html),
# eliminar (eliminar_producto.html) y crear (plantilla_para_formulario.html).
# Si pulsamos en "Informes" nos redirige a "informes.html" que será un index que albergue a "compras_cliente.html",
# "top_diez_clientes.html", "top_diez_productos.html" y "productos_por_marca.html".
#
# Vista principal
# path('tienda/compra/', ListadoProductosCompraFilterView.as_view(), name='listado_comprar'),
#
# Gestión de productos
# path('tienda/admin/productos/listado/', ListadoProductosView.as_view(), name='listado_productos'),
# path('tienda/admin/productos/edicion/<int:pk>', EditarProductoView.as_view(), name='editar_producto'),
# path('tienda/admin/productos/eliminar/<int:pk>', EliminarProductoView.as_view(), name='eliminar_producto'),
# path('tienda/admin/productos/crear/', CrearProductoView.as_view(), name='crear_producto'),
#
# Informes
# path('tienda/informes/', InformesView.as_view(), name='informe_productos'),
#
# 	Vista en el index de informes
# 	path('tienda/informes/marca/', ProductoPorMarcaFilterView.as_view(), name='informe_productos_marca'),
# 	path('tienda/informes/productos/topten/', TopDiezProductosListView.as_view(), name='informe_productos_topten'),
# 	path('tienda/informes/compras/', ComprasClientesFilterView.as_view(), name='informe_compras_usuario'),
# 	path('tienda/informes/users/topten/', TopDiezClientesListView.as_view(), name='informe_usuarios_topten'),

    path('tienda/admin/productos/listado/', ListadoProductosView.as_view(), name='listado_productos'),
    path('tienda/admin/productos/edicion/<int:pk>', EditarProductoView.as_view(), name='editar_producto'),
    path('tienda/admin/productos/eliminar/<int:pk>', EliminarProductoView.as_view(), name='eliminar_producto'),
    path('tienda/admin/productos/crear/', CrearProductoView.as_view(), name='crear_producto'),

    path('tienda/informes/', InformesView.as_view(), name='informe_productos'),

	path('tienda/informes/marca/', ProductoPorMarcaFilterView.as_view(), name='informe_productos_marca'),
	path('tienda/informes/productos/topten/', TopDiezProductosListView.as_view(), name='informe_productos_topten'),
	path('tienda/informes/compras/', ComprasClientesFilterView.as_view(), name='informe_compras_usuario'),
	path('tienda/informes/users/topten/', TopDiezClientesListView.as_view(), name='informe_usuarios_topten'),

# Flujo de trabajo del cliente
# El cliente en primera instancia verá los productos del "listado_productos_compra.html". Este usuario se registrará en la página
# con el "registrar_cliente.html", o podrá iniciar sesión con el "login.html". Hecho esto el cliente podrá cerrar sesión con el logout
# y redirigirá al inicio.
#
# Vista principal
# path('tienda/compra/', ListadoProductosCompraFilterView.as_view(), name='listado_comprar'),
#
# Registro, inicio y cierre de sesión
# path('user/register/', ClienteSignUpView.as_view(), name="register"),
# path('tienda/login/', ClienteLoginView.as_view(), name='login'),
# path('tienda/logout/', ClienteLogoutView.as_view(), name='logout'),

    path('tienda/login/', ClienteLoginView.as_view(), name='login'),
    path('tienda/logout/', ClienteLogoutView.as_view(), name='logout'),
    path('user/register/', ClienteSignUpView.as_view(), name="register"),

    path('tienda/compra/carrito/', CarroCompraView.as_view(), name='carrito'),
    path('tienda/compra/checkout/', CheckoutView.as_view(), name='checkout'),
    path('user/info/compra/<int:pk>', HistorialView.as_view(), name="compra_detail"),
    path('tienda/compra/detalle/<int:pk>', DetallesDelProductoView.as_view(), name='detalle_producto'),
    path('tienda/compra/carrito/agregar', AgregarProductoCarroView.as_view(), name='agregar_carrito'),
    path('tienda/compra/carrito/borrar/<uuid:pk>', EliminarProductoCarroView.as_view(), name='borrar_carrito'),
    path('tienda/compra/', ListadoProductosCompraFilterView.as_view(), name='listado_comprar'),

    path('user/info/direccion/crear', CrearDireccionView.as_view(), name="client_address_create"),
    path('user/info/direccion/update/<int:pk>', ModificarDireccionView.as_view(), name="client_address_update"),
    path('user/info/direccion/delete/<int:pk>', EliminarDireccionView.as_view(), name="client_address_delete"),
    path('user/info/tarjetapago/crear', CrearTarjetaDePagoView.as_view(), name="client_payment_create"),
    path('user/info/tarjetapago/update/<int:pk>', ModificarTarjetaDePagoView.as_view(), name="client_payment_update"),
    path('user/info/tarjetapago/delete/<int:pk>', EliminarTarjetaDePagoView.as_view(), name="client_payment_delete"),
    path('user/info/', InformacionDelClienteView.as_view(), name="client_info"),

    path('user/compra/valoracion/create/<int:pk>', CrearValoracionesView.as_view(), name="order_rating_create"),
    path('user/compra/valoracion/update/<int:pk>', ModificarValoracionesView.as_view(), name="order_rating_update"),

    path('user/<int:cliente_id>/modificar-saldo/', ModificarSaldoView.as_view(), name='modificar_saldo'),

    path('user/info/update/password/', ModificarContrasenaView.as_view(), name="client_info_password_update"),
    path('user/info/update/<int:pk>', ModificarDatosDelClienteView.as_view(), name="client_info_update"),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
