from django.urls import path
from . import views

urlpatterns = [
    path("", views.pos, name="pos"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/set/<int:pk>/", views.set_qty, name="set_qty"),
    path("cart/remove/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("receipt/<int:pk>/", views.receipt, name="receipt"),
    path("sales/", views.sales_list, name="sales_list"),
    path("price-checker/", views.price_checker, name="price_checker"),
    # Product Management URLs
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/deactivate/<int:pk>/', views.deactivate_product, name='deactivate_product'),
    path('instant-login/', views.instant_login, name='instant_login'),
]