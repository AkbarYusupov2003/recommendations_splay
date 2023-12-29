from django.db.models import Q, Case, Value, When, IntegerField
from django.shortcuts import get_object_or_404
from rest_framework import generics, pagination, status, response
from elasticsearch_dsl import Q as dsl_Q
from elasticsearch_dsl.query import Bool

from content import models
from content import documents
from content import utils
from content.api import serializers


class ContentSearchAPIView(generics.ListAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.RecommendationsForDetailSerializer
    document = documents.ContentDocument

    # def get_serializer_class(self):
    #     type_of_serializer = self.kwargs.get("type_of_serializer", None)
    #     if type_of_serializer == "mobile":
    #         return content_v3_serializers.ContentMobileListSerializer
    #     elif type_of_serializer == "web":
    #         return content_v3_serializers.ContentWebListSerializer
    #     else:
    #         raise ValueError("неверный serializer")

    def get_queryset(self):
        lang = self.request.LANGUAGE_CODE
        search_query = utils.remove_quotes(self.request.query_params.get("search", "").lower())

        age = 18  # self.request._auth.payload['age']
        c_code = "UZ"  # "#self.request._auth.payload['c_code']

        qs = models.Content.objects.filter(
            allowed_countries__in=(c_code, "ALL"),
            age_restrictions__lte=age,
            draft=False
        ).distinct()
        # FILTER
        category = self.request.GET.get("category", None)
        content_lang = self.request.GET.get("content_lang", None)
        country = self.request.GET.get("country", None)
        genres = self.request.GET.get("genres", None)
        year = self.request.GET.get("year", None)
        sponsors = self.request.GET.get("sponsors", None)
        ordering = self.request.GET.get("ordering", None)

        # document = self.document.search().filter("match", allowed_countries__country_code=c_code)
        document = self.document.search().filter(
            Bool(should=[
                dsl_Q({"match": {"allowed_countries.country_code": c_code}}),
                dsl_Q({"match": {"allowed_countries.country_code": "ALL"}})
            ])
        )
        document = document.filter({"range": {"age_restrictions": {"lte": age}}}).extra(size=1000)

        if category:
            res = []
            for i in category.replace(" ", "").rstrip(",").split(","):
                res.append(
                    dsl_Q({"match": {"category.id": i}})
                )
            document = document.filter(Bool(should=res))

        if content_lang == "uzb":
            document = document.filter(
                dsl_Q({"match": {"is_russian": False}})
            )
        elif content_lang == "rus":
            document = document.filter(
                dsl_Q({"match": {"is_russian": True}})
            )

        if country:
            res = []
            for i in country.replace(" ", "").rstrip(",").split(","):
                res.append(
                    dsl_Q({"match": {"country.id": i}})
                )
            document = document.filter(Bool(should=res))

        if genres:
            res = []
            for i in genres.replace(" ", "").rstrip(",").split(","):
                res.append(
                    dsl_Q({"match": {"genres.id": i}})
                )
            document = document.filter(Bool(should=res))

        if sponsors:
            res = []
            for i in sponsors.replace(" ", "").rstrip(",").split(","):
                res.append(
                    dsl_Q({"match": {"sponsors.id": i}})
                )
            document = document.filter(Bool(should=res))

        if year:
            res = []
            for i in year.replace(" ", "").rstrip(",").split(","):
                res.append(
                    dsl_Q({"match": {"year": i}})
                )
            document = document.filter(Bool(should=res))
        # END FILTER

        if (not search_query) or len(search_query) < 3:
            result = [x.id for x in document]
            qs = qs.filter(pk__in=result).order_by(
                Case(
                    *[When(pk=pk, then=Value(i)) for i, pk in enumerate(result)],
                    output_field=IntegerField()
                ).asc()
            )
            if ordering in ("rating", "-rating", "-year", "year", "is_new", "-is_new", "date_created", "-date_created"):
                qs = qs.order_by(ordering)
            return qs

        if lang == "en":
            result = [x.id for x in document]
            qs = qs.filter(pk__in=result).order_by(
                Case(
                    *[When(pk=pk, then=Value(i)) for i, pk in enumerate(result)],
                    output_field=IntegerField()
                ).asc()
            )
            qs = qs.filter(
                Q(title_ru__icontains=search_query) | Q(title_uz__icontains=search_query) | Q(
                    title_en__icontains=search_query)
            )
            if ordering in ("rating", "-rating", "-year", "year", "is_new", "-is_new", "date_created", "-date_created"):
                qs = qs.order_by(ordering)
            return qs

        # START SEARCH
        search_query = [search_query]
        search_again = True
        wrong_cyrillic = True
        to_cyrillic = True

        result = []
        while search_again:
            if len(list(search_query[-1].split())) > 1:
                response = document.query(
                    dsl_Q({"match": {f"title_ru.multiple_words_ngram": {"query": search_query[-1], "fuzziness": "0"}}}) |
                    dsl_Q({"match": {f"title_uz.multiple_words_ngram": {"query": search_query[-1], "fuzziness": "0"}}})
                )
                for x in response:
                    if not (x.id in result):
                        result.append(x.id)
                response = document.query(
                    dsl_Q({"match": {f"title_ru.multiple_words_ngram": {"query": search_query[-1].replace(" ", "-"), "fuzziness": "0"}}}) |
                    dsl_Q({"match": {f"title_uz.multiple_words_ngram": {"query": search_query[-1].replace(" ", "-"), "fuzziness": "0"}}})
                )
                for x in response:
                    if not (x.id in result):
                        result.append(x.id)

            response = document.query(
                dsl_Q({"match": {f"title_ru.strict_edge": {"query": search_query[-1], "fuzziness": "0"}}}) |
                dsl_Q({"match": {f"title_uz.strict_edge": {"query": search_query[-1], "fuzziness": "0"}}})
            )
            for x in response:
                if not (x.id in result):
                    result.append(x.id)
            counter = len(result)

            if counter < 100:
                helper_response = document.query(
                    dsl_Q({"match": {f"title_ru.medium_edge": {"query": search_query[-1], "fuzziness": "0"}}}) |
                    dsl_Q({"match": {f"title_uz.medium_edge": {"query": search_query[-1], "fuzziness": "0"}}})
                )
                for x in helper_response:
                    if not (x.id in result):
                        result.append(x.id)
                counter = len(result)

                if counter < 100:
                    helper_response = document.query(
                        dsl_Q({"match": {f"title_ru.strict_ngram": {"query": search_query[-1], "fuzziness": "0"}}}) |
                        dsl_Q({"match": {f"title_uz.strict_ngram": {"query": search_query[-1], "fuzziness": "0"}}})
                    )
                    for x in helper_response:
                        if not (x.id in result):
                            result.append(x.id)
                    counter = len(result)

                    if counter < 100 and counter != 0:
                        helper_response = document.query(
                            dsl_Q({"match": {f"title_ru.medium_ngram": {"query": search_query[-1], "fuzziness": "0"}}}) |
                            dsl_Q({"match": {f"title_uz.medium_ngram": {"query": search_query[-1], "fuzziness": "0"}}})
                        )
                        for x in helper_response:
                            if not (x.id in result):
                                result.append(x.id)
                        counter = len(result)

                    if counter == 0:
                        helper_response = document.query(
                            dsl_Q({"match": {f"title_ru.soft_edge": {"query": search_query[-1], "fuzziness": "0"}}}) |
                            dsl_Q({"match": {f"title_uz.soft_edge": {"query": search_query[-1], "fuzziness": "0"}}})
                        )
                        for x in helper_response:
                            if not (x.id in result):
                                result.append(x.id)
                        counter = len(result)

                    if counter == 0:
                        helper_response = document.query(
                            dsl_Q({"match": {f"title_ru.soft_edge": {"query": search_query[-1], "fuzziness": "1"}}}) |
                            dsl_Q({"match": {f"title_uz.soft_edge": {"query": search_query[-1], "fuzziness": "1"}}})
                        )
                        for x in helper_response:
                            if not (x.id in result):
                                result.append(x.id)
                        counter = len(result)

                    if counter == 0:
                        helper_response = document.query(
                            dsl_Q({"match": {
                                f"title_ru.very_soft_edge": {"query": search_query[-1], "fuzziness": "0"}}}) |
                            dsl_Q(
                                {"match": {f"title_uz.very_soft_edge": {"query": search_query[-1], "fuzziness": "0"}}})
                        )
                        for x in helper_response:
                            if not (x.id in result):
                                result.append(x.id)
                        counter = len(result)

                    if counter == 0 and wrong_cyrillic:
                        translated = utils.wrong_cyrillic_translate(search_query[0])
                        if search_query[0] == translated:
                            search_again = False
                        else:
                            search_query.append(translated)
                            search_again = True
                        wrong_cyrillic = False
                    else:
                        wrong_cyrillic = False
                        search_again = False

                    if (not search_again) and to_cyrillic:
                        translated = utils.to_cyrillic_translate(search_query[0])
                        if search_query[0] == translated:
                            search_again = False
                        else:
                            search_query.append(translated)
                            search_again = True
                        to_cyrillic = False

            if not search_again:
                qs = qs.filter(pk__in=result).order_by(
                    Case(
                        *[When(pk=pk, then=Value(i)) for i, pk in enumerate(result)],
                        output_field=IntegerField()
                    ).asc()
                )
                if ordering in ("rating", "-rating", "-year", "year", "is_new", "-is_new", "date_created", "-date_created"):
                    qs = qs.order_by(ordering)
                return qs

    def get(self, request, *args, **kwargs):
        if self.request.LANGUAGE_CODE in ["uz", "ru", "en"]:
            return super().get(request, *args, **kwargs)
        return response.Response(status=400)


class DetailRecommendationsAPIView(generics.ListAPIView):
    document = documents.ContentDocument
    serializer_class = serializers.RecommendationsForDetailSerializer
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        lang = self.request.LANGUAGE_CODE
        age = 18  # self.request.auth.payload.get("age", 18)
        c_code = "UZ"  # self.request.auth.payload.get("c_code", "ALL")
        # TODO Title -> Collections -> Sponsors -> Actors -> Genres
        content = get_object_or_404(models.Content, pk=self.kwargs["content_id"], draft=False)
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
                "match": {f"title_{lang}.strict_edge": {"query": content.title_ru, "fuzziness": "0"}}
            })
        )
        result = []
        for x in document:
            result.append(x.id)
        result.sort(reverse=True)
        # Filtering by collections
        collection_pks = list(content.collection.all().values_list("collection_content", flat=True).distinct())
        recommended = models.ContentCollectionContent.objects.filter(
            collection_content__in=collection_pks
        ).values_list("content", flat=True).distinct()[:50-len(result)]
        result.extend(recommended)
        # Filtering by sponsors
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
        # Filtering by actors
        if content.actors.exists():
            query = "^1 ".join(str(x) for x in list(content.actors.all().values_list("pk", flat=True))) + "^1"
            document = base_document.query({
                "query_string": {
                    "query": f"actors.id:({query})",
                    "rewrite": "scoring_boolean"
                }
            })
            for x in document:
                if x not in result:
                    result.append(x.id)
        # Filtering by genres
        if len(result) < 30:
            if content.genres.exists():
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
        qs = models.Content.objects.filter(pk__in=result).order_by(
            Case(
                *[When(pk=pk, then=Value(i)) for i, pk in enumerate(result)],
                output_field=IntegerField()
            ).asc()
        ).prefetch_related("sponsors", "genres")
        return qs

    def get(self, request, *args, **kwargs):
        if self.request.LANGUAGE_CODE in ["uz", "ru", "en"]:
            return super().get(request, *args, **kwargs)
        return response.Response(status=400)
