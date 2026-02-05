import logging
from django.conf import settings
from paynow import Paynow
from .models import Order

logger = logging.getLogger(__name__)


def is_configured():
    return bool(settings.PAYNOW_INTEGRATION_ID and settings.PAYNOW_INTEGRATION_KEY and settings.PAYNOW_RETURN_URL and settings.PAYNOW_RESULT_URL)


def validate_result_post(post_data, integration_key):
    return True


def initiate_payment(order):
    if not is_configured():
        logger.warning("Paynow not configured: missing env vars")
        return None, None
    total = float(order.total)
    if total <= 0:
        logger.warning("Paynow amount must be greater than 0")
        return None, None
    paynow = Paynow(
        settings.PAYNOW_INTEGRATION_ID,
        settings.PAYNOW_INTEGRATION_KEY,
        settings.PAYNOW_RETURN_URL,
        settings.PAYNOW_RESULT_URL,
    )
    if Paynow.__module__ != "paynow.advanced" and "advanced" not in str(type(paynow).__name__).lower():
        print("[Paynow] Using class: {} from {}".format(type(paynow).__name__, type(paynow).__module__))
    payment = paynow.create_payment(order.reference, order.email or "")
    payment.add("Order", total)
    try:
        response = paynow.send(payment)
    except Exception as e:
        logger.warning("Paynow send failed: %s", e)
        return None, None
    print("[Paynow] response repr: {}".format(repr(response)))
    print("[Paynow] response.status: {}".format(getattr(response, "status", None)))
    print("[Paynow] response.success: {}".format(getattr(response, "success", None)))
    print("[Paynow] response.redirect_url: {}".format(getattr(response, "redirect_url", None)))
    print("[Paynow] response.poll_url: {}".format(getattr(response, "poll_url", None)))
    if not response.success:
        logger.warning("Paynow response not success")
        return None, None
    redirect_url = (getattr(response, "redirect_url", None) or "").strip()
    if not redirect_url:
        logger.warning("Paynow response missing redirect_url")
    if redirect_url and (not isinstance(redirect_url, str) or not redirect_url.lower().startswith("http")):
        print("[Paynow] redirect_url rejected (not non-empty string starting with http): {}".format(redirect_url[:80] if redirect_url else ""))
        redirect_url = ""
    if redirect_url:
        print("[Paynow] redirect_url is Paynow payment URL: {}".format("/User/Login" not in redirect_url))
        print("[Paynow] redirect_url is /User/Login: {}".format("/User/Login" in redirect_url))
    order.paynow_redirect_url = redirect_url
    order.paynow_poll_url = getattr(response, "poll_url", None) or ""
    order.status = Order.STATUS_PENDING
    order.save()
    return (redirect_url, response.poll_url) if redirect_url else (None, getattr(response, "poll_url", None))


def initiate_ecocash(order, phone):
    if not is_configured():
        logger.warning("Paynow not configured: missing env vars")
        return False, None, "", "Paynow is not configured."
    total = float(order.total)
    if total <= 0:
        logger.warning("Paynow amount must be greater than 0")
        return False, None, "", "Order total must be greater than 0."
    paynow = Paynow(
        settings.PAYNOW_INTEGRATION_ID,
        settings.PAYNOW_INTEGRATION_KEY,
        settings.PAYNOW_RETURN_URL or "https://partyfantasy.co.zw/payment/return/",
        settings.PAYNOW_RESULT_URL or "https://partyfantasy.co.zw/paynow/result/",
    )
    email = (order.email or "").strip() or "guest+{}@kart.local".format(order.reference)
    payment = paynow.create_payment(order.reference, email)
    payment.add("Order", total)
    try:
        response = paynow.send_mobile(payment, phone.strip(), "ecocash")
    except Exception as e:
        logger.warning("Paynow send_mobile failed: %s", e)
        return False, None, "", str(e)
    if not getattr(response, "success", False):
        err_msg = ""
        if getattr(response, "data", None) and isinstance(response.data, dict):
            err_msg = (
                response.data.get("error")
                or response.data.get("status")
                or ""
            )
        if not err_msg and hasattr(response, "error") and isinstance(response.error, str):
            err_msg = response.error
        logger.warning("Paynow mobile response not success: %s", err_msg or "unknown")
        return False, None, "", (err_msg or "Payment could not be started.")
    poll_url = getattr(response, "poll_url", None) or ""
    paynow_ref = ""
    if hasattr(response, "data") and response.data:
        paynow_ref = response.data.get("paynowreference", "") or ""
    order.paynow_poll_url = poll_url
    order.paynow_reference = paynow_ref
    order.status = Order.STATUS_PENDING
    order.save()
    return True, poll_url, paynow_ref, ""


def check_payment_status(order):
    if order.status == Order.STATUS_PAID:
        return order.status
    if not is_configured() or not order.paynow_poll_url:
        return order.status
    paynow = Paynow(
        settings.PAYNOW_INTEGRATION_ID,
        settings.PAYNOW_INTEGRATION_KEY,
        settings.PAYNOW_RETURN_URL,
        settings.PAYNOW_RESULT_URL,
    )
    try:
        status = paynow.check_transaction_status(order.paynow_poll_url)
    except Exception:
        return order.status
    if status.paid:
        order.status = Order.STATUS_PAID
    elif getattr(status, "status", "").lower() in ("cancelled", "failed"):
        order.status = Order.STATUS_FAILED
    order.save()
    return order.status
