import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-badju-records-cle-secrete-a-changer-en-prod'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

AUTH_USER_MODEL = 'models_app.User'

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps du projet
    'models_app',
    'users',
    'artistes',
    'morceaux',
    'engagement',
    'classement',
    'publicites',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'badjus_records.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'badjus_records.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'badjus_records',
        'USER': 'postgres',
        'PASSWORD': 'eloge16king2',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

AUTH_USER_MODEL = 'models_app.User'

LOGIN_URL = '/connexion/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Lome'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─────────────────────────────────────────────
# DJANGO-UNFOLD CONFIGURATION
# ─────────────────────────────────────────────
from django.templatetags.static import static
from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE":    "Badju's Records",
    "SITE_HEADER":   "Badju's Records",
    "SITE_SUBHEADER": "Panneau d'administration",
    "SITE_URL":      "/",

    # Logo
    "SITE_LOGO": lambda request: static("img/logo-transparent.png"),
    "SITE_ICON": lambda request: static("img/logo-transparent.png"),

    # Symbole favori
    "SITE_SYMBOL": "music_note",

    # Couleurs dark mode + or
    "COLORS": {
        "primary": {
            "50":  "255 251 235",
            "100": "254 243 199",
            "200": "253 230 138",
            "300": "252 211 77",
            "400": "251 191 36",
            "500": "245 166 35",   # ← accent-gold principal
            "600": "217 119 6",
            "700": "180 83 9",
            "800": "146 64 14",
            "900": "120 53 15",
            "950": "69 26 3",
        },
        "font": {
            "subtle-light":       "107 114 128",
            "subtle-dark":        "156 163 175",
            "default-light":      "75 85 99",
            "default-dark":       "209 213 219",
            "important-light":    "17 24 39",
            "important-dark":     "243 244 246",
        },
    },

    # Thème sombre par défaut
    "THEME": "dark",

    # CSS personnalisé
    "STYLES": [
        lambda request: static("css/admin_custom.css"),
    ],

    # Navigation sidebar
    "SIDEBAR": {
        "show_search":      True,
        "show_all_applications": False,
        "navigation": [
            {
                "title":     "Tableau de bord",
                "separator": False,
                "items": [
                    {
                        "title": "Accueil admin",
                        "icon":  "home",
                        "link":  reverse_lazy("admin:index"),
                    },
                    {
                        "title": "Voir le site",
                        "icon":  "open_in_new",
                        "link":  "/",
                    },
                ],
            },
            {
                "title":     "Musique",
                "separator": True,
                "items": [
                    {
                        "title": "Morceaux",
                        "icon":  "music_note",
                        "link":  reverse_lazy("admin:models_app_morceau_changelist"),
                        "badge": "models_app.badge_callbacks.morceaux_en_attente",
                    },
                    {
                        "title": "Vidéos",
                        "icon":  "videocam",
                        "link":  reverse_lazy("admin:models_app_video_changelist"),
                        "badge": "models_app.badge_callbacks.videos_en_attente",
                    },
                ],
            },
            {
                "title":     "Artistes & Utilisateurs",
                "separator": True,
                "items": [
                    {
                        "title": "Artistes",
                        "icon":  "mic",
                        "link":  reverse_lazy("admin:models_app_profilartiste_changelist"),
                    },
                    {
                        "title": "Utilisateurs",
                        "icon":  "group",
                        "link":  reverse_lazy("admin:models_app_user_changelist"),
                    },
                ],
            },
            {
                "title":     "Engagement",
                "separator": True,
                "items": [
                    {
                        "title": "Votes",
                        "icon":  "thumb_up",
                        "link":  reverse_lazy("admin:models_app_vote_changelist"),
                    },
                    {
                        "title": "Téléchargements",
                        "icon":  "download",
                        "link":  reverse_lazy("admin:models_app_telechargement_changelist"),
                    },
                    {
                        "title": "Abonnements",
                        "icon":  "notifications",
                        "link":  reverse_lazy("admin:models_app_abonnement_changelist"),
                    },
                ],
            },
            {
                "title":     "Monétisation",
                "separator": True,
                "items": [
                    {
                        "title": "Publicités",
                        "icon":  "campaign",
                        "link":  reverse_lazy("admin:models_app_publicite_changelist"),
                    },
                ],
            },
        ],
    },
}