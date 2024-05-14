from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from .models import Marca, Cliente
from django.utils.translation import gettext_lazy as _

class BuscarCompraForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), label='Cliente', required=False)

class RegistrarClienteForm(UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class BuscarProductoForm(forms.Form):
    texto = forms.CharField(required=False, widget=forms.TextInput({'class': 'form-control', 'placeholder': 'Buscar ...'}))
    marca = forms.ModelMultipleChoiceField(required=False, queryset=Marca.objects.all(), widget=forms.CheckboxSelectMultiple)

class CheckoutForm(forms.Form):
    metodo_pago = forms.ModelChoiceField(widget=forms.Select, required=True, queryset=None, label=_("payment_method"))
    direccion_envio = forms.ModelChoiceField(widget=forms.Select, required=True, queryset=None, label=_("shipping_address"))
    direccion_facturacion = forms.ModelChoiceField(widget=forms.Select, required=True, queryset=None, label=_("payment_address"))

class ModificarSaldoForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['saldo']

class CompraForm(forms.Form):
    unidades = forms.IntegerField(min_value=1, label=_("units"))
    id_producto = forms.IntegerField(widget=forms.HiddenInput())

class CarritoForm(forms.Form):
    id_producto = forms.IntegerField(widget=forms.HiddenInput())
    unidades = forms.IntegerField(min_value=1)