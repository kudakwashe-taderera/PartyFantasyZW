from django.urls import reverse

from .utils import get_cart


def cart(request):
    cart = get_cart(request)
    count = sum(cart.values())
    return {"cart_item_count": count}


def back_nav(request):
    path = (request.path or "").strip("/")
    if not path:
        return {"back_url": None, "back_label": None}
    if path.startswith("products/") and path.count("/") >= 1:
        return {"back_url": reverse("product_list"), "back_label": "Party boxes"}
    if path == "cart":
        return {"back_url": reverse("product_list"), "back_label": "Party boxes"}
    if path == "checkout":
        return {"back_url": reverse("cart"), "back_label": "Cart"}
    if path.startswith("payment/"):
        return {"back_url": reverse("cart"), "back_label": "Cart"}
    if path in ("about", "gallery", "reviews", "contact"):
        return {"back_url": reverse("home"), "back_label": "Home"}
    if path == "products":
        return {"back_url": reverse("home"), "back_label": "Home"}
    return {"back_url": reverse("home"), "back_label": "Home"}

