from decimal import Decimal
from .models import Product, SiteSetting


CART_SESSION_KEY = "cart"


def get_cart(request):
    cart = request.session.get(CART_SESSION_KEY)
    if cart is None:
        cart = {}
        request.session[CART_SESSION_KEY] = cart
    return cart


def save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def add_to_cart_session(request, product_id, qty):
    cart = get_cart(request)
    key = str(product_id)
    current_qty = cart.get(key, 0)
    cart[key] = current_qty + qty
    save_cart(request, cart)


def update_cart_item(request, product_id, qty):
    cart = get_cart(request)
    key = str(product_id)
    if qty > 0:
        cart[key] = qty
    else:
        if key in cart:
            del cart[key]
    save_cart(request, cart)


def remove_cart_item(request, product_id):
    cart = get_cart(request)
    key = str(product_id)
    if key in cart:
        del cart[key]
        save_cart(request, cart)


def clear_cart(request):
    if CART_SESSION_KEY in request.session:
        del request.session[CART_SESSION_KEY]
        request.session.modified = True


def get_cart_items(request):
    cart = get_cart(request)
    product_ids = [int(pk) for pk in cart.keys()]
    products = Product.objects.filter(id__in=product_ids, is_active=True)
    items = []
    subtotal = Decimal("0.00")
    for product in products:
        qty = cart.get(str(product.id), 0)
        if qty <= 0:
            continue
        line_total = product.price * qty
        subtotal += line_total
        items.append(
            {
                "product": product,
                "qty": qty,
                "line_total": line_total,
            }
        )
    return items, subtotal


def get_site_setting():
    setting, created = SiteSetting.objects.get_or_create(id=1, defaults={"delivery_fee": Decimal("0.00")})
    return setting

