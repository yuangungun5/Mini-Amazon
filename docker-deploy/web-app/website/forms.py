from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Order,Cart,Money

class ProductSearchForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['description']

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['count']

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['coordinateX', 'coordinateY']

class RechargeForm(forms.ModelForm):
    class Meta:
        model = Money
        fields = ['recharge']