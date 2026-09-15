from pathlib import Path
import os
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR/".env")
SECRET_KEY=os.getenv("SECRET_KEY","nexacrm-development-secret-key-change-in-production")
DEBUG=os.getenv("DEBUG","True").lower()=="true"
ALLOWED_HOSTS=[h.strip() for h in os.getenv("ALLOWED_HOSTS","127.0.0.1,localhost,.vercel.app").split(",") if h.strip()]
INSTALLED_APPS=["django.contrib.admin","django.contrib.auth","django.contrib.contenttypes","django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles","crmapp"]
MIDDLEWARE=["django.middleware.security.SecurityMiddleware","whitenoise.middleware.WhiteNoiseMiddleware","django.contrib.sessions.middleware.SessionMiddleware","django.middleware.common.CommonMiddleware","django.middleware.csrf.CsrfViewMiddleware","django.contrib.auth.middleware.AuthenticationMiddleware","django.contrib.messages.middleware.MessageMiddleware","django.middleware.clickjacking.XFrameOptionsMiddleware"]
ROOT_URLCONF="crm.urls"
TEMPLATES=[{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[BASE_DIR/"templates"],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION="crm.wsgi.application"
DB_ENGINE=os.getenv("DB_ENGINE","sqlite")
if DB_ENGINE=="postgres":
    DATABASES={"default":{"ENGINE":"django.db.backends.postgresql","NAME":os.getenv("DB_NAME","nexacrm"),"USER":os.getenv("DB_USER","postgres"),"PASSWORD":os.getenv("DB_PASSWORD",""),"HOST":os.getenv("DB_HOST","localhost"),"PORT":os.getenv("DB_PORT","5432")}}
else: DATABASES={"default":{"ENGINE":"django.db.backends.sqlite3","NAME":BASE_DIR/"db.sqlite3"}}
AUTH_PASSWORD_VALIDATORS=[]
LANGUAGE_CODE="en-us"; TIME_ZONE="Asia/Kolkata"; USE_I18N=True; USE_TZ=True
STATIC_URL="/static/"; STATIC_ROOT=BASE_DIR/"staticfiles"; STATICFILES_DIRS=[BASE_DIR/"static"]
STATICFILES_STORAGE="whitenoise.storage.CompressedManifestStaticFilesStorage"
DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"
LOGIN_URL="/login/"; LOGIN_REDIRECT_URL="/dashboard/"; LOGOUT_REDIRECT_URL="/login/"
CSRF_TRUSTED_ORIGINS=[x.strip() for x in os.getenv("CSRF_TRUSTED_ORIGINS","https://*.vercel.app").split(",") if x.strip()]
if not DEBUG:
    SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO","https")
    SESSION_COOKIE_SECURE=True; CSRF_COOKIE_SECURE=True
