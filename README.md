# Party Fantasy ZW

Minimal Django storefront for Zimbabwe-only party boxes, using USD pricing and Paynow.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the storefront and `http://127.0.0.1:8000/admin/` for the admin.

## Environment variables (Paynow)

Create a `.env` file in the project root (same folder as `manage.py`) with:

```
PAYNOW_INTEGRATION_ID=your_actual_id
PAYNOW_INTEGRATION_KEY=your_actual_key
PAYNOW_RETURN_URL=http://127.0.0.1:8000/payment/return/
PAYNOW_RESULT_URL=http://127.0.0.1:8000/paynow/result/
```

Django loads `.env` automatically when the file exists. For local dev use `http://127.0.0.1:8000`; for production use your real domain. Paynow will send customers back to the return URL with `?reference=...`; the app redirects that to the payment status page. If these vars are missing, the site still works but Paynow redirect will not be used.

## Admin: products, categories, delivery fee

1. Log in to `/admin/` with your superuser account.
2. Create `Category` entries (name and slug).
3. Create `Product` entries, assign them to categories, set `price` in USD, upload an image if available, and mark `is_active` to show them on the site.
4. In `Site settings`, create a single row and set `delivery_fee` (flat fee in USD).

Product images are stored in `media/products/`. Static assets (including the placeholder image) live under `static/`.

Add an image file at `static/img/placeholder.jpg` to be used whenever a product image is missing.

## Initial products fixture

Load categories and products from the fixture: `python manage.py loaddata initial_products`. If you already have data and need to reload, flush store data then load again: `python manage.py shell -c "from store.models import Product, Order, OrderItem; OrderItem.objects.all().delete(); Order.objects.all().delete(); Product.objects.all().delete(); from store.models import Category; Category.objects.all().delete()"` then `python manage.py loaddata initial_products`.

