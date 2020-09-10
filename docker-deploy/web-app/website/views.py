from django.core.mail import send_mail
from django.conf import settings

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Product, Order, Cart, Money, Wishlist
from .forms import ProductSearchForm, UserRegisterForm, UserUpdateForm, CartForm, CheckoutForm,RechargeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

import socket
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
from . import world_amazon_pb2 as world
from . import amazon_client_pb2 as amazon

HOST = "vcm-14285.vm.duke.edu"
#HOST = "vcm-13676.vm.duke.edu"
PORT = 33333
ADDR = (HOST, PORT)

def home(request):
    context = {
        'products': Product.objects.all()
    }
    return render(request, 'website/home.html', context)

def index(request):
    return render(request, 'website/index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            
            messages.success(request, f'You are now able to log in!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'website/register.html',{'form':form})


@login_required
def account(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('account')
        else:
            messages.warning(request,f'Your message is incorrect!')
            return redirect('account')
    else:
        u_form = UserUpdateForm(instance=request.user)
        context = {
            'u_form': u_form,
        }
        return render(request, 'website/account.html', context)
    

class ProductListView(ListView):
    model = Product
    template_name = 'website/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'products'
    ordering = ['productID']
    paginate_by = 5


def productSearch(request):
    if request.method == 'POST':
        form = ProductSearchForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['description'] 
            
            context = {
                'products': Product.objects.all().filter(description__icontains=name) 
            }
            return render(request, 'website/product_results.html',context)
    else:
        form = ProductSearchForm()
        return render(request, 'website/search.html', {'form':form})


class SearchListView(ListView):
    model = Product
    template_name = 'website/product_results.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'products'
    ordering = ['productID']
    paginate_by = 5

    
class ProductDetailView(DetailView):
    model = Product
    template_name = 'website/product_detail.html'

@login_required()
def RechargeView(request):
    money = Money.objects.filter(user=request.user).first()
    if not money:
        Money.objects.create(user=request.user, recharge=0)
    if request.method == 'POST':
        form = RechargeForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['recharge']
            money.recharge+=amount
            money.save()
            return redirect('recharge')
    else:
        form = RechargeForm()
    return render(request, 'website/recharge.html', {'object':money,'form':form})

 
@login_required()
def addToCart(request, pk):
    if request.method == 'POST':
        form = CartForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data['count']
            user = request.user
            item = Product.objects.get(productID=pk)
            cart_price = qty*item.price
            check_cart = Cart.objects.filter(owner=user, product=item, order_id=0).first()
            if not check_cart:
                Cart.objects.create(owner=user, product=item, count=qty, total_price=cart_price)
            else:
                check_cart.count += qty
                check_cart.total_price += qty*item.price
                check_cart.save()
            messages.success(request, f'Product has been added to cart!')
            return redirect('cart_page')
        
    else:
        form = CartForm()
        return render(request,'website/add_cart.html', {'form':form})

    
@login_required()
def addToList(request, pk):
    user = request.user
    product_toadd = Product.objects.get(pk=pk)
    in_list = Wishlist.objects.all().filter(user=request.user).filter(product=product_toadd).first()
    if not in_list:
        Wishlist.objects.create(user=user, product=product_toadd)
    messages.success(request, f'Product has been added to wishlist!')
    return redirect(reverse('product-detail', kwargs = {'pk': pk}))


class WishListView(LoginRequiredMixin,ListView):
    model = Wishlist
    template_name = 'website/wishlist.html'
    context_object_name = 'items'
    ordering = '-id'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        return Wishlist.objects.filter(user=user).order_by('-id')

    
@login_required()
def CartPage(request):
    user = request.user
    cart_items = Cart.objects.all().filter(owner=user).filter(order_id=0)
    idle = False
    total_price = 0
    if not cart_items.exists():
        idle = True
    else:
        for item in cart_items:
            total_price += item.total_price
    print(idle)
    context = {
        'items': Cart.objects.all().filter(owner=user).filter(order_id=0),
        'null': idle,
        'price': total_price
    }
    
    return render(request, 'website/cart_page.html', context)
    

@login_required()
def deleteFromCart(request, pk):
    item = Cart.objects.get(pk=pk)
    item.delete()
    messages.success(request, f'Product has been removed from cart!')

    return redirect('cart_page')


@login_required()
def checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            x = form.cleaned_data['coordinateX']
            y = form.cleaned_data['coordinateY']
            user = request.user
            cart_items = Cart.objects.all().filter(owner=user).filter(order_id=0)
            total_price = 0
            for item in cart_items:
                total_price += item.total_price
            balance = Money.objects.filter(user=user).first()
            if not balance:
                messages.warning(request,f'Your balance is not sufficient!')
                return redirect('recharge')
            if (balance.recharge < total_price):
                messages.warning(request,f'Your balance is not sufficient!')
                return redirect('recharge')
            this_order = Order.objects.create(owner=user, coordinateX=x, coordinateY=y)
            ID = this_order.id
            curr_recharge = balance.recharge - total_price
            balance.recharge = curr_recharge
            balance.save()
            cart_items.update(order_id=ID)
            
            amazonSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            amazonSock.connect((socket.gethostbyname(HOST),PORT))
            product_message = amazon.AOrder()
            product_message.orderid = ID
            product_message.userid = user.id
            product_message.x = x
            product_message.y = y
            cart_items = Cart.objects.all().filter(owner=user).filter(order_id=ID)
            for item in cart_items:
                print(item.product.description)
                thing = product_message.things.add()
                thing.id = item.product.productID
                thing.description = item.product.description
                thing.count = item.count
            messageToSend = product_message.SerializeToString()
            
            _EncodeVarint(amazonSock.send, len(messageToSend), None)
            amazonSock.send(messageToSend)
            amazonSock.close()

            from_email= settings.EMAIL_HOST_USER
            subject = 'Your order is created!'
            message = 'Thank you for using MINIAMAZON\n'
            message += 'Your order is confirmed! Please wait for delivery!'

            to_list = [user.email,from_email]
            send_mail(subject,message,from_email,to_list,fail_silently=False)            
            
            return redirect('myorder')
            
    else:
        form = CheckoutForm()
        return render(request, 'website/checkout.html', {'form':form})

    
class OrderListView(LoginRequiredMixin,ListView):
    model = Order
    template_name = 'website/orders.html'
    context_object_name = 'orders'
    ordering = ['-timeCreated']
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(owner=user).order_by('-timeCreated')


def OrderDetail(request, pk):
    user = request.user
    context = {
        'order': Order.objects.get(pk=pk),
        'items': Cart.objects.all().filter(owner=user).filter(order_id=pk)
    }
    return render(request, 'website/order_detail.html', context)


def query_status(request, pk):
    context = {
        'order':Order.objects.get(pk=pk) 
    }
    return render(request, 'website/order_status.html', context)
    
