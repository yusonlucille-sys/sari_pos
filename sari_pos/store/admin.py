from django.contrib import admin
from .models import Product, Sale, SaleItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "unit", "is_active", "updated_at")
    list_editable = ("price", "stock", "unit", "is_active")   # inline edit!
    list_filter = ("is_active",)
    search_fields = ("name",)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ("product", "name", "price", "quantity", "subtotal")


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "total", "cash", "change")
    inlines = [SaleItemInline]
    readonly_fields = ("total", "cash", "change")