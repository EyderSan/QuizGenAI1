from pathlib import Path
import os
import sys
from dotenv import load_dotenv
import dj_database_url

# --- Mitigar conflictos por agentes de Azure (OpenTelemetry) ---
sys.path = [p for p in sys.path if "/agents/python" not in p]
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")  # opcional en local

# -------------------------
# Helpers
# -------------------------
def csv_env(name, default=""):
    raw = os.getenv(name, default)
    return [x.strip() for x in raw.split(",") if x.strip()]

# -------------------------
# Core
# -------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "!!!_dev_only_change_me_!!!")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Evita redirecciones 301 (slash/no-slash) que rompen el preflight OPTIONS
APPEND_SLASH = False

DEFAULT_ALLOWED = [
    ".railway.app",
    "localhost",
    "127.0.0.1",
    "quizgenai1-production.up.railway.app",  # ajusta al tuyo si cambia
]
ALLOWED_HOSTS = csv_env("ALLOWED_HOSTS", ",".join(DEFAULT_ALLOWED))

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -------------------------
# CORS / CSRF
# -------------------------
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://quiz-gen-ai-three.vercel.app")

DEFAULT_CORS = [
    FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOWED_ORIGINS = csv_env("CORS_ALLOWED_ORIGINS", ",".join(DEFAULT_CORS))

# Permite previews *.vercel.app
CORS_ALLOWED_ORIGIN_REGEXES = [r"^https://.*\.vercel\.app$"]

# Abierto por defecto para estabilizar (ciérralo luego en variables)
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "True").lower() == "true"
# Compatibilidad con versiones antiguas del paquete
CORS_ORIGIN_ALLOW_ALL = CORS_ALLOW_ALL_ORIGINS
CORS_ORIGIN_WHITELIST = CORS_ALLOWED_ORIGINS

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
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
CORS_PREFLIGHT_MAX_AGE = 86400
# Aplícalo a todo el sitio
CORS_URLS_REGEX = r"^/.*$"

DEFAULT_CSRF = [
    "https://*.railway.app",
    "https://quizgenai1-production.up.railway.app",
    "https://*.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CSRF_TRUSTED_ORIGINS = csv_env("CSRF_TRUSTED_ORIGINS", ",".join(DEFAULT_CSRF))

# -------------------------
# Apps / Middleware
# -------------------------
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
    "backend.fallback_cors.FallbackCORSMiddleware",  # <- airbag CORS/OPTIONS (temporal)
    "corsheaders.middleware.CorsMiddleware",         # <- CORS oficial
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

# -------------------------
# Base de datos
# -------------------------
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
ssl_require = DATABASE_URL.startswith(("postgres://", "postgresql://"))
DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=ssl_require,
    )
}

# -------------------------
# Password validators
# -------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------
# i18n / tz
# -------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------
# Estáticos (WhiteNoise)
# -------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# crea la carpeta para evitar el warning en contenedores efímeros
os.makedirs(STATIC_ROOT, exist_ok=True)

STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------
# Seguridad (prod)
# -------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    # Activa HSTS cuando todo esté ok:
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True
