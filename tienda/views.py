# Importamos las librerías y módulos.
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core import serializers
import datetime
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView, TemplateView, View, DetailView, CreateView, DeleteView, FormView
from django_filters.views import FilterView
from django.db.models import Sum, F
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from extra_views import FormSetView
from .forms import *
from .models import *
from django.forms import formset_factory

# Definimos una función para verificar si un usuario es un cliente.
def verify_client(user):
    return Cliente.objects.filter(user=user).exists()

# Redireccionamos al usuario al listado de compras.
def welcome(request):
    return redirect('listado_comprar')

# Se requiere que el usuario sea un miembro del personal para acceder a esta vista.
@method_decorator(staff_member_required, name='dispatch')
class EditarProductoView(UpdateView):
    # Especificamos el modelo que se va a editar.
    model = Producto
    # Especificamos la plantilla que se utilizará para renderizar la vista.
    template_name = 'tienda/administrador/administrar_productos/editar_producto.html'
    # Especificamos los campos del modelo que se van a editar.
    fields = ['marca', 'nombre', 'modelo', 'unidades', 'precio', 'vip', 'image']
    # Especificamos la URL a la que se redirige después de que el formulario se haya enviado con éxito.
    success_url = reverse_lazy('listado_productos')
    # Definimos el comportamiento cuando el formulario es inválido.
    def form_invalid(self, form):
        # Agregamos un mensaje de advertencia si hay un error en el formulario.
        messages.add_message(self.request, messages.WARNING, "Error de formulario")

# Se requiere que el usuario sea un miembro del personal para acceder a esta vista.
@method_decorator(staff_member_required, name='dispatch')
class EliminarProductoView(DeleteView):
    # Especificamos el modelo que se va a eliminar.
    model = Producto
    # Especificamos la plantilla que se utilizará para renderizar la vista.
    template_name = 'tienda/administrador/administrar_productos/eliminar_producto.html'
    # Especificamos la URL a la que se redirige después de que el producto se haya eliminado con éxito.
    success_url = reverse_lazy('listado_productos')

# Se requiere que el usuario sea un miembro del personal para acceder a esta vista.
@method_decorator(staff_member_required, name='dispatch')
class ListadoProductosView(ListView):
    # Especificamos el modelo que se va a listar.
    model = Producto
    # Especificamos la plantilla que se utilizará para renderizar la vista.
    template_name = 'tienda/administrador/administrar_productos/listado_productos.html'
    # Especificamos la consulta que se utilizará para obtener los productos.
    queryset = Producto.objects.all()
    # Especificamos el nombre del contexto que contendrá los productos.
    context_object_name = "productos"

# Se requiere que el usuario sea un miembro del personal para acceder a esta vista.
@method_decorator(staff_member_required(), name='dispatch')
class CrearProductoView(CreateView):
    # Especificamos el modelo que se va a crear.
    model = Producto
    # Especificamos la plantilla que se utilizará para renderizar la vista.
    template_name = 'tienda/plantilla_para_formulario.html'
    # Especificamos los campos del modelo que se van a crear.
    fields = ['marca', 'nombre', 'modelo', 'unidades', 'precio', 'vip', 'image']
    # Especificamos la URL a la que se redirige después de que el formulario se haya enviado con éxito.
    success_url = reverse_lazy('listado_productos')

# Se requiere que el usuario sea un miembro del personal para acceder a esta vista.
@method_decorator(staff_member_required(), name='dispatch')
class ComprasClientesFilterView(ListView):
    # Especifica la plantilla que se utilizará para renderizar la vista.
    template_name = 'tienda/administrador/informes/compras_clientes.html'
    # Especifica el nombre del contexto que contendrá las compras.
    context_object_name = "compras"
    # Especifica el formulario que se utilizará para filtrar las compras.
    form_class = BuscarCompraForm
    # Definimos la consulta que se utilizará para obtener las compras.
    def get_queryset(self):
        queryset = Compra.objects.all()
        cliente = self.request.GET.get('cliente')
        if cliente:
            queryset = queryset.filter(cliente=cliente)
        return queryset
    # Agregamos el formulario al contexto.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET)
        return context

# Se requiere que el usuario sea un miembro del personal para acceder a esta vista.
@method_decorator(staff_member_required(), name='dispatch')
class InformesView(TemplateView):
    template_name = 'tienda/administrador/informes/informes.html'

# Se requiere que el usuario sea un miembro del personal para acceder a esta vista.
@method_decorator(staff_member_required(), name='dispatch')
class ProductoPorMarcaFilterView(ListView):
    # Especificamos la plantilla que se utilizará para renderizar la vista.
    template_name = 'tienda/administrador/informes/productos_por_marca.html'
    # Especificamos el nombre del contexto.
    context_object_name = "productos"
    # Especificamos el modelo.
    model = Producto
    # Definimos la consulta que se utilizará para obtener las compras.
    def get_queryset(self):
        queryset = super().get_queryset()
        marca_id = self.request.GET.get('marca_id')
        if marca_id:
            queryset = queryset.filter(marca_id=marca_id)
        return queryset
    # Agregamos el formulario al contexto.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marcas'] = Marca.objects.all()
        return context

# Se requiere que el usuario sea un miembro del personal para acceder a esta vista.
@method_decorator(staff_member_required(), name='dispatch')
class TopDiezClientesListView(ListView):
    # Especificamos la plantilla que se utilizará para renderizar la vista.
    template_name = 'tienda/administrador/informes/top_diez_clientes.html'
    # Especificamos el nombre del contexto.
    context_object_name = "usuarios"
    # Especificamos la consulta .
    queryset = Cliente.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuarios = Cliente.objects.filter(compra__isnull=False).annotate(
            sum_importes=Sum('compra__importe')
        ).order_by("-sum_importes")[:10]
        context['usuarios'] = usuarios
        return context

# Se requiere que el usuario sea un miembro del personal para acceder a esta vista.
@method_decorator(staff_member_required(), name='dispatch')
class TopDiezProductosListView(ListView):
    # Especificamos la plantilla que se utilizará para renderizar la vista.
    template_name = 'tienda/administrador/informes/top_diez_productos.html'
    # Especificamos el nombre del contexto.
    context_object_name = "productos"
    # Especificamos la consulta.
    queryset = Producto.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productos = Producto.objects.filter(productocompra__isnull=False).annotate(
            sum_ventas=Sum('productocompra__unidades'),
            sum_importes=Sum(F('precio') * F('productocompra__unidades'), output_field=models.FloatField())
        ).order_by("-sum_ventas")[:10]
        context['productos'] = productos
        return context

class ClienteLoginView(LoginView):
    # Especificamos la plantilla que se utilizará para renderizar la vista.
    template_name = 'tienda/inicio_sesion/login.html'
    # Sobrescribimos el método form_valid para verificar el cliente antes de iniciar sesión.
    def form_valid(self, form):
        user = form.get_user()
        # Función para verificar si el usuario es un cliente registrado.
        if verify_client(user): 
            return_value = super().form_valid(form)
        else:
            messages.add_message(self.request, messages.WARNING, "No está registrado para iniciar sesión.")
            return_value = self.form_invalid(form)
        return return_value
    # Sobrescribimos el método get_success_url para redirigir al usuario a la página después del inicio de sesión.
    def get_success_url(self):
        try:
            next_page = self.request.GET['next']
        except:
            next_page = "/"
        return next_page

class ClienteLogoutView(LoginRequiredMixin, LogoutView):
    # Especificamos la página a la que se redirigirá después de cerrar sesión.
    next_page = '/tienda'
    # Agregamos un mensaje de error al contexto para notificar al usuario que la sesión se ha cerrado.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages.add_message(self.request, messages.ERROR, "Sesión cerrada")
        return context

class ClienteSignUpView(CreateView):
    # Especificamos el modelo, la plantilla y el formulario de registro de clientes.
    model = Cliente
    template_name = 'tienda/plantilla_para_formulario.html'
    success_url = reverse_lazy('tienda')
    form_class = RegistrarClienteForm
    # Sobrescribimos el método para obtener el formulario.
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form
    # Sobrescribimos el método form_valid para procesar el formulario después de ser válido.
    def form_valid(self, form):
        # Llamamos al método form_valid de la clase padre.
        response = super().form_valid(form)
        # Obtenemos el nombre de usuario del formulario.
        form_username = form.cleaned_data.get("username")
        # Obtenemos el usuario recién creado.
        user = User.objects.get(username=form_username)
        # Creamos un objeto de cliente asociado con el usuario y lo guardamos en la base de datos.
        cliente = Cliente(vip=False, saldo=0, user=user)
        cliente.save()
        # Iniciamos sesión con el usuario recién creado.
        login(self.request, user)
        # Devolvemos la respuesta.
        return response

class CarroCompraView(LoginRequiredMixin, UserPassesTestMixin, FormSetView):
    # Especificamos la plantilla y el formulario para la vista del carrito de compras.
    template_name = 'tienda/cliente/compra/carro.html'
    form_class = CarritoForm
    # Sobrescribimos el método formset_valid para procesar el formulario del carrito cuando es válido.
    def formset_valid(self, formset):
        # Obtenemos el contexto.
        context = self.get_context_data()
        productoscompra = context['productoscompra']
        counter = 0
        # Actualizamos las unidades de los productos en el carrito.
        for form, productocompra in zip(formset, productoscompra):
            productocompra.unidades = form.cleaned_data['unidades']
            counter += 1

        context['productoscompra'] = productoscompra
        # Guardamos la lista actualizada de productos en el carrito en la sesión.
        if counter > 0:
            self.request.session['lista_productos_carrito'] = serializers.serialize('json', productoscompra)

        return super().formset_valid(formset)
    # Método para verificar si el usuario es un cliente.
    def test_func(self):
        return verify_client(self.request.user)
    # Sobrescribimos el método para obtener el contexto.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productoscompra = []
        # Verificamos si hay productos en el carrito en la sesión.
        if 'lista_productos_carrito' in self.request.session:
            context['comprobar_vacio'] = False
            des_list = serializers.deserialize('json', self.request.session['lista_productos_carrito'])
            for productocompra in des_list:
                productoscompra.append(productocompra.object)
        else:
            context['comprobar_vacio'] = True

        context['productoscompra'] = productoscompra
        context['formset'] = formset_factory(self.form_class, extra=len(productoscompra))

        if 'productoscompra' in context:
            # Creamos un formulario con datos iniciales para cada producto en el carrito.
            initial = [{'id_producto': productocompra.producto.id, 'unidades': productocompra.unidades}
                       for productocompra in context['productoscompra']]
            context['formset'] = formset_factory(self.form_class, extra=len(productoscompra))(initial=initial)

        return context

class ComprobarCarro:
    # Método para comprobar si hay productos en el carrito.
    def dispatch(self, request, *args, **kwargs):
        if 'lista_productos_carrito' not in self.request.session:
            messages.add_message(self.request, messages.ERROR, "Carrito vacío")
            return self.redirect_tienda()
        return super().dispatch(request, *args, **kwargs)
    # Método para redirigir a la tienda.
    def redirect_tienda(self):
        return HttpResponseRedirect(reverse_lazy('tienda'))

class CheckoutView(ComprobarCarro, LoginRequiredMixin, UserPassesTestMixin, FormView):
    # Especificamos la plantilla, el formulario y la URL de redirección después del checkout.
    template_name = 'tienda/cliente/compra/checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('tienda')
    # Método para verificar si el usuario es un cliente.
    def test_func(self):
        return verify_client(self.request.user)
    # Sobrescribimos el método para obtener el contexto.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productoscompra = []
        precio_total = 0
        # Obtenemos los productos en el carrito y calculamos el precio total.
        if 'lista_productos_carrito' in self.request.session:
            des_list = serializers.deserialize('json', self.request.session['lista_productos_carrito'])
            for productocompra in des_list:
                productoscompra.append(productocompra.object)
                precio_total += (productocompra.object.precio * productocompra.object.unidades)
        print("Productos en el carrito:", productoscompra)
        context['productoscompra'] = productoscompra
        context['precio_total'] = precio_total
        return context
    # Sobrescribimos el método para obtener el formulario.
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtramos las opciones de método de pago y direcciones de envío y facturación basadas en el cliente.
        form.fields['metodo_pago'].queryset = TarjetaDePago.objects.filter(cliente__user_id=self.request.user.id)
        form.fields['direccion_envio'].queryset = Direccion.objects.filter(cliente__user_id=self.request.user.id, envio=True)
        form.fields['direccion_facturacion'].queryset = Direccion.objects.filter(cliente__user_id=self.request.user.id, facturacion=True)
        return form
    # Sobrescribimos el método form_valid para procesar el formulario cuando es válido.
    @transaction.atomic
    def form_valid(self, form):
        form_valid = super().form_valid(form)
        context = self.get_context_data()
        productoscompra = context['productoscompra']
        cliente = Cliente.objects.filter(user=self.request.user).first()
        # Verificamos si hay suficientes unidades de productos disponibles para la compra.
        for productocompra in productoscompra:
            if productocompra.unidades > productocompra.producto.unidades:
                messages.add_message(self.request, messages.ERROR, "Compra inválida")
                return redirect('checkout')
        # Procesamos la compra si el cliente tiene suficiente saldo.
        if cliente.saldo >= context['precio_total']:
            compra = Compra()
            compra.importe = context['precio_total']
            compra.fecha = datetime.date.today()
            compra.iva = 0.21
            compra.cliente = cliente

            compra.metodo_pago = form.cleaned_data.get('metodo_pago')
            compra.direccion_envio = form.cleaned_data.get('direccion_envio')
            compra.direccion_facturacion = form.cleaned_data.get('direccion_facturacion')

            compra.save()

            cliente.saldo -= compra.importe
            cliente.save()
            # Actualizamos las unidades de productos y asociamos los productos con la compra.
            for productocompra in productoscompra:
                productocompra.compra = compra
                productocompra.producto.unidades -= productocompra.unidades
                productocompra.producto.save()
                productocompra.save()
            # Vaciamos el carrito de compras en la sesión.
            del self.request.session['lista_productos_carrito']
            messages.add_message(self.request, messages.SUCCESS, "Compra realizada")

        return form_valid

class HistorialView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    # Especificamos el modelo y la plantilla para la vista del historial de compras.
    model = Compra
    template_name = 'tienda/cliente/compra/historial.html'
    # Sobrescribimos el método para obtener el contexto.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtenemos los productos comprados en esta compra.
        context['productoscompra'] = ProductoCompra.objects.filter(compra_id=self.object.id).select_related(
            'valoracion')
        return context
    # Método para verificar si el usuario es el propietario de la compra.
    def test_func(self):
        result = False
        # Obtenemos la compra correspondiente al id proporcionado en la URL.
        compra = get_object_or_404(Compra, pk=self.kwargs["pk"])
        # Verificamos si el usuario es un cliente y si la compra pertenece al usuario.
        if verify_client(self.request.user) and compra.cliente.user.id == self.request.user.id:
            result = True
        return result

class DetallesDelProductoView(DetailView):
    # Especificamos el modelo, la plantilla y el nombre del objeto de contexto.
    model = Producto
    template_name = 'tienda/cliente/compra/detalle_del_producto.html'
    context_object_name = 'producto'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Verificamos si el usuario está autenticado y es un cliente.
        if not request.user.is_anonymous and verify_client(request.user):
            # Creamos un formulario de compra con el producto actual.
            form = CompraForm(initial={'id_producto': self.object.id})
        else:
            form = None
        # Obtenemos las valoraciones del producto.
        valoraciones = Valoracion.objects.filter(productocompra__producto_id=self.object.id)
        # Pasamos el producto, el formulario y las valoraciones al contexto.
        context = {'producto': self.object, 'form': form, 'valoraciones': valoraciones}
        return render(request, self.template_name, context)

class AgregarProductoCarroView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    # Especificamos el formulario para agregar productos al carrito.
    form_class = CompraForm
    # Método para verificar si el usuario es un cliente.
    def test_func(self):
        return verify_client(self.request.user)
    # Método para procesar el formulario cuando es válido.
    def form_valid(self, form):
        lista_productos = []
        # Obtenemos la lista de productos en el carrito si existe en la sesión.
        if 'lista_productos_carrito' in self.request.session:
            des_list = serializers.deserialize('json', self.request.session['lista_productos_carrito'])
            for productocompra in des_list:
                lista_productos.append(productocompra.object)
        # Obtenemos la cantidad y el id del producto del formulario.
        unidades = form.cleaned_data['unidades']
        id_producto = form.cleaned_data['id_producto']
        producto = Producto.objects.filter(id=id_producto).first()
        # Verificamos si el producto ya está en el carrito.
        if any(miProducto.producto.id == producto.id for miProducto in lista_productos):
            for miProducto in lista_productos:
                if miProducto.producto.id == producto.id:
                    miProducto.unidades = miProducto.unidades + int(unidades)
        else:
            # Si el producto no está en el carrito, lo añadimos.
            nuevo_producto = ProductoCompra(producto=producto, compra=None, unidades=unidades,
                                            precio=producto.precio)
            lista_productos.append(nuevo_producto)
        # Guardamos la lista actualizada de productos en el carrito en la sesión.
        self.request.session['lista_productos_carrito'] = serializers.serialize('json', lista_productos)
        # Añadimos un mensaje de éxito y redirigimos a la página deseada.
        messages.add_message(self.request, messages.SUCCESS, "Añadido al carrito")
        return redirect(self.get_success_url())
    # Método para obtener la URL.
    def get_success_url(self):
        try:
            next_page = self.request.GET['next']
        except:
            next_page = "/"
        return next_page

class EliminarProductoCarroView(LoginRequiredMixin, UserPassesTestMixin, View):
    # Método para verificar si el usuario es un cliente.
    def test_func(self):
        return verify_client(self.request.user)
    # Método GET para eliminar un producto del carrito.
    def get(self, request, pk):
        productoscompra = []
        # Verificamos si hay productos en el carrito en la sesión.
        if 'lista_productos_carrito' in self.request.session:
            des_list = serializers.deserialize('json', self.request.session['lista_productos_carrito'])
            for productocompra in des_list:
                # Agregamos todos los productos excepto el que se va a eliminar.
                if not productocompra.object.uuid == pk:
                    productoscompra.append(productocompra.object)
            # Guardamos la lista actualizada de productos en el carrito en la sesión.
            if len(productoscompra) > 0:
                self.request.session['lista_productos_carrito'] = serializers.serialize('json', productoscompra)
            else:
                del self.request.session['lista_productos_carrito']
        # Redirigimos al carrito después de eliminar el producto.
        return redirect('carrito')

class ListadoProductosCompraFilterView(FilterView):
    # Especificamos la plantilla y el nombre del objeto de contexto.
    template_name = 'tienda/cliente/compra/listado_productos_compra.html'
    context_object_name = "productos"
    # Obtenemos el formulario de búsqueda.
    def get(self, request, *args, **kwargs):
        form = BuscarProductoForm(request.GET)

        if form.is_valid():
            # Obtenemos el texto de búsqueda y las marcas seleccionadas del formulario.
            texto_busqueda = form.cleaned_data.get('texto', '').lower()
            marcas_seleccionadas = form.cleaned_data.get('marca', [])
            print("Texto de búsqueda:", texto_busqueda)
            print("Marcas seleccionadas:", marcas_seleccionadas)
            # Filtramos los productos basados en las opciones de búsqueda.
            queryset = Producto.objects.filter(unidades__gt=0)

            if texto_busqueda:
                queryset = queryset.filter(nombre__icontains=texto_busqueda)

            if marcas_seleccionadas:
                queryset = queryset.filter(marca__in=marcas_seleccionadas)
        else:
            print("El formulario no es válido:", form.errors)
            queryset = Producto.objects.filter(unidades__gt=0)
        # Filtramos productos VIP si el usuario está autenticado como cliente.
        user = request.user
        if user.is_authenticated and verify_client(user):
            cliente = Cliente.objects.get(user=user)
            if not cliente.vip:
                queryset = queryset.filter(vip=False)
        else:
            queryset = queryset.filter(vip=False)
        # Pasamos los productos y el formulario al contexto.
        context = {
            'productos': queryset,
            'form': form,
        }
        return render(request, self.template_name, context)

class CrearDireccionView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    # Especificamos el modelo, la plantilla y la URL de redirección después de crear una dirección.
    model = Direccion
    template_name = 'tienda/plantilla_para_formulario.html'
    success_url = reverse_lazy('client_info')
    # Especificamos los campos que se mostrarán en el formulario.
    fields = ['tipo_via', 'nombre', 'numero', 'envio', 'facturacion']
    # Método para verificar si el usuario es un cliente.
    def test_func(self):
        return verify_client(self.request.user)
    # Método para procesar el formulario cuando es válido.
    def form_valid(self, form):
        # Obtenemos el cliente asociado al usuario actual.
        cliente = Cliente.objects.filter(user__id=self.request.user.id).first()
        # Guardamos la dirección asociada al cliente.
        instance = form.save(commit=False)
        instance.cliente = cliente
        instance.save()

        return super().form_valid(form)

class ModificarDireccionView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    # Especificamos el modelo, la plantilla, los campos y la URL de redirección después de modificar una dirección.
    model = Direccion
    template_name = 'tienda/plantilla_para_formulario.html'
    fields = ['tipo_via', 'nombre', 'numero', 'envio', 'facturacion']
    success_url = reverse_lazy('client_info')
    # Método para verificar si el usuario es el propietario de la dirección.
    def test_func(self):
        current_user = self.request.user
        result = False
        direccion = get_object_or_404(Direccion, pk=self.kwargs["pk"])
        if direccion.cliente.user.id == current_user.id:
            result = True
        return result

class EliminarDireccionView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    # Especificamos el modelo, la plantilla y la URL de redirección después de eliminar una dirección.
    model = Direccion
    template_name = 'tienda/cliente/datos_cliente/eliminar_direccion.html'
    success_url = reverse_lazy('client_info')
    # Método para verificar si el usuario es el propietario de la dirección.
    def test_func(self):
        current_user = self.request.user
        result = False
        direccion = get_object_or_404(Direccion, pk=self.kwargs["pk"])
        if direccion.cliente.user.id == current_user.id:
            result = True
        return result


class CrearTarjetaDePagoView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    # Especificamos el modelo, la plantilla y la URL de redirección después de crear una tarjeta de pago.
    model = TarjetaDePago
    template_name = 'tienda/plantilla_para_formulario.html'
    success_url = reverse_lazy('client_info')
    # Especificamos los campos que se mostrarán en el formulario.
    fields = ['numero', 'tipo', 'titular', 'fecha_caducidad']
    # Método para verificar si el usuario es un cliente.
    def test_func(self):
        return verify_client(self.request.user)
    # Método para modificar el widget del campo de fecha de caducidad.
    def get_form(self, form_class=None):
        form = super(CrearTarjetaDePagoView, self).get_form()
        form.fields['fecha_caducidad'].widget.input_type = 'date'
        return form
    # Método para procesar el formulario cuando es válido.
    def form_valid(self, form):
        # Obtenemos el cliente asociado al usuario actual.
        cliente = Cliente.objects.filter(user__id=self.request.user.id).first()
        # Guardamos la tarjeta de pago asociada al cliente.
        instance = form.save(commit=False)
        instance.cliente = cliente
        instance.save()

        return super().form_valid(form)

class ModificarTarjetaDePagoView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    # Especificamos el modelo, la plantilla, los campos y la URL de redirección después de modificar una tarjeta de pago.
    model = TarjetaDePago
    template_name = 'tienda/plantilla_para_formulario.html'
    fields = ['numero', 'tipo', 'titular', 'fecha_caducidad']
    success_url = reverse_lazy('client_info')
    # Método para verificar si el usuario es el propietario de la tarjeta de pago.
    def test_func(self):
        current_user = self.request.user
        result = False
        tarjeta_pago = get_object_or_404(TarjetaDePago, pk=self.kwargs["pk"])
        if tarjeta_pago.cliente.user.id == current_user.id:
            result = True
        return result

class EliminarTarjetaDePagoView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    # Especificamos el modelo, la plantilla y la URL de redirección después de eliminar una tarjeta de pago.
    model = TarjetaDePago
    template_name = 'tienda/cliente/datos_cliente/eliminar_tarjeta_de_pago.html'
    success_url = reverse_lazy('client_info')
    # Método para verificar si el usuario es el propietario de la tarjeta de pago.
    def test_func(self):
        current_user = self.request.user
        result = False
        tarjeta_pago = get_object_or_404(TarjetaDePago, pk=self.kwargs["pk"])
        if tarjeta_pago.cliente.user.id == current_user.id:
            result = True
        return result

class InformacionDelClienteView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    # Especificamos el modelo y la plantilla para la vista de información del cliente.
    model = Cliente
    template_name = 'tienda/cliente/client_info.html'
    # Método para obtener el objeto Cliente asociado al usuario actual.
    def get_object(self, queryset=None):
        return get_object_or_404(Cliente, user=self.request.user)
    # Método para obtener el contexto de la vista.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtenemos las compras, direcciones y tarjetas de pago del cliente.
        context['compras'] = Compra.objects.filter(cliente__user_id=self.object.user.id)
        context['direcciones'] = Direccion.objects.filter(cliente__user_id=self.object.user.id)
        context['tarjetas_pago'] = TarjetaDePago.objects.filter(cliente__user_id=self.object.user.id)
        return context
    # Método para verificar si el usuario es un cliente.
    def test_func(self):
        return verify_client(self.request.user)

class CrearValoracionesView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    # Especificamos el modelo, la plantilla y los campos para la creación de valoraciones.
    model = Valoracion
    template_name = 'tienda/plantilla_para_formulario.html'
    fields = ['puntuacion', 'comentario']
    # Método para verificar si el usuario puede crear una valoración para un producto.
    def test_func(self):
        current_user = self.request.user
        productocompra = get_object_or_404(ProductoCompra, pk=self.kwargs.get('pk'))
        valoracion_exists = Valoracion.objects.filter(productocompra_id=productocompra.id).first()
        result = False

        if productocompra.compra.cliente.user.id == current_user.id and not valoracion_exists:
            result = True

        return result
    # Método para procesar el formulario cuando es válido.
    def form_valid(self, form):
        productocompra = get_object_or_404(ProductoCompra, pk=self.kwargs.get('pk'))
        instance = form.save(commit=False)
        instance.productocompra = productocompra
        instance.save()
        return super().form_valid(form)
    # Método para obtener la URL.
    def get_success_url(self):
        try:
            next_page = self.request.GET['next']
        except:
            next_page = "/"
        return next_page

class ModificarValoracionesView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    # Especificamos el modelo, la plantilla y los campos para modificar una valoración.
    model = Valoracion
    template_name = 'tienda/plantilla_para_formulario.html'
    fields = ['puntuacion', 'comentario']
    # Método para verificar si el usuario puede modificar una valoración.
    def test_func(self):
        current_user = self.request.user
        result = False
        valoracion = get_object_or_404(Valoracion, pk=self.kwargs["pk"])
        if (current_user.has_perm('tienda.can_edit_commentary')
                or valoracion.productocompra.compra.cliente.user.id == current_user.id):
            result = True
        return result
    # Método para obtener la URL.
    def get_success_url(self):
        try:
            next_page = self.request.GET['next']
        except:
            next_page = "/"
        return next_page

class ModificarSaldoView(UpdateView):
    # Especificamos el modelo, la plantilla, el formulario y la URL de redirección después de modificar el saldo.
    model = Cliente
    template_name = 'tienda/plantilla_para_formulario.html'
    form_class = ModificarSaldoForm
    success_url = reverse_lazy('client_info')
    # Método para obtener el objeto Cliente a partir del ID del cliente.
    def get_object(self, queryset=None):
        cliente_id = self.kwargs.get('cliente_id')
        return Cliente.objects.get(id=cliente_id)

class ModificarContrasenaView(LoginRequiredMixin, FormView):
    # Especificamos la plantilla, el formulario y la URL de redirección después de modificar la contraseña.
    template_name = 'tienda/plantilla_para_formulario.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('client_info')
    # Método para obtener los argumentos del formulario.
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    # Método para procesar el formulario cuando es válido.
    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        return super().form_valid(form)

class ModificarDatosDelClienteView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    # Especificamos el modelo, la plantilla, la URL de redirección y los campos para modificar los datos del cliente.
    model = User
    template_name = 'tienda/plantilla_para_formulario.html'
    success_url = reverse_lazy('client_info')
    fields = ['first_name', 'last_name', 'email']
    # Método para verificar si el usuario tiene permiso para modificar los datos del cliente.
    def test_func(self):
        result = True
        current_user = self.request.user
        request_user_id = self.kwargs.get('pk')

        if not current_user.id == request_user_id:
            result = False
            messages.add_message(self.request, messages.ERROR, "No tienes permiso para acceder a este perfil.")
        return result