from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, pagination, status, response
from rest_framework.views import APIView
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q as dsl_Q

from content import models
from content import documents
from content.api import serializers


class RecommendationsForDetailAPIView(generics.GenericAPIView):
    document = documents.ContentDocument
    serializer_class = serializers.RecommendationsForDetailSerializer
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        age = 18  # self.request.auth.payload.get("age", 18)
        c_code = "UZ"  # self.request.auth.payload.get("c_code", "ALL")

        content = get_object_or_404(
            models.Content, pk=self.kwargs["content_id"], age_restrictions__gte=age, allowed_countries__country_code=c_code
        )
        document = self.document.search().filter("match", allowed_countries__country_code=c_code)
        document = document.filter({"range": {"age_restrictions": {"lte": age}}}) # .extra(size=1000)
        # TODO Strict title check -> add from sponsors -> add from genres
        # TODO Try to find with current title -> if not found split title by words -> Try to find ->

        # Filtering by title
        document = document.filter(
            dsl_Q({
                "match": {"title_ru.strict_edge": {"query": content.title_ru, "fuzziness": "0"}}
            })
        )
        result = []
        for x in document:
            result.append(x)
        # Filtering by sponsors
        query = "^1 ".join(str(x) for x in list(content.sponsors.all().values_list("pk", flat=True)))
        document = document.query({
            "query_string": {
                "query": f"sponsors.id:({query})",
                "rewrite": "scoring_boolean"
            }
        })
        for x in document:
            if x not in result:
                result.append(x)
        # Filtering by genres
        if len(result) < 30:
            query = "^1 ".join(str(x) for x in list(content.genres.all().values_list("pk", flat=True)))
            document = document.query({
                "query_string": {
                    "query": f"genres.id:({query}",
                    "rewrite": "scoring_boolean"
                }
            })
            for x in document:
                if x not in result:
                    result.append(x)

        return models.Content.objects.all()

    def get(self, request, *args, **kwargs):
        if self.request.LANGUAGE_CODE == "uz" or self.request.LANGUAGE_CODE == "ru":
            queryset = self.get_queryset()
            results = self.paginate_queryset(queryset)
            res = self.get_serializer(results, many=True)
            return self.get_paginated_response(res.data)

        return response.Response(status=status.HTTP_400_BAD_REQUEST)


# def tester():
#     contents = models.Content.objects.all()
#     counter = 0
#     print(
#         contents.get(pk=3555).title_ru, contents.get(pk=3555).sponsors.all()
#     )
#     for content in contents:
#         if len(content.genres.all()) == 0:
#             print(content.title_ru)
#         counter += 1

def test():
    contents = models.Content.objects.all()
    max_sponsors = 0
    for content in contents:
        c = content.genres.all().count()
        if c > max_sponsors:
            max_sponsors = c
    print("MAX", max_sponsors)
