from django.conf import settings
from django.utils import translation
from django.db.models.fields import files
from rest_framework import serializers


langs = settings.LANGUAGES


class StdImageSerializer(serializers.ImageField):
    """
    Get all the variations of the StdImageField
    """

    def to_native(self, obj):
        return self.get_variations_urls(obj)

    def to_representation(self, obj):
        if not obj:
            return None
        return self.get_variations_urls(obj)

    def get_variations_urls(self, obj):
        """
        Get all the logo urls.
        """

        # Initiate return object
        return_object = {}

        # Get the field of the object
        field = obj.field

        # A lot of ifs going araound, first check if it has the field variations
        if hasattr(field, 'variations'):
            # Get the variations
            variations = field.variations
            # Go through the variations dict
            for key in variations.keys():
                # Just to be sure if the stdimage object has it stored in the obj
                if hasattr(obj, key):
                    # get the by stdimage properties
                    field_obj = getattr(obj, key, None)
                    if field_obj and hasattr(field_obj, 'url'):
                        # store it, with the name of the variation type into our return object
                        return_object[key] = super(StdImageSerializer, self).to_representation(field_obj)

        # Also include the original (if possible)
        if hasattr(obj, 'url'):
            return_object['original'] = super(StdImageSerializer, self).to_representation(obj)

        return return_object


class NameISOSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        def file_serialize(field):
            serializers.FileField.context = self.context
            return serializers.FileField().to_representation(field)

        i18n_fields = getattr(self.Meta, 'i18n_fields', dict())
        representation = super().to_representation(instance)
        for field in i18n_fields.get("exact", list()):
            representation[f'{field}'] = getattr(instance, f"{field}_{translation.get_language()}", None)
            if isinstance(representation[f'{field}'], files.FieldFile):
                representation[f'{field}'] = file_serialize(representation[f'{field}'])
        for field in i18n_fields.get("catch", list()):
            representation[f'{field}'] = getattr(instance, f"{field}_{translation.get_language()}", None)
            if isinstance(representation[f'{field}'], files.FieldFile):
                representation[f'{field}'] = file_serialize(representation[f'{field}'])
            if not representation[f"{field}"]:
                for iso, lang in langs:
                    if getattr(instance, f'{field}_{iso}', None):
                        representation[f'{field}'] = getattr(instance, f"{field}_{iso}", None)
                        if isinstance(representation[f'{field}'], files.FieldFile):
                            representation[f'{field}'] = file_serialize(representation[f'{field}'])
                        break
        return representation

    class Meta:
        model = None
        i18n_fields: dict = {
            "catch": list(),
            "exact": list(),
        }
        fields = list()

