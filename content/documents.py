from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from content import utils
from content import models
from content import analyzers


@registry.register_document
class ContentDocument(Document):
    title_ru = fields.TextField(
        attr="title_ru",
        fields={
            "multiple_words_ngram": fields.TextField(analyzer=analyzers.multiple_words_analyzer),
            "strict_edge": fields.TextField(analyzer=analyzers.strict_edge_ngram_analyzer),
            "medium_edge": fields.TextField(analyzer=analyzers.medium_edge_ngram_analyzer),
            "soft_edge": fields.TextField(analyzer=analyzers.soft_edge_ngram_analyzer),
            "very_soft_edge": fields.TextField(analyzer=analyzers.very_soft_edge_ngram_analyzer),
            "strict_ngram": fields.TextField(analyzer=analyzers.strict_ngram_analyzer),
            "medium_ngram": fields.TextField(analyzer=analyzers.medium_ngram_analyzer),
        }
    )
    title_uz = fields.TextField(
        attr="title_uz",
        fields={
            "multiple_words_ngram": fields.TextField(analyzer=analyzers.multiple_words_analyzer),
            "strict_edge": fields.TextField(analyzer=analyzers.strict_edge_ngram_analyzer),
            "medium_edge": fields.TextField(analyzer=analyzers.medium_edge_ngram_analyzer),
            "soft_edge": fields.TextField(analyzer=analyzers.soft_edge_ngram_analyzer),
            "very_soft_edge": fields.TextField(analyzer=analyzers.very_soft_edge_ngram_analyzer),
            "strict_ngram": fields.TextField(analyzer=analyzers.strict_ngram_analyzer),
            "medium_ngram": fields.TextField(analyzer=analyzers.medium_ngram_analyzer),
        }
    )
    # -------------------------------------------------------------------------------------------
    age_restrictions = fields.IntegerField(
        attr="age_restrictions"
    )
    allowed_countries = fields.ObjectField(
        attr="allowed_countries",
        properties={
            "country_code": fields.TextField(),
            "country_name": fields.TextField(),
        }
    )
    year = fields.IntegerField(attr="year")
    # -------------------------------------------------------------------------------------------
    category = fields.ObjectField(
        attr="category",
        properties={
            "id": fields.IntegerField(),
            # "name_uz": fields.TextField(),
            # "name_ru": fields.TextField(),
        }
    )
    country = fields.ObjectField(
        attr="country",
        properties={
            "id": fields.IntegerField(),
            # "name_uz": fields.TextField(),
            # "name_ru": fields.TextField(),
        },
        multi=True
    )
    genres = fields.ObjectField(
        attr="genres",
        properties={
            "id": fields.IntegerField(),
            # "name_uz": fields.TextField(),
            # "name_ru": fields.TextField(),
            # "slug": fields.TextField(),
            # "ordering": fields.IntegerField()
        },
        multi=True
    )
    sponsors = fields.ObjectField(
        attr="sponsors",
        properties={
            "id": fields.IntegerField(),
            # "name": fields.TextField(),
        },
        multi=True
    )
    # -------------------------------------------------------------------------------------------

    def get_queryset(self):
        return super().get_queryset().filter(draft=False).select_related(
            "category"
        ).prefetch_related("allowed_countries")

    def get_indexing_queryset(self):
        qs = self.get_queryset()
        res = []
        for content in qs:
            obj = content.__dict__
            allowed_countries = []
            for country in content.allowed_countries.all():
                allowed_countries.append({
                    "country_code": country.country_code, "country_name": country.country_name
                })
            obj["allowed_countries"] = allowed_countries

            genres = []
            for genre in content.genres.all():
                genres.append({"id": genre.pk})
            obj["genres"] = genres

            sponsors = []
            for sponsor in content.sponsors.all():
                sponsors.append({"id": sponsor.pk})
            obj["sponsors"] = sponsors

            countries = []
            for country in content.country.all():
                countries.append({"id": country.pk})
            obj["country"] = countries

            obj["category"] = {"id": content.category.pk}
            obj["pk"] = content.pk
            obj["title_uz"] = utils.remove_quotes(obj["title_uz"])
            obj["title_ru"] = utils.remove_quotes(obj["title_ru"])
            res.append(obj)
        return res

    @classmethod
    def generate_id(cls, object_instance):
        try:
            return object_instance.get("pk")
        except:
            return object_instance.pk

    class Index:
        name = "contents"

    class Django:
        model = models.Content
        fields = ["id", "is_russian", "rating", "rating_count", "date_created"]
