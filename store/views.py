import uuid
from decimal import Decimal
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages 
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from .models import Category, Product, Order, OrderItem, GalleryItem, Review, ContactMessage
from .forms import CheckoutForm, ContactForm, ReviewForm
from .utils import (
    add_to_cart_session,
    update_cart_item,
    remove_cart_item,
    clear_cart,
    get_cart,
    get_cart_items,
    get_site_setting,
    save_cart,
)
from . import paynow, whatsapp


def _send_admin_order_paid_email(order):
    lines = [
        f"Order reference: {order.reference}",
        f"Name: {order.full_name}",
        f"Phone: {order.phone}",
        f"Email: {order.email or '(not provided)'}",
        f"Theme: {order.theme or '-'}",
        f"Child name: {order.child_name or '-'}",
        f"Age: {order.age or '-'}",
        f"Collection date: {order.collection_date or '-'}",
        f"Toy preference: {order.toy_preference or '-'}",
        f"Delivery: {order.delivery_method or '-'}",
        f"Address: {order.delivery_address or '-'}",
        "",
        "Items:",
    ]
    for oi in order.items.all():
        lines.append(f"  • {oi.product.name} x {oi.qty} @ $ {oi.unit_price} = $ {oi.line_total}")
    lines.extend(["", f"Subtotal: $ {order.subtotal}", f"Delivery: $ {order.delivery_fee}", f"Total: $ {order.total}", "", "[PAID]"])
    body = "\n".join(lines)
    send_mail(
        f"Order paid #{order.reference} – Party Fantasy ZW",
        body,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
        fail_silently=True,
    )

def _send_admin_order_paid_whatsapp(order):
    if order.status != Order.STATUS_PAID:
        return
    if getattr(order, "whatsapp_sent", False):
        return
    if not whatsapp.is_configured():
        return

    lines = [
        "NEW PAID ORDER ✅",
        f"Ref: {order.reference}",
        f"Name: {order.full_name or '-'}",
        f"Phone: {order.phone or '-'}",
        f"Email: {order.email or '(not provided)'}",
        f"Theme: {order.theme or '-'}",
        f"Child: {order.child_name or '-'}",
        f"Age: {order.age or '-'}",
        f"Collection date: {order.collection_date or '-'}",
        f"Toy preference: {order.toy_preference or '-'}",
        f"Delivery: {order.delivery_method or '-'}",
        f"Address: {order.delivery_address or '-'}",
        "",
        "Items:",
    ]

    for oi in order.items.all():
        lines.append(f"- {oi.product.name} x{oi.qty} = $ {oi.line_total}")

    lines.extend([
        "",
        f"Subtotal: $ {order.subtotal}",
        f"Delivery: $ {order.delivery_fee}",
        f"Total: $ {order.total}",
    ])

    msg = "\n".join(lines)

    try:
        whatsapp.send_text(settings.WA_ADMIN_TO, msg)
        order.whatsapp_sent = True
        order.save(update_fields=["whatsapp_sent"])
    except Exception:
        pass

def _send_customer_order_paid_email(order):
    if not order.email or not order.email.strip():
        return
    lines = [
        f"Order reference: {order.reference}",
        "",
        "Order summary:",
        f"  Subtotal:    $ {order.subtotal}",
        f"  Delivery:    $ {order.delivery_fee}",
        f"  Total:       $ {order.total}",
        "",
        "Items:",
    ]
    for oi in order.items.all():
        lines.append(f"  • {oi.product.name} x {oi.qty} @ $ {oi.unit_price} = $ {oi.line_total}")
    summary = "\n".join(lines)
    name = (order.full_name or "there").strip() or "there"
    body = (
        f"Dear {name},\n\n"
        "Thank you for your order. We have received your payment and your order is confirmed.\n\n"
        f"{summary}\n\n"
        "We will be in touch regarding delivery or collection. "
        "If you have any questions, please reply to this email or contact us—we are happy to help.\n\n"
        "Best regards,\n"
        "The Party Fantasy ZW Team"
    )
    send_mail(
        f"Order confirmed – #{order.reference} – Party Fantasy ZW",
        body,
        settings.DEFAULT_FROM_EMAIL,
        [order.email.strip()],
        fail_silently=True,
    )


def _send_customer_payment_failed_email(order):
    if not order.email or not order.email.strip():
        return
    name = (order.full_name or "there").strip() or "there"
    body = (
        f"Dear {name},\n\n"
        "We are sorry, but the payment for your order could not be completed. "
        "Your payment may have been cancelled or declined. No charges have been made to your account.\n\n"
        f"Order reference: {order.reference}\n\n"
        "If you would like to complete your purchase, you can try again from the payment page or place a new order on our website. "
        "If you need any assistance, please reply to this email or contact us—we are here to help.\n\n"
        "Best regards,\n"
        "The Party Fantasy ZW Team"
    )
    send_mail(
        f"Payment not completed – Order #{order.reference} – Party Fantasy ZW",
        body,
        settings.DEFAULT_FROM_EMAIL,
        [order.email.strip()],
        fail_silently=True,
    )


def gallery(request):
    items = list(GalleryItem.objects.all())
    return render(request, "gallery.html", {"items": items})


REVIEWS_PAGE_SIZE = 10


def reviews(request):
    queryset = Review.objects.filter(is_visible=True).order_by("-created_at")
    total_count = queryset.count()
    show_all = request.GET.get("show") == "all"
    if show_all:
        reviews_list = list(queryset)
    else:
        reviews_list = list(queryset[:REVIEWS_PAGE_SIZE])
    sent = request.GET.get("sent") == "1"
    form = ReviewForm()
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            Review.objects.create(
                name=data["name"].strip(),
                email=(data.get("email") or "").strip(),
                rating=data.get("rating") or None,
                text=data["text"].strip(),
                is_visible=True,
            )
            return redirect(reverse("reviews") + "?sent=1")
    context = {
        "reviews_list": reviews_list,
        "form": form,
        "sent": sent,
        "total_count": total_count,
        "show_all": show_all,
    }
    return render(request, "reviews.html", context)


def home(request):
    products = list(Product.objects.filter(is_active=True).order_by("-created_at")[:6])
    min_price = min((p.price for p in products), default=None)
    featured_reviews = list(Review.objects.filter(is_visible=True).order_by("-created_at")[:3])
    return render(request, "home.html", {"featured_products": products, "min_price": min_price, "featured_reviews": featured_reviews})


def product_list(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    categories = Category.objects.all().order_by("name")
    products = Product.objects.filter(is_active=True)
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)
    if category_slug:
        products = products.filter(category__slug=category_slug)
    products_list = list(products.distinct().order_by("name"))
    if category_slug:
        get_object_or_404(Category, slug=category_slug)
    context = {
        "products_list": products_list,
        "categories": categories,
        "current_query": query,
        "current_category": category_slug,
    }
    return render(request, "products.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    if request.method == "POST":
        qty_raw = request.POST.get("qty", "10")
        try:
            qty = int(qty_raw)
        except ValueError:
            qty = 10
        if qty < 10:
            qty = 10
        add_to_cart_session(request, product.id, qty)
        return redirect("cart")
    return render(request, "product_detail.html", {"product": product})

def add_to_cart(request, product_id):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    product = get_object_or_404(Product, id=product_id, is_active=True)

    qty_raw = request.POST.get("qty", "10")
    try:
        qty = int(qty_raw)
    except ValueError:
        qty = 10

    if qty < 10:
        qty = 10

    add_to_cart_session(request, product.id, qty)
    return redirect("cart")


def cart_view(request):
    if request.method == "POST":
        action = request.POST.get("action")
        product_id = request.POST.get("product_id")
        if product_id:
            try:
                pid = int(product_id)
            except ValueError:
                pid = None

            if pid:
                if action == "update":
                    qty_raw = request.POST.get("qty", "10")
                    try:
                        qty = int(qty_raw)
                    except ValueError:
                        qty = 10

                    if qty == 0:
                        update_cart_item(request, pid, 0)
                    elif 1 <= qty < 10:
                        messages.warning(request, "Minimum order quantity is 10 per item.")
                    else:
                        update_cart_item(request, pid, qty)

                elif action == "remove":
                    remove_cart_item(request, pid)

        return redirect("cart")

    items, subtotal = get_cart_items(request)
    setting = get_site_setting()
    delivery_fee = setting.delivery_fee
    delivery_total = subtotal + delivery_fee
    context = {
        "items": items,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "delivery_total": delivery_total,
    }
    return render(request, "cart.html", context)

def checkout(request):
    items, subtotal = get_cart_items(request)
    if not items:
        return redirect("cart")

    setting = get_site_setting()
    delivery_fee_value = setting.delivery_fee
    pickup_total = subtotal
    delivery_total = subtotal + delivery_fee_value

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            delivery_method = data.get("delivery_method")
            if delivery_method == "delivery":
                delivery_fee = delivery_fee_value
            else:
                delivery_fee = Decimal("0.00")

            total = subtotal + delivery_fee
            reference = uuid.uuid4().hex.upper()

            order = Order.objects.create(
                reference=reference,
                full_name=data.get("full_name") or "",
                phone=data.get("phone") or "",
                email=data.get("email") or "",
                theme=data.get("theme") or "",
                child_name=data.get("child_name") or "",
                age=data.get("age"),
                collection_date=data.get("collection_date"),
                toy_preference=data.get("toy_preference") or "",
                delivery_method=delivery_method or "",
                delivery_address=data.get("delivery_address") or "",
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                total=total,
            )

            for item in items:
                product = item["product"]
                qty = item["qty"]
                unit_price = product.price
                line_total = unit_price * qty
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    qty=qty,
                    unit_price=unit_price,
                    line_total=line_total,
                )

            save_cart(request, get_cart(request))

            # -----------------------------
            # BYPASS PAYNOW FOR NOW:
            # Send order to WhatsApp sales team
            # -----------------------------
            if whatsapp.is_configured():
                lines = [
                    "NEW ORDER (Payment Later) 🟡",
                    f"Ref: {order.reference}",
                    f"Name: {order.full_name or '-'}",
                    f"Phone: {order.phone or '-'}",
                    f"Email: {order.email or '(not provided)'}",
                    f"Theme: {order.theme or '-'}",
                    f"Child: {order.child_name or '-'}",
                    f"Age: {order.age or '-'}",
                    f"Collection date: {order.collection_date or '-'}",
                    f"Toy preference: {order.toy_preference or '-'}",
                    f"Delivery: {order.delivery_method or '-'}",
                    f"Address: {order.delivery_address or '-'}",
                    "",
                    "Items:",
                ]

                for oi in order.items.all():
                    lines.append(f"- {oi.product.name} x{oi.qty} = $ {oi.line_total}")

                lines.extend([
                    "",
                    f"Subtotal: $ {order.subtotal}",
                    f"Delivery: $ {order.delivery_fee}",
                    f"Total: $ {order.total}",
                    "",
                    "Customer message: Please confirm order on WhatsApp. Payment will be arranged after confirmation.",
                ])

                msg = "\n".join(lines)

                try:
                    whatsapp.send_text(settings.WA_ADMIN_TO, msg)
                except Exception:
                    pass

            # previously we used messages to inform the user, but that caused
            # the same notices to appear on cart/other pages later.  Instead we
            # render the information directly on the order_received template.

            # Clear cart so they don't accidentally resubmit
            clear_cart(request)

            # Redirect to new order-received page instead of payment flow
            return redirect("order_received", reference=order.reference)

    else:
        form = CheckoutForm()

    context = {
        "form": form,
        "items": items,
        "subtotal": subtotal,
        "delivery_fee_value": delivery_fee_value,
        "pickup_total": pickup_total,
        "delivery_total": delivery_total,
        "paynow_configured": paynow.is_configured(),
    }
    return render(request, "checkout.html", context)



def order_received(request, reference):
    order = get_object_or_404(Order, reference=reference)
    return render(request, "order_received.html", {"order": order})


def payment_return(request):
    reference = (
        request.GET.get("reference") or request.GET.get("Reference") or request.GET.get("ref")
    )
    if reference:
        reference = str(reference).strip()
    if not reference:
        reference = request.session.pop("paynow_return_reference", None)
    if reference:
        return redirect("payment_status", reference=reference)
    return redirect("home")


def payment_status(request, reference):
    order = get_object_or_404(Order, reference=reference)
    was_paid = order.status == Order.STATUS_PAID
    was_failed = order.status == Order.STATUS_FAILED
    if request.method == "POST":
        paynow.check_payment_status(order)
        order.refresh_from_db()
        if not was_paid and order.status == Order.STATUS_PAID:
            _send_admin_order_paid_email(order)
            _send_customer_order_paid_email(order)
            _send_admin_order_paid_whatsapp(order)
        if not was_failed and order.status == Order.STATUS_FAILED:
            _send_customer_payment_failed_email(order)
        return redirect("payment_status", reference=order.reference)
    paynow.check_payment_status(order)
    order.refresh_from_db()
    if not was_paid and order.status == Order.STATUS_PAID:
        _send_admin_order_paid_email(order)
        _send_customer_order_paid_email(order)
        _send_admin_order_paid_whatsapp(order)
    if not was_failed and order.status == Order.STATUS_FAILED:
        _send_customer_payment_failed_email(order)
    context = {
        "order": order,
        "paynow_configured": paynow.is_configured(),
        "ecocash_error": request.session.pop("ecocash_error", None),
    }
    if order.status == Order.STATUS_PAID:
        clear_cart(request)
        return render(request, "payment_success.html", context)
    if order.status == Order.STATUS_FAILED:
        return render(request, "payment_cancelled.html", context)
    return render(request, "payment_other.html", context)


def about(request):
    return render(request, "about.html")


def contact(request):
    sent = False
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            ContactMessage.objects.create(
                name=data.get("name") or "",
                email=data.get("email") or "",
                phone=data.get("phone") or "",
                message=data.get("message") or "",
            )
            subject = "Party Fantasy ZW Enquiry"
            lines = []
            if data.get("name"):
                lines.append(f"Name: {data['name']}")
            if data.get("email"):
                lines.append(f"Email: {data['email']}")
            if data.get("phone"):
                lines.append(f"Phone: {data['phone']}")
            lines.append("")
            lines.append(data["message"])
            body = "\n".join(lines)
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=True,
            )
            sent = True
    else:
        form = ContactForm()
    return render(request, "contact.html", {"form": form, "sent": sent})


def paynow_result(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Method not allowed")
    reference = request.POST.get("reference")
    if not reference:
        return HttpResponseBadRequest("Missing reference")
    if not paynow.is_configured():
        return HttpResponse("OK", status=200)
    if not paynow.validate_result_post(request.POST, settings.PAYNOW_INTEGRATION_KEY):
        return HttpResponseBadRequest("Invalid hash")
    order = Order.objects.filter(reference=reference).first()
    if not order:
        return HttpResponse("OK", status=200)
    was_paid = order.status == Order.STATUS_PAID
    was_failed = order.status == Order.STATUS_FAILED
    paynow.check_payment_status(order)
    order.refresh_from_db()
    if not was_paid and order.status == Order.STATUS_PAID:
        _send_admin_order_paid_email(order)
        _send_customer_order_paid_email(order)
        _send_admin_order_paid_whatsapp(order)
    if not was_failed and order.status == Order.STATUS_FAILED:
        _send_customer_payment_failed_email(order)
    return HttpResponse("OK", status=200)


def ecocash_start(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Method not allowed")
    reference = (request.POST.get("reference") or "").strip()
    phone = (request.POST.get("phone") or "").strip()
    if not reference or not phone:
        return redirect("payment_status", reference=reference or "unknown")
    order = Order.objects.filter(reference=reference).first()
    if not order:
        return redirect("home")
    ok, _poll_url, _ref, err_msg = paynow.initiate_ecocash(order, phone)
    if not ok:
        request.session["ecocash_error"] = err_msg or "Could not start EcoCash payment. Check the phone number and try again."
    return redirect("payment_status", reference=order.reference)


def paynow_status_json(request, order_reference):
    order = get_object_or_404(Order, reference=order_reference)
    was_paid = order.status == Order.STATUS_PAID
    was_failed = order.status == Order.STATUS_FAILED
    paynow.check_payment_status(order)
    order.refresh_from_db()
    if not was_paid and order.status == Order.STATUS_PAID:
        _send_admin_order_paid_email(order)
        _send_customer_order_paid_email(order)
        _send_admin_order_paid_whatsapp(order)
    if not was_failed and order.status == Order.STATUS_FAILED:
        _send_customer_payment_failed_email(order)
    paid = order.status == Order.STATUS_PAID
    status = order.status
    message = "Paid" if paid else ("Failed or cancelled" if order.status == Order.STATUS_FAILED else "Pending")
    return JsonResponse({"status": status, "paid": paid, "message": message})

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap_xml'))}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def sitemap_xml(request):
    base = request.build_absolute_uri("/")[:-1]

    urls = [
        {"loc": f"{base}{reverse('home')}", "changefreq": "weekly", "priority": "1.0"},
        {"loc": f"{base}{reverse('product_list')}", "changefreq": "weekly", "priority": "0.9"},
        {"loc": f"{base}{reverse('gallery')}", "changefreq": "monthly", "priority": "0.6"},
        {"loc": f"{base}{reverse('reviews')}", "changefreq": "monthly", "priority": "0.6"},
        {"loc": f"{base}{reverse('about')}", "changefreq": "yearly", "priority": "0.5"},
        {"loc": f"{base}{reverse('contact')}", "changefreq": "yearly", "priority": "0.5"},
    ]

    for p in Product.objects.filter(is_active=True).only("slug").order_by("-created_at"):
        urls.append(
            {
                "loc": f"{base}{reverse('product_detail', kwargs={'slug': p.slug})}",
                "changefreq": "weekly",
                "priority": "0.8",
            }
        )

    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        xml.append("  <url>")
        xml.append(f"    <loc>{u['loc']}</loc>")
        xml.append(f"    <changefreq>{u['changefreq']}</changefreq>")
        xml.append(f"    <priority>{u['priority']}</priority>")
        xml.append("  </url>")
    xml.append("</urlset>")
    return HttpResponse("\n".join(xml) + "\n", content_type="application/xml")