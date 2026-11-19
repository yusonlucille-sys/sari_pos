from django.contrib import admin

from .models import Product, Sale, SaleItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "unit", "is_active", "updated_at")
    list_editable = ("price", "stock", "unit", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("name",)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "name", "price", "quantity", "subtotal")


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "total", "cash", "change")
    readonly_fields = ("total", "cash", "change", "created_at")
    inlines = [SaleItemInline]
    ordering = ("-created_at",)


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ("id", "sale", "name", "quantity", "price", "subtotal")
    search_fields = ("name",)