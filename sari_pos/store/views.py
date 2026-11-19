from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db import transaction
from django.db.models import F, Value
from django.db.models.functions import Greatest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.contrib.auth.models import User

from .models import Product, Sale, SaleItem


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _cart_items(request):
    """Resolve the session cart into (items, total). Ignores inactive/missing products."""
    cart = request.session.get("cart", {})
    items, total = [], Decimal("0.00")
    products = Product.objects.filter(
        id__in=[int(k) for k in cart], is_active=True
    )
    for p in products:
        qty = cart.get(str(p.id), 0)
        if qty <= 0:
            continue
        sub = p.price * qty
        total += sub
        items.append({"product": p, "qty": qty, "subtotal": sub})
    return items, total


def _safe_next(request, fallback="pos"):
    """Redirect to ?next=… if it looks like a local path, else to fallback view name."""
    nxt = request.POST.get("next") or ""
    return nxt if nxt.startswith("/") else fallback


# ------------------------------------------------------------------
# POS screen (Auto-logs in instant user if not authenticated)
# ------------------------------------------------------------------
def pos(request):
    if not request.user.is_authenticated:
        user, _ = User.objects.get_or_create(
            username="pos_admin",
            defaults={"is_staff": True, "is_superuser": True}
        )
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

    q = request.GET.get("q", "").strip()
    products = Product.objects.filter(is_active=True)
    if q:
        products = products.filter(name__icontains=q)
    items, total = _cart_items(request)
    return render(request, "store/pos.html", {
        "products": products,
        "q": q,
        "items": items,
        "total": total,
    })


# ------------------------------------------------------------------
# Cart actions
# ------------------------------------------------------------------
@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    cart = request.session.get("cart", {})
    key = str(product.id)
    cart[key] = min(cart.get(key, 0) + 1, 999)
    request.session["cart"] = cart
    return redirect(_safe_next(request))


@require_POST
def set_qty(request, pk):
    cart = request.session.get("cart", {})
    key = str(pk)
    try:
        qty = int(request.POST.get("qty", "1"))
    except ValueError:
        qty = 1
    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = min(qty, 999)
    request.session["cart"] = cart
    return redirect("pos")


@require_POST
def remove_from_cart(request, pk):
    cart = request.session.get("cart", {})
    cart.pop(str(pk), None)
    request.session["cart"] = cart
    return redirect("pos")


@require_POST
def clear_cart(request):
    request.session["cart"] = {}
    return redirect("pos")


# ------------------------------------------------------------------
# Checkout
# ------------------------------------------------------------------
@require_POST
def checkout(request):
    items, total = _cart_items(request)
    if not items:
        messages.error(request, "Cart is empty.")
        return redirect("pos")

    try:
        cash = Decimal(request.POST.get("cash", "0"))
    except InvalidOperation:
        messages.error(request, "Invalid cash amount.")
        return redirect("pos")

    if cash < total:
        messages.error(request, f"Cash ₱{cash} is less than total ₱{total}.")
        return redirect("pos")

    change = cash - total

    with transaction.atomic():
        sale = Sale.objects.create(total=total, cash=cash, change=change)
        for it in items:
            p = it["product"]
            SaleItem.objects.create(
                sale=sale,
                product=p,
                name=p.name,
                price=p.price,
                quantity=it["qty"],
                subtotal=it["subtotal"],
            )
            if p.stock > 0:
                Product.objects.filter(pk=p.pk).update(
                    stock=Greatest(F("stock") - it["qty"], Value(0))
                )

    request.session["cart"] = {}
    return redirect("receipt", pk=sale.pk)


def receipt(request, pk):
    sale = get_object_or_404(
        Sale.objects.prefetch_related("items"), pk=pk
    )
    return render(request, "store/receipt.html", {"sale": sale})


def sales_list(request):
    return render(request, "store/sales.html", {
        "sales": Sale.objects.all()[:100],
    })


# ------------------------------------------------------------------
# Price checker
# ------------------------------------------------------------------
def price_checker(request):
    q = request.GET.get("q", "").strip()
    results = Product.objects.none()
    if q:
        results = Product.objects.filter(
            is_active=True, name__icontains=q
        )[:30]
    return render(request, "store/price_checker.html", {"q": q, "results": results})


# ------------------------------------------------------------------
# Product Management (Instant / No Restrictions)
# ------------------------------------------------------------------
def add_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        stock = request.POST.get("stock", 0)
        unit = request.POST.get("unit", "pcs")
        if name and price:
            Product.objects.create(
                name=name,
                price=price,
                stock=stock,
                unit=unit,
                is_active=True
            )
            return redirect('pos')
    return render(request, "store/product_form.html", {"action": "Add"})


def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock", 0)
        product.unit = request.POST.get("unit", "pcs")
        product.save()
        return redirect('pos')
    return render(request, "store/product_form.html", {"action": "Edit", "product": product})


def deactivate_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = False
    product.save()
    return redirect('pos')


def instant_login(request):
    user, _ = User.objects.get_or_create(
        username="pos_admin",
        defaults={"is_staff": True, "is_superuser": True}
    )
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    return redirect('pos')