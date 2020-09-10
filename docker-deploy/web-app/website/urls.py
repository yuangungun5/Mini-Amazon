from django.urls import path
from django.contrib.auth import views as auth_views
from .views import ProductListView, SearchListView, ProductDetailView, OrderListView, WishListView
from . import views

urlpatterns = [
    path('home/', ProductListView.as_view(), name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='website/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='website/logout.html'), name='logout'),
    path('account/', views.account, name='account'),
    path('add_cart/<int:pk>/', views.addToCart, name='add_cart'),
    path('add_list/<int:pk>/', views.addToList, name='add_list'),
    path('wishlist/', WishListView.as_view(), name='wishlist'),
    path('cart_page/', views.CartPage, name='cart_page'),
    path('delete_cart/<int:pk>/', views.deleteFromCart, name='delete_cart'),
    path('checkout/', views.checkout, name='order-create'),
    path('orders/', OrderListView.as_view(), name='myorder'),
    path('order_status/<int:pk>/', views.query_status, name='query-status'),
    path('orders/<int:pk>/', views.OrderDetail, name='order-detail'),
    path('search/', views.productSearch, name='search'),
    path('product_results/', SearchListView.as_view(), name='product-results'),
    path('product_detail/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('recharge/', views.RechargeView, name='recharge'),
    path('', views.index, name='index'),
]
