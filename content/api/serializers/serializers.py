from content import models
from content.api.serializers import base
from rest_framework import serializers


class RecommendationsForDetailSerializer(base.NameISOSerializer):
    poster_h = base.StdImageSerializer()

    class Meta:
        model = models.Content
        i18n_fields: dict = {
            "catch": list(),
            "exact": ("title",),
        }
        fields = (
            "id",
            "is_serial",
            "is_new",
            "is_russian",
            "poster_h",
            "rating",
            "age_restrictions",
        )