from django.urls import path

from content.api import views

app_name = "content"

urlpatterns = [
    path("<int:content_id>/", views.RecommendationsForDetailAPIView.as_view()),
]
