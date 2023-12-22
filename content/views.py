from django.shortcuts import get_object_or_404
from rest_framework import status, generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response

from content import models


class RecommendationsFromContentAPIView(APIView):

    def get(self, request, *args, **kwargs):
        # TODO Recommendations from: sponsors, title, genres
        # TODO from jwt get age, allowed_countries

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
        return Response({"message": "ok"}, status=200)


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
