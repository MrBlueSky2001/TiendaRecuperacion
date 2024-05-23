import datetime
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core import serializers
from django.db import transaction
from django.db.models import Sum, F
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView, TemplateView, View, DetailView, CreateView, DeleteView, FormView
from django_filters.views import FilterView
from extra_views import FormSetView
from .forms import *
from .models import *
from django.forms import formset_factory


def verify_client(user):
    return Cliente.objects.filter(user=user).exists()

def welcome(request):
    return redirect('listado_comprar')

@method_decorator(staff_member_required, name='dispatch')
class EditarProductoView(UpdateView):
    model = Producto
    template_name = 'tienda/administrador/administrar_productos/editar_producto.html'
    fields = ['marca', 'nombre', 'modelo', 'unidades', 'precio', 'vip', 'image']
    success_url = reverse_lazy('listado_productos')

    def form_invalid(self, form):
        messages.add_message(self.request, messages.WARNING, "Error de formulario")

@method_decorator(staff_member_required, name='dispatch')
class EliminarProductoView(DeleteView):
    model = Producto
    template_name = 'tienda/administrador/administrar_productos/eliminar_producto.html'
    success_url = reverse_lazy('listado_productos')

@method_decorator(staff_member_required, name='dispatch')
class ListadoProductosView(ListView):
    model = Producto
    template_name = 'tienda/administrador/administrar_productos/listado_productos.html'
    queryset = Producto.objects.all()
    context_object_name = "productos"

@method_decorator(staff_member_required(), name='dispatch')
class CrearProductoView(CreateView):
    model = Producto
    template_name = 'tienda/plantilla_para_formulario.html'
    fields = ['marca', 'nombre', 'modelo', 'unidades', 'precio', 'vip', 'image']
    success_url = reverse_lazy('listado_productos')

@method_decorator(staff_member_required(), name='dispatch')
class ComprasClientesFilterView(ListView):
    template_name = 'tienda/administrador/informes/compras_clientes.html'
    context_object_name = "compras"
    form_class = BuscarCompraForm

    def get_queryset(self):
        queryset = Compra.objects.all()
        cliente = self.request.GET.get('cliente')
        if cliente:
            queryset = queryset.filter(cliente=cliente)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET)
        return context

@method_decorator(staff_member_required(), name='dispatch')
class InformesView(TemplateView):
    template_name = 'tienda/administrador/informes/informes.html'

@method_decorator(staff_member_required(), name='dispatch')
class ProductoPorMarcaFilterView(ListView):
    template_name = 'tienda/administrador/informes/productos_por_marca.html'
    context_object_name = "productos"
    model = Producto

    def get_queryset(self):
        queryset = super().get_queryset()
        marca_id = self.request.GET.get('marca_id')
        if marca_id:
            queryset = queryset.filter(marca_id=marca_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marcas'] = Marca.objects.all()
        return context

@method_decorator(staff_member_required(), name='dispatch')
class TopDiezClientesListView(ListView):
    template_name = 'tienda/administrador/informes/top_diez_clientes.html'
    context_object_name = "usuarios"
    queryset = Cliente.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuarios = Cliente.objects.filter(compra__isnull=False).annotate(
            sum_importes=Sum('compra__importe')
        ).order_by("-sum_importes")[:10]
        context['usuarios'] = usuarios
        return context

@method_decorator(staff_member_required(), name='dispatch')
class TopDiezProductosListView(ListView):
    template_name = 'tienda/administrador/informes/top_diez_productos.html'
    context_object_name = "productos"
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
    template_name = 'tienda/inicio_sesion/login.html'

    def form_valid(self, form):
        user = form.get_user()
        if verify_client(user):
            return_value = super().form_valid(form)
        else:
            messages.add_message(self.request, messages.WARNING, "No está registrado para iniciar sesión.")
            return_value = self.form_invalid(form)
        return return_value

    def get_success_url(self):
        try:
            next_page = self.request.GET['next']
        except:
            next_page = "/"
        return next_page

class ClienteLogoutView(LoginRequiredMixin, LogoutView):
    next_page = '/tienda'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages.add_message(self.request, messages.ERROR, "Sesión cerrada")
        return context

class ClienteSignUpView(CreateView):
    model = Cliente
    template_name = 'tienda/plantilla_para_formulario.html'
    success_url = reverse_lazy('tienda')
    form_class = RegistrarClienteForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        form_username = form.cleaned_data.get("username")
        user = User.objects.get(username=form_username)
        cliente = Cliente(vip=False, saldo=0, user=user)
        cliente.save()
        login(self.request, user)

        return response

class CarroCompraView(LoginRequiredMixin, UserPassesTestMixin, FormSetView):
    template_name = 'tienda/cliente/compra/carro.html'
    form_class = CarritoForm

    def formset_valid(self, formset):
        context = self.get_context_data()
        productoscompra = context['productoscompra']
        counter = 0

        for form, productocompra in zip(formset, productoscompra):
            productocompra.unidades = form.cleaned_data['unidades']
            counter += 1

        context['productoscompra'] = productoscompra

        if counter > 0:
            self.request.session['lista_productos_carrito'] = serializers.serialize('json', productoscompra)

        return super().formset_valid(formset)

    def test_func(self):
        return verify_client(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productoscompra = []

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
            initial = [{'id_producto': productocompra.producto.id, 'unidades': productocompra.unidades}
                       for productocompra in context['productoscompra']]
            context['formset'] = formset_factory(self.form_class, extra=len(productoscompra))(initial=initial)

        return context

class ComprobarCarro:
    def dispatch(self, request, *args, **kwargs):
        if 'lista_productos_carrito' not in self.request.session:
            messages.add_message(self.request, messages.ERROR, "Carrito vacío")
            return self.redirect_tienda()
        return super().dispatch(request, *args, **kwargs)

    def redirect_tienda(self):
        return HttpResponseRedirect(reverse_lazy('tienda'))

class CheckoutView(ComprobarCarro, LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'tienda/cliente/compra/checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('tienda')

    def test_func(self):
        return verify_client(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productoscompra = []
        precio_total = 0
        if 'lista_productos_carrito' in self.request.session:
            des_list = serializers.deserialize('json', self.request.session['lista_productos_carrito'])
            for productocompra in des_list:
                productoscompra.append(productocompra.object)
                precio_total += (productocompra.object.precio * productocompra.object.unidades)
        print("Productos en el carrito:", productoscompra)
        context['productoscompra'] = productoscompra
        context['precio_total'] = precio_total
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['metodo_pago'].queryset = TarjetaDePago.objects.filter(cliente__user_id=self.request.user.id)
        form.fields['direccion_envio'].queryset = Direccion.objects.filter(cliente__user_id=self.request.user.id, envio=True)
        form.fields['direccion_facturacion'].queryset = Direccion.objects.filter(cliente__user_id=self.request.user.id, facturacion=True)
        return form

    @transaction.atomic
    def form_valid(self, form):
        form_valid = super().form_valid(form)
        context = self.get_context_data()
        productoscompra = context['productoscompra']
        cliente = Cliente.objects.filter(user=self.request.user).first()

        for productocompra in productoscompra:
            if productocompra.unidades > productocompra.producto.unidades:
                messages.add_message(self.request, messages.ERROR, "Compra inválida")
                return redirect('checkout')

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

            for productocompra in productoscompra:
                productocompra.compra = compra
                productocompra.producto.unidades -= productocompra.unidades
                productocompra.producto.save()
                productocompra.save()

            del self.request.session['lista_productos_carrito']
            messages.add_message(self.request, messages.SUCCESS, "Compra realizada")

        return form_valid

class HistorialView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Compra
    template_name = 'tienda/cliente/compra/historial.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productoscompra'] = ProductoCompra.objects.filter(compra_id=self.object.id).select_related(
            'valoracion')
        return context

    def test_func(self):
        result = False
        compra = get_object_or_404(Compra, pk=self.kwargs["pk"])
        if verify_client(self.request.user) and compra.cliente.user.id == self.request.user.id:
            result = True
        return result

class DetallesDelProductoView(DetailView):
    model = Producto
    template_name = 'tienda/cliente/compra/detalle_del_producto.html'
    context_object_name = 'producto'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_anonymous and verify_client(request.user):
            form = CompraForm(initial={'id_producto': self.object.id})
        else:
            form = None
        valoraciones = Valoracion.objects.filter(productocompra__producto_id=self.object.id)
        context = {'producto': self.object, 'form': form, 'valoraciones': valoraciones}
        return render(request, self.template_name, context)

class AgregarProductoCarroView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class = CompraForm

    def test_func(self):
        return verify_client(self.request.user)

    def form_valid(self, form):
        lista_productos = []

        if 'lista_productos_carrito' in self.request.session:
            des_list = serializers.deserialize('json', self.request.session['lista_productos_carrito'])
            for productocompra in des_list:
                lista_productos.append(productocompra.object)

        unidades = form.cleaned_data['unidades']
        id_producto = form.cleaned_data['id_producto']
        producto = Producto.objects.filter(id=id_producto).first()

        if any(miProducto.producto.id == producto.id for miProducto in lista_productos):
            for miProducto in lista_productos:
                if miProducto.producto.id == producto.id:
                    miProducto.unidades = miProducto.unidades + int(unidades)
        else:
            nuevo_producto = ProductoCompra(producto=producto, compra=None, unidades=unidades,
                                            precio=producto.precio)
            lista_productos.append(nuevo_producto)

        self.request.session['lista_productos_carrito'] = serializers.serialize('json', lista_productos)

        messages.add_message(self.request, messages.SUCCESS, "Añadido al carrito")
        return redirect(self.get_success_url())

    def get_success_url(self):
        try:
            next_page = self.request.GET['next']
        except:
            next_page = "/"
        return next_page

class EliminarProductoCarroView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return verify_client(self.request.user)

    def get(self, request, pk):
        productoscompra = []
        if 'lista_productos_carrito' in self.request.session:
            des_list = serializers.deserialize('json', self.request.session['lista_productos_carrito'])
            for productocompra in des_list:
                if not productocompra.object.uuid == pk:
                    productoscompra.append(productocompra.object)
            if len(productoscompra) > 0:
                self.request.session['lista_productos_carrito'] = serializers.serialize('json', productoscompra)
            else:
                del self.request.session['lista_productos_carrito']
        return redirect('carrito')

class ListadoProductosCompraFilterView(FilterView):
    template_name = 'tienda/cliente/compra/listado_productos_compra.html'
    context_object_name = "productos"

    def get(self, request, *args, **kwargs):
        form = BuscarProductoForm(request.GET)

        if form.is_valid():
            texto_busqueda = form.cleaned_data.get('texto', '').lower()
            marcas_seleccionadas = form.cleaned_data.get('marca', [])
            print("Texto de búsqueda:", texto_busqueda)
            print("Marcas seleccionadas:", marcas_seleccionadas)

            queryset = Producto.objects.filter(unidades__gt=0)

            if texto_busqueda:
                queryset = queryset.filter(nombre__icontains=texto_busqueda)

            if marcas_seleccionadas:
                queryset = queryset.filter(marca__in=marcas_seleccionadas)
        else:
            print("El formulario no es válido:", form.errors)
            queryset = Producto.objects.filter(unidades__gt=0)

        user = request.user
        if user.is_authenticated and verify_client(user):
            cliente = Cliente.objects.get(user=user)
            if not cliente.vip:
                queryset = queryset.filter(vip=False)
        else:
            queryset = queryset.filter(vip=False)

        context = {
            'productos': queryset,
            'form': form,
        }
        return render(request, self.template_name, context)

class CrearDireccionView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Direccion
    template_name = 'tienda/plantilla_para_formulario.html'
    success_url = reverse_lazy('client_info')
    fields = ['tipo_via', 'nombre', 'numero', 'envio', 'facturacion']

    def test_func(self):
        return verify_client(self.request.user)

    def form_valid(self, form):
        cliente = Cliente.objects.filter(user__id=self.request.user.id).first()
        instance = form.save(commit=False)
        instance.cliente = cliente
        instance.save()

        return super().form_valid(form)

class ModificarDireccionView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Direccion
    template_name = 'tienda/plantilla_para_formulario.html'
    fields = ['tipo_via', 'nombre', 'numero', 'envio', 'facturacion']
    success_url = reverse_lazy('client_info')

    def test_func(self):
        current_user = self.request.user
        result = False
        direccion = get_object_or_404(Direccion, pk=self.kwargs["pk"])
        if direccion.cliente.user.id == current_user.id:
            result = True
        return result

class EliminarDireccionView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Direccion
    template_name = 'tienda/cliente/datos_cliente/eliminar_direccion.html'
    success_url = reverse_lazy('client_info')

    def test_func(self):
        current_user = self.request.user
        result = False
        direccion = get_object_or_404(Direccion, pk=self.kwargs["pk"])
        if direccion.cliente.user.id == current_user.id:
            result = True
        return result


class CrearTarjetaDePagoView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = TarjetaDePago
    template_name = 'tienda/plantilla_para_formulario.html'
    success_url = reverse_lazy('client_info')
    fields = ['numero', 'tipo', 'titular', 'fecha_caducidad']

    def test_func(self):
        return verify_client(self.request.user)

    def get_form(self, form_class=None):
        form = super(CrearTarjetaDePagoView, self).get_form()
        form.fields['fecha_caducidad'].widget.input_type = 'date'
        return form

    def form_valid(self, form):
        cliente = Cliente.objects.filter(user__id=self.request.user.id).first()
        instance = form.save(commit=False)
        instance.cliente = cliente
        instance.save()

        return super().form_valid(form)

class ModificarTarjetaDePagoView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TarjetaDePago
    template_name = 'tienda/plantilla_para_formulario.html'
    fields = ['numero', 'tipo', 'titular', 'fecha_caducidad']
    success_url = reverse_lazy('client_info')

    def test_func(self):
        current_user = self.request.user
        result = False
        tarjeta_pago = get_object_or_404(TarjetaDePago, pk=self.kwargs["pk"])
        if tarjeta_pago.cliente.user.id == current_user.id:
            result = True
        return result

class EliminarTarjetaDePagoView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TarjetaDePago
    template_name = 'tienda/cliente/datos_cliente/eliminar_tarjeta_de_pago.html'
    success_url = reverse_lazy('client_info')

    def test_func(self):
        current_user = self.request.user
        result = False
        tarjeta_pago = get_object_or_404(TarjetaDePago, pk=self.kwargs["pk"])
        if tarjeta_pago.cliente.user.id == current_user.id:
            result = True
        return result

class InformacionDelClienteView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Cliente
    template_name = 'tienda/cliente/client_info.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Cliente, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['compras'] = Compra.objects.filter(cliente__user_id=self.object.user.id)
        context['direcciones'] = Direccion.objects.filter(cliente__user_id=self.object.user.id)
        context['tarjetas_pago'] = TarjetaDePago.objects.filter(cliente__user_id=self.object.user.id)
        return context

    def test_func(self):
        return verify_client(self.request.user)

class CrearValoracionesView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Valoracion
    template_name = 'tienda/plantilla_para_formulario.html'
    fields = ['puntuacion', 'comentario']

    def test_func(self):
        current_user = self.request.user
        productocompra = get_object_or_404(ProductoCompra, pk=self.kwargs.get('pk'))
        valoracion_exists = Valoracion.objects.filter(productocompra_id=productocompra.id).first()
        result = False

        if productocompra.compra.cliente.user.id == current_user.id and not valoracion_exists:
            result = True

        return result

    def form_valid(self, form):
        productocompra = get_object_or_404(ProductoCompra, pk=self.kwargs.get('pk'))
        instance = form.save(commit=False)
        instance.productocompra = productocompra
        instance.save()
        return super().form_valid(form)

    def get_success_url(self):
        try:
            next_page = self.request.GET['next']
        except:
            next_page = "/"
        return next_page

class ModificarValoracionesView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Valoracion
    template_name = 'tienda/plantilla_para_formulario.html'
    fields = ['puntuacion', 'comentario']

    def test_func(self):
        current_user = self.request.user
        result = False
        valoracion = get_object_or_404(Valoracion, pk=self.kwargs["pk"])
        if (current_user.has_perm('tienda.can_edit_commentary')
                or valoracion.productocompra.compra.cliente.user.id == current_user.id):
            result = True
        return result

    def get_success_url(self):
        try:
            next_page = self.request.GET['next']
        except:
            next_page = "/"
        return next_page

class ModificarSaldoView(UpdateView):
    model = Cliente
    template_name = 'tienda/plantilla_para_formulario.html'
    form_class = ModificarSaldoForm
    success_url = reverse_lazy('client_info')

    def get_object(self, queryset=None):
        cliente_id = self.kwargs.get('cliente_id')
        return Cliente.objects.get(id=cliente_id)

class ModificarContrasenaView(LoginRequiredMixin, FormView):
    template_name = 'tienda/plantilla_para_formulario.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('client_info')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        return super().form_valid(form)

class ModificarDatosDelClienteView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'tienda/plantilla_para_formulario.html'
    success_url = reverse_lazy('client_info')
    fields = ['first_name', 'last_name', 'email']

    def test_func(self):
        result = True
        current_user = self.request.user
        request_user_id = self.kwargs.get('pk')

        if not current_user.id == request_user_id:
            result = False
            messages.add_message(self.request, messages.ERROR, "No tienes permiso para acceder a este perfil.")
        return result