from rest_framework import serializers

from content import models
from content.api.serializers import base


class ContentSponsorListSerializer(base.NameISOSerializer):
    id = serializers.IntegerField(source='sponsor.id')
    name = serializers.CharField(source="sponsor.name")

    class Meta:
        model = models.ContentSponsor
        fields = "id", "name",


class ContentGenreListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='genre.id')
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.ContentGenre
        fields = "id", "name"

    def get_name(self, obj):
        return getattr(obj.genre, f"name_{self.context['request'].LANGUAGE_CODE}", None)


class RecommendationsForDetailSerializer(base.NameISOSerializer):
    poster_h = base.StdImageSerializer()
    sponsors = serializers.SerializerMethodField()
    genres = serializers.SerializerMethodField()

    class Meta:
        model = models.Content
        i18n_fields: dict = {
            "catch": list(),
            "exact": ("title",),
        }
        fields = (
            "id",
            "sponsors",
            "genres",
            # "is_serial",
            # "is_new",
            # "is_russian",
            "poster_h",
            # "rating",
            # "age_restrictions",
        )

    def get_sponsors(self, obj):
        return ContentSponsorListSerializer(obj.content_sponsors.all(), context=self.context, many=True).data

    def get_genres(self, obj):
        return ContentGenreListSerializer(obj.content_genres.all(), context=self.context, many=True).data
