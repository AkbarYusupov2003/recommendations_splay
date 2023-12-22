SECRET_KEY = "123"
DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "recommendations_splay",
        "USER": "postgres",
        "PASSWORD": "123456",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
