"""
Django settings for zibanoo project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os

from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1j7*c*27gn+t$tpohmvdlpje&lgo=^v1&j#b8wd+4t6#)0#9f5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['hameddjf.pythonanywhere.com', 'example.com' , '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',


    'accounts',
    'products',
    'comments',
    'carts',
    'orders',
    'blogs',
    'rating',
    'dashboard',


    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'mptt',
    "azbankgateways",
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'products.middleware.SimpleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'zibanoo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'zibanoo.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CORS_ALLOW_ALL_ORIGINS = True



# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'ZIBANOO',
#         'USER': os.environ.get('db_user'),
#         'PASSWORD': os.environ.get('db_password'),
#         'HOST': os.environ.get('db_host'),
#         'PORT': os.environ.get('db_port'),
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

# ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'yourdomain.com']
USE_I18N = True
LANGUAGE_CODE = 'fa-ir'

TIME_ZONE = 'Asia/Tehran'

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    BASE_DIR / "static"
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# تنظیمات ایمیل (برای ارسال لینک فعال‌سازی)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = os.environ.get('default_from_email')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('email_host')
EMAIL_PORT = os.environ.get('email_port')
EMAIL_USE_TLS = 587
EMAIL_HOST_USER = os.environ.get('email_host_user')
EMAIL_HOST_PASSWORD = os.environ.get('email_host_password')
EMAIL_TIMEOUT = 300

# تنظیم مدل یوزر سفارشی
AUTH_USER_MODEL = 'accounts.CustomUser'

# تنظیمات سایت
SITE_ID = 1


# تنظیمات JWT


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=10),  # مدت اعتبار access token
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),  # مدت اعتبار refresh token
    'ROTATE_REFRESH_TOKENS': True,  # ایجاد refresh token جدید بعد از هر درخواست
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),  # نوع header احراز هویت در API

}

# تنظیمات REST Framework برای استفاده از JWT به عنوان روش احراز هویت
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT احراز هویت
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
SPECTACULAR_SETTINGS = {
    'COMPONENT_SPLIT_REQUEST': True,
}


AZ_IRANIAN_BANK_GATEWAYS = {
    'GATEWAYS': {
        'ZARINPAL': {
            # 'MERCHANT_CODE': '92d1635b-4155-4d64-8bdc-87e89755ea6b',
            'MERCHANT_CODE': '9a668b46-5577-4561-93a8-b24ac3a9d24d',
            'METHOD': 'POST',  # GET or POST
            'SANDBOX': 1,  # 0 disable, 1 active
        },
        'IDPAY': {
            'MERCHANT_CODE': 'ced73ac8-9ec9-40e6-aa47-08757df1be16',
            'METHOD': 'POST',  # GET or POST
            'X_SANDBOX': 1,
        },
    },
    'IS_SAMPLE_FORM_ENABLE': False,
    'DEFAULT': 'IDPAY',
    'CURRENCY': 'IRR',
    'TRACKING_CODE_QUERY_PARAM': 'tc',  # tracking code query parameter
    'TRACKING_CODE_LENGTH': 16,
    'SETTING_VALUE_READER_CLASS': 'azbankgateways.readers.DefaultReader',
    'BANK_PRIORITIES': [
        'ZARINPAL',
    ],  # IDPay priority GATEWAY

    'IS_SAFE_GET_GATEWAY_PAYMENT': True,  # enable secure payment
    'CUSTOM_APP': None,  # optional
}


JAZZMIN_SETTINGS = {
    "site_title": "داشبورد",
    "site_header": "ZIBANOO",
    "site_brand": "ZIBANOO",
    "welcome_sign": "خوش امدین به پنل ادمین ZIBANOO",
    "copyright": "ZIBANOO",
    "order_sidebar_by": "ZIBANOO",
    "show_sidebar": True,
    "show_header": True,
    "navigation_expanded": False,
    "custom_css": "css/custom.css",  # آدرس CSS سفارشی
}
# آدرس JS سفارشی اگر نیاز دارید
# JAZZMIN_SETTINGS["custom_js"] = ("your_custom_js.js",)
