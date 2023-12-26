from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, pagination, status, response
from rest_framework.views import APIView
from elasticsearch_dsl import Q

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

        age = 18  # self.request.auth.payload.get("age", 18)
        c_code = "UZ"  # self.request.auth.payload.get("c_code", "ALL")

        content = get_object_or_404(
            models.Content,
            pk=self.kwargs["content_id"]
        )
        document = self.document.search().filter("match", allowed_countries__country_code=c_code).extra(size=100)
        #document = document.filter({"range": {"age_restrictions": {"lte": age}}}).extra(size=100)
        print("d", document.count())
        res = []
        sponsors_ids = list(content.sponsors.all().values_list("pk", flat=True))
        doc_res = document.query(
            Q({"match": {"category.id": "2"}}) #sponsors_ids}})
        )
        print("count", doc_res.count())
        for x in doc_res:
            print("x", x)

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
