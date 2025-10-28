# backend/settings.py
from pathlib import Path
import os
import sys
import re
from dotenv import load_dotenv
import dj_database_url

# --- Mitigar conflictos por agentes de Azure (OpenTelemetry) ---
sys.path = [p for p in sys.path if "/agents/python" not in p]
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")  # opcional en local

# Helper para leer listas desde variables de entorno (coma-separadas)
def csv_env(name, default=""):
    raw = os.getenv(name, default)
    return [x.strip() for x in raw.split(",") if x.strip()]

# =========================
# Core
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "!!!_dev_only_change_me_!!!")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# --- Railway: hosts permitidos ---
# Puedes sobreescribir con ALLOWED_HOSTS en variables de entorno.
DEFAULT_ALLOWED = [
    ".railway.app",             # cualquier subdominio de Railway
    "localhost", "127.0.0.1",
    # agrega tu dominio exacto si ya lo conoces:
    "quizgenai1-production.up.railway.app",
]
ALLOWED_HOSTS = csv_env("ALLOWED_HOSTS", ",".join(DEFAULT_ALLOWED))

# =========================
# CORS / CSRF para frontend en Vercel
# =========================
# Tu frontend actual:
FRONTEND_URL = "https://quiz-gen-ai-three.vercel.app"

DEFAULT_CORS = [
    FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOWED_ORIGINS = csv_env("CORS_ALLOWED_ORIGINS", ",".join(DEFAULT_CORS))

# Acepta cualquier subdominio *.vercel.app (previews)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
]

# Si no usas cookies/sesiones desde el browser, puedes dejar False.
# Si sí envías cookies (SessionAuth/CSRF), déjalo True.
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = ["*"]

# CSRF: confía en Railway + Vercel + localhost
DEFAULT_CSRF = [
    "https://*.railway.app",
    "https://quizgenai1-production.up.railway.app",
    "https://*.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CSRF_TRUSTED_ORIGINS = csv_env("CSRF_TRUSTED_ORIGINS", ",".join(DEFAULT_CSRF))

# =========================
# Apps / Middleware
# =========================
INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "api",
]

MIDDLEWARE = [
    # CORS debe ir lo más arriba posible
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"
ASGI_APPLICATION = "backend.asgi.application"

# =========================
# Base de datos
# =========================
# Railway suele inyectar DATABASE_URL (Postgres).
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}")

# Si es Postgres en Railway (sslmode=require), forzamos SSL.
ssl_require = DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=ssl_require,
    )
}

# =========================
# Password validators
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =========================
# i18n / zona horaria
# =========================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# =========================
# Archivos estáticos (Whitenoise)
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================
# Seguridad detrás de proxy (Railway)
# =========================
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    USE_X_FORWARDED_HOST = True
    # Activa HSTS cuando verifiques todo ok en HTTPS:
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True

# =========================
# DRF (opcional)
# =========================
# Si usas SessionAuthentication con cookies, necesitarás CSRF correcto.
# Si solo usas llamadas tipo token/Bearer, puedes quitar SessionAuthentication.
# REST_FRAMEWORK = {
#     "DEFAULT_AUTHENTICATION_CLASSES": [
#         "rest_framework.authentication.BasicAuthentication",
#         "rest_framework.authentication.SessionAuthentication",
#     ]
# }
