from django.urls import path

from content.api import views


app_name = "content"

urlpatterns = [
    path("<str:type_of_serializer>/content-search/", views.ContentSearchAPIView.as_view()),
    path("<str:type_of_serializer>/<int:content_id>/", views.DetailRecommendationsAPIView.as_view()),
]
