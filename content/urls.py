from django.urls import path

from content import views


app_name = "content"

urlpatterns = [
    path("<int:content_id>/", views.RecommendationsFromContentAPIView.as_view()),
]
