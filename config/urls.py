from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    # path("recommendations/", include("content.urls", namespace="content")),
    path("", include("content.urls", namespace="content")),
]
