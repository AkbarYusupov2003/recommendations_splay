SECRET_KEY = "123"
DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "recommendations_content",
        "USER": "postgres",
        "PASSWORD": "123456",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

ELASTICSEARCH__USERNAME = "elastic"
ELASTICSEARCH__PASSWORD = "ml0LOVWEX14gs8nvrqi="
ELASTICSEARCH__HOST_IP = "localhost"
ELASTICSEARCH__HOST_PORT = "9200"
ELASTICSEARCH_URL = f'elasticsearch://{ELASTICSEARCH__USERNAME}:{ELASTICSEARCH__PASSWORD}@{ELASTICSEARCH__HOST_IP}:{ELASTICSEARCH__HOST_PORT}'

ELASTICSEARCH_DSL = {
    "default": {
        "hosts": ELASTICSEARCH_URL
    },
}

ELASTICSEARCH_INDEX_NAMES = {
    "content.content": "contents",
}
