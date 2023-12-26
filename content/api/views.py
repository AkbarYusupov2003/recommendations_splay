from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, pagination, status, response
from rest_framework.views import APIView

from content import models
from content import documents
from content.api import serializers


class RecommendationsForDetailAPIView(generics.GenericAPIView):
    document = documents.ContentDocument
    serializer_class = serializers.RecommendationsForDetailSerializer
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        # TODO Recommendations from: sponsors, title, genres
        # TODO from jwt get age, allowed_countries
        lang = self.request.LANGUAGE_CODE

        age_restrictions = 18  # self.request.auth.payload.get("age", 18)
        country_code = "UZ"  # self.request.auth.payload.get("c_code", "ALL")

        content = get_object_or_404(
            models.Content,
            pk=self.kwargs["content_id"]
        )
        allowed_contents = models.Content.objects.all()

        print("\n")
        print("title: ", content.title_ru)
        print("sponsors: ", content.sponsors.all())
        print("genres: ", content.genres.all())
        print("\n")
        return models.Content.objects.all()

    def get(self, request, *args, **kwargs):
        if self.request.LANGUAGE_CODE == "uz" or self.request.LANGUAGE_CODE == "ru":
            queryset = self.get_queryset()
            results = self.paginate_queryset(queryset)
            res = self.get_serializer(results, many=True)
            return self.get_paginated_response(res.data)

        return response.Response(status=status.HTTP_400_BAD_REQUEST)


def tester():
    contents = models.Content.objects.all()
    counter = 0
    print(
        contents.get(pk=3555).title_ru, contents.get(pk=3555).sponsors.all()
    )
    for content in contents:
        if len(content.genres.all()) == 0:
            print(content.title_ru)
        counter += 1
