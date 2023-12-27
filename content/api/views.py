from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, pagination, status, response
from rest_framework.views import APIView
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q

from content import models
from content import documents
from content.api import serializers


class RecommendationsForDetailAPIView(generics.GenericAPIView):
    document = documents.ContentDocument
    serializer_class = serializers.RecommendationsForDetailSerializer
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        # TODO Recommendations from: sponsors, title, genres fields
        age = 18  # self.request.auth.payload.get("age", 18)
        c_code = "UZ"  # self.request.auth.payload.get("c_code", "ALL")

        content = get_object_or_404(models.Content, pk=self.kwargs["content_id"])
        client = Elasticsearch(settings.ELASTICSEARCH_URL)
        sponsors_ids = list(content.sponsors.all().values_list("pk", flat=True))
        sponsors_query = "^1 ".join(str(x) for x in sponsors_ids)
        document = self.document.search().filter("match", allowed_countries__country_code=c_code)
        document = document.filter({"range": {"age_restrictions": {"lte": age}}})#.extra(size=100)

        # response = document.query({
        #     "query_string": {
        #         f"query": f"sponsors.id:({sponsors_query})",
        #         "rewrite": "scoring_boolean"
        #     }
        # })
        print("Sponsors: ", sponsors_ids)
        # Strict title check -> add from sponsors -> add from genres

        res = client.search(
            index="contents",
            body={
                "query": {
                    "query_string": {
                        f"query": f"sponsors.id:({sponsors_query})",
                        "rewrite": "scoring_boolean"
                    },
                }
            }
        )
        for hit in res['hits']['hits']:
            score = hit["_score"]
            source = hit["_source"]
            print(score, f"{source['id']}.{source['title_ru']}", source["sponsors"])

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
