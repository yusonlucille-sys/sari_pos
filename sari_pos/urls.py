"""
URL configuration for sari_pos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('instant-login/', views.instant_login, name='instant_login'),

    # Core POS & Management URLs
    path('', views.pos, name='pos'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('set-qty/<int:pk>/', views.set_qty, name='set_qty'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('receipt/<int:pk>/', views.receipt, name='receipt'),
    path('sales/', views.sales_list, name='sales_list'),
    path('price-checker/', views.price_checker, name='price_checker'),
    
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/deactivate/<int:pk>/', views.deactivate_product, name='deactivate_product'),
]