from django.db.models import Case, Value, When, IntegerField
from django.shortcuts import get_object_or_404
from rest_framework import generics, pagination, status, response
from elasticsearch_dsl import Q as dsl_Q
from elasticsearch_dsl.query import Bool

from content import models
from content import documents
from content.api import serializers


class DetailRecommendationsAPIView(generics.GenericAPIView):
    document = documents.ContentDocument
    serializer_class = serializers.RecommendationsForDetailSerializer
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        age = 18  # self.request.auth.payload.get("age", 18)
        c_code = "UZ"  # self.request.auth.payload.get("c_code", "ALL")

        content = get_object_or_404(
            models.Content,
            pk=self.kwargs["content_id"], age_restrictions__lte=age, allowed_countries__in=(c_code, "ALL")
        )
        base_document = self.document.search().filter(
            Bool(should=[
                dsl_Q({"match": {"allowed_countries.country_code": c_code}}),
                dsl_Q({"match": {"allowed_countries.country_code": "ALL"}})
            ])
        )
        base_document = base_document.filter(
            Bool(must=[
                dsl_Q({"match": {"category.id": content.category_id}}),
            ])
        )
        base_document = base_document.filter(
            Bool(must_not=[
                dsl_Q({"match": {"id": content.pk}}),
                dsl_Q({"range": {"age_restrictions": {"gt": age}}})
            ])
        ).extra(size=50)
        # Filtering by title
        document = base_document.filter(
            dsl_Q({
                "match": {"title_ru.strict_ngram": {"query": content.title_ru, "fuzziness": "0"}}
            })
        )
        result = []
        for x in document:
            result.append(x.id)
        result.sort(reverse=True)
        # Filtering by sponsors
        print("r1", result)
        if content.sponsors.exists():
            query = "^1 ".join(str(x) for x in list(content.sponsors.all().values_list("pk", flat=True))) + "^1"
            document = base_document.query({
                "query_string": {
                    "query": f"sponsors.id:({query})",
                    "rewrite": "scoring_boolean"
                }
            })
            for x in document:
                if x not in result:
                    result.append(x.id)
        print("r2", result)
        # Filtering by genres
        if content.genres.exists():
            if len(result) < 30:
                query = "^1 ".join(str(x) for x in list(content.genres.all().values_list("pk", flat=True))) + "^1"
                document = base_document.query({
                    "query_string": {
                        "query": f"genres.id:({query})",
                        "rewrite": "scoring_boolean"
                    }
                }).extra(size=30)
                for x in document:
                    if x not in result:
                        result.append(x.id)
        print("r3", result)
        qs = models.Content.objects.filter(pk__in=result).order_by(
            Case(
                *[When(pk=pk, then=Value(i)) for i, pk in enumerate(result)],
                output_field=IntegerField()
            ).asc()
        ).prefetch_related("sponsors", "genres")
        return qs

    def get(self, request, *args, **kwargs):
        if self.request.LANGUAGE_CODE == "uz" or self.request.LANGUAGE_CODE == "ru":
            queryset = self.get_queryset()
            results = self.paginate_queryset(queryset)
            res = self.get_serializer(results, many=True)
            return self.get_paginated_response(res.data)

        return response.Response(status=status.HTTP_400_BAD_REQUEST)
