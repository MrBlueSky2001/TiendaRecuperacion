from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3, ReCaptchaV2Checkbox

from .models import Producto, Marca, Cliente, TarjetaDePago, Direccion
from django.forms import ModelChoiceField
from django.utils.translation import gettext_lazy as _


class CompraForm(forms.Form):
    unidades = forms.IntegerField(min_value=1, label=_("units"))
    id_producto = forms.IntegerField(widget=forms.HiddenInput())

    # def clean(self):
    #     cleaned_data = super().clean()
    #     unidades_ingresadas = cleaned_data.get("unidades")
    #     id_producto = cleaned_data.get("id_producto")
    #     producto = Producto.objects.get(pk=id_producto)
    #
    #     if unidades_ingresadas > producto.unidades:
    #         raise ValidationError("No hay suficientes unidades disponibles para este producto.")


class ClienteRegistrationForm(UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    # https://pypi.org/project/django-recaptcha/

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class CheckoutForm(forms.Form):
    metodo_pago = forms.ModelChoiceField(widget=forms.Select, required=True, queryset=None, label=_("payment_method"))
    direccion_envio = forms.ModelChoiceField(widget=forms.Select, required=True, queryset=None, label=_("shipping_address"))
    direccion_facturacion = forms.ModelChoiceField(widget=forms.Select, required=True, queryset=None, label=_("payment_address"))


class CarritoForm(forms.Form):
    id_producto = forms.IntegerField(widget=forms.HiddenInput())
    unidades = forms.IntegerField(min_value=1)

class FormBuscarProducto(forms.Form):
    texto = forms.CharField(required=False, widget=forms.TextInput({'class': 'form-control', 'placeholder': 'Buscar ...'}))
    marca = forms.ModelMultipleChoiceField(required=False, queryset=Marca.objects.all(), widget=forms.CheckboxSelectMultiple)