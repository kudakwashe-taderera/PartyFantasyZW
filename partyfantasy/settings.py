import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

if os.path.isfile(BASE_DIR / ".env"):
    with open(BASE_DIR / ".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1].replace('\\"', '"')
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1].replace("\\'", "'")
                os.environ.setdefault(key, value)

SECRET_KEY = os.environ.get("SECRET_KEY", "replace-this-with-a-secure-key")
DEBUG = os.environ.get("DEBUG", "true").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "codexware.pythonanywhere.com",
]
if os.environ.get("ALLOWED_HOSTS_EXTRA"):
    ALLOWED_HOSTS += [h.strip() for h in os.environ["ALLOWED_HOSTS_EXTRA"].split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://codexware.pythonanywhere.com",
]
if os.environ.get("CSRF_TRUSTED_ORIGINS_EXTRA"):
    CSRF_TRUSTED_ORIGINS += [o.strip() for o in os.environ["CSRF_TRUSTED_ORIGINS_EXTRA"].split(",") if o.strip()]

INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "store",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "partyfantasy.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "store.context_processors.cart",
                "store.context_processors.back_nav",
            ],
        },
    },
]

WSGI_APPLICATION = "partyfantasy.wsgi.application"
ASGI_APPLICATION = "partyfantasy.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Harare"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if os.environ.get("EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("EMAIL_HOST")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() in ("true", "1", "yes")
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Party Fantasy ZW <noreply@partyfantasyzw.local>")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "tadererak@gmail.com")

PAYNOW_INTEGRATION_ID = os.environ.get("PAYNOW_INTEGRATION_ID", "")
PAYNOW_INTEGRATION_KEY = os.environ.get("PAYNOW_INTEGRATION_KEY", "")
PAYNOW_RETURN_URL = os.environ.get("PAYNOW_RETURN_URL", "")
PAYNOW_RESULT_URL = os.environ.get("PAYNOW_RESULT_URL", "")

UNFOLD = {
    "SITE_TITLE": "Party Fantasy ZW Admin",
    "SITE_HEADER": "Party Fantasy ZW Admin",
    "THEME": "dark",
    "COLORS": {
        "primary": {
            "50": "oklch(97.5% 0.02 350)",
            "100": "oklch(94% 0.05 350)",
            "200": "oklch(88% 0.10 350)",
            "300": "oklch(80% 0.15 350)",
            "400": "oklch(70% 0.19 350)",
            "500": "oklch(62% 0.22 350)",
            "600": "oklch(55% 0.22 350)",
            "700": "oklch(48% 0.20 350)",
            "800": "oklch(42% 0.17 350)",
            "900": "oklch(35% 0.14 350)",
            "950": "oklch(28% 0.12 350)",
        },
    },
}

