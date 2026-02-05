from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("payment/return/", views.payment_return, name="payment_return"),
    path("payment/<str:reference>/", views.payment_status, name="payment_status"),
    path("about/", views.about, name="about"),
    path("gallery/", views.gallery, name="gallery"),
    path("reviews/", views.reviews, name="reviews"),
    path("contact/", views.contact, name="contact"),
    path("paynow/result/", views.paynow_result, name="paynow_result"),
    path("payments/paynow/ecocash/start/", views.ecocash_start, name="ecocash_start"),
    path("payments/paynow/status/<str:order_reference>/", views.paynow_status_json, name="paynow_status_json"),
]

