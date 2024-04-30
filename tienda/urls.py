from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

from .views import ProductoCreateView, ProductoDeleteView, ProductosListView, ProductoUpdateView, \
    ProductosTopTenListView, ClientesTopTenListView, ProductoPorMarcaInformeFilterView, \
    InformesView, ComprasPorClienteInformeFilterView, ListadoComprarFilterView, LoginClienteView, ProductoDetailView, \
    LogoutClienteView, ClienteDetailView, ClienteCreateView, DireccionCreateView, \
    TarjetaPagoCreateView, ClienteUpdateView, PasswordUpdateView, ValoracionUpdateView, ValoracionCreateView, \
    CheckoutCreateView, CarritoView, AgregarCarritoItemView, CarritoDeleteItemView, CompraDetailView, \
    DireccionUpdateView, DireccionDeleteView, TarjetaPagoUpdateView, TarjetaPagoDeleteView

urlpatterns = [
    path('', views.welcome, name='welcome'),

    path('tienda/', views.welcome, name='tienda'),

    #Gestión de staff
    path('tienda/admin/productos/listado/', ProductosListView.as_view(), name='listado_productos'),
    path('tienda/admin/productos/edicion/<int:pk>', ProductoUpdateView.as_view(), name='editar_producto'),
    path('tienda/admin/productos/eliminar/<int:pk>', ProductoDeleteView.as_view(), name='eliminar_producto'),
    path('tienda/admin/productos/crear/', ProductoCreateView.as_view(), name='crear_producto'),

    #Compra
    path('tienda/compra/', ListadoComprarFilterView.as_view(), name='listado_comprar'),
    path('tienda/compra/detalle/<int:pk>', ProductoDetailView.as_view(), name='detalle_producto'),
    path('tienda/compra/carrito/', CarritoView.as_view(), name='carrito'),
    path('tienda/compra/carrito/borrar/<uuid:pk>', CarritoDeleteItemView.as_view(), name='borrar_carrito'),
    path('tienda/compra/carrito/agregar', AgregarCarritoItemView.as_view(), name='agregar_carrito'),
    path('tienda/compra/checkout/', CheckoutCreateView.as_view(), name='checkout'),

    #Informes
    path('tienda/informes/', InformesView.as_view(), name='informe_productos'),
    path('tienda/informes/marca/', ProductoPorMarcaInformeFilterView.as_view(), name='informe_productos_marca'),
    path('tienda/informes/productos/topten/', ProductosTopTenListView.as_view(), name='informe_productos_topten'),
    path('tienda/informes/users/topten/', ClientesTopTenListView.as_view(), name='informe_usuarios_topten'),
    path('tienda/informes/compras/', ComprasPorClienteInformeFilterView.as_view(), name='informe_compras_usuario'),

    #Gestión usuarios
    path('tienda/login/', LoginClienteView.as_view(), name='login'),
    path('tienda/logout/', LogoutClienteView.as_view(), name='logout'),
    path('user/register/', ClienteCreateView.as_view(), name="register"),

    #Perfil Usuario
    path('user/info/', ClienteDetailView.as_view(), name="client_info"),
    path('user/info/update/<int:pk>', ClienteUpdateView.as_view(), name="client_info_update"),
    path('user/info/update/password/', PasswordUpdateView.as_view(), name="client_info_password_update"),
    path('user/info/direccion/crear', DireccionCreateView.as_view(), name="client_address_create"),
    path('user/info/direccion/update/<int:pk>', DireccionUpdateView.as_view(), name="client_address_update"),
    path('user/info/direccion/delete/<int:pk>', DireccionDeleteView.as_view(), name="client_address_delete"),
    path('user/info/tarjetapago/update/<int:pk>', TarjetaPagoUpdateView.as_view(), name="client_payment_update"),
    path('user/info/tarjetapago/delete/<int:pk>', TarjetaPagoDeleteView.as_view(), name="client_payment_delete"),
    path('user/info/tarjetapago/crear', TarjetaPagoCreateView.as_view(), name="client_payment_create"),
    path('user/info/compra/<int:pk>', CompraDetailView.as_view(), name="compra_detail"),

    #Valoraciones
    path('user/compra/valoracion/update/<int:pk>', ValoracionUpdateView.as_view(), name="order_rating_update"),
    path('user/compra/valoracion/create/<int:pk>', ValoracionCreateView.as_view(), name="order_rating_create"),
    path('user/register/', ClienteCreateView.as_view(), name="register"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
