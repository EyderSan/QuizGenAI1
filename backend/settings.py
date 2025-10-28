# backend/settings.py
from pathlib import Path
import os
import sys
from dotenv import load_dotenv
import dj_database_url
import re

# --- Mitigar conflictos por agentes de Azure (OpenTelemetry) ---
sys.path = [p for p in sys.path if "/agents/python" not in p]
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")  # opcional en local


# =========================
# Helpers
# =========================
def csv_env(name, default=""):
    raw = os.getenv(name, default)
    return [x.strip() for x in raw.split(",") if x.strip()]


# =========================
# Core
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "!!!_dev_only_change_me_!!!")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Railway: por defecto aceptamos *.railway.app + localhost
DEFAULT_ALLOWED = [
    ".railway.app",
    "localhost",
    "127.0.0.1",
    # agrega aquí tu dominio exacto si ya lo conoces
    "quizgenai1-production.up.railway.app",
]
ALLOWED_HOSTS = csv_env("ALLOWED_HOSTS", ",".join(DEFAULT_ALLOWED))

# Útil si Railway está detrás de proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# =========================
# CORS / CSRF
# =========================
# Frontend principal (ajústalo si cambias Vercel)
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://quiz-gen-ai-three.vercel.app")

DEFAULT_CORS = [
    FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOWED_ORIGINS = csv_env("CORS_ALLOWED_ORIGINS", ",".join(DEFAULT_CORS))

# Permite cualquier preview de Vercel (*.vercel.app)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
]

# Si necesitas abrir todo temporalmente para test:
# export CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "False").lower() == "true"

# Si usas cookies/sesiones desde el browser (CSRF), deja True.
# Si solo usas tokens/Bearer, podría ser False, pero dejar True no rompe.
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
# Limitar headers a lo típico del preflight
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
# Max-Age del preflight (puedes bajarlo si lo prefieres)
CORS_PREFLIGHT_MAX_AGE = 86400

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
    "corsheaders",  # <-- debe estar instalado
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
    "corsheaders.middleware.CorsMiddleware",  # <-- lo más arriba posible
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
# Railway inyecta DATABASE_URL si usas Postgres
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
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
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Nota: el warning "No directory at: /app/staticfiles/" se resuelve ejecutando
# collectstatic en build/predeploy o creando el directorio vacío:
#   python manage.py collectstatic --noinput
#   (o) mkdir -p staticfiles


# =========================
# Seguridad en producción
# =========================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    # Activa HSTS cuando verifiques todo ok en HTTPS:
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True


# =========================
# DRF (opcional)
# =========================
# REST_FRAMEWORK = {
#     "DEFAULT_AUTHENTICATION_CLASSES": [
#         "rest_framework.authentication.SessionAuthentication",
#         "rest_framework.authentication.BasicAuthentication",
#     ],
# }
