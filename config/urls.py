from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include


urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("content.urls", namespace="content")),
)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
