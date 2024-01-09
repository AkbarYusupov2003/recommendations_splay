import requests
from django import forms
from django.contrib import admin

from content import models


class ContentForm(forms.ModelForm):
    kinopoisk_id = forms.CharField(required=False)

    def save(self, commit=True):
        print("TRYING TO SAVE")
        kinopoisk_id = self.cleaned_data.get('kinopoisk_id', None)
        #del self.cleaned_data["kinopoisk_id"]

        # Do something with extra_field here

        return super().save(commit=commit)


@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = (
        "title_ru", "category", "get_genres", "get_sponsors", "get_country", "get_allowed_countries", "slug", "is_serial","draft"
    )
    list_filter = ("draft", "is_serial")
    search_fields = ("title_ru", "title_uz")
    form = ContentForm

    def save_model(self, request, obj, form, change):
        headers = {"X-API-KEY": "DG0DEXV-EDW43B2-G3N8J6K-BA8ECZ6"}
        url = f"https://api.kinopoisk.dev/v1.4/movie/search?query={obj.title_ru}"
        response = requests.get(url, headers=headers)
        print("response", response.json())
        # TODO
        self.message_user(request, "Hsh dfh df")
        return super().save_model(request, obj, form, change)

    def get_genres(self, object):
        res = []
        genres = list(object.genres.all().values_list("name_ru", flat=True))
        for genre in genres:
            res.append(genre)
        return res

    def get_sponsors(self, object):
        res = []
        sponsors = list(object.sponsors.all().values_list("name", flat=True))
        for sponsor in sponsors:
            res.append(sponsor)
        return res

    def get_country(self, object):
        res = []
        countries = list(object.country.all().values_list("name_ru", flat=True))
        for country in countries:
            res.append(country)
        return res

    def get_allowed_countries(self, object):
        res = []
        allowed_countries = list(object.allowed_countries.all().values_list("country_name", flat=True))
        for country in allowed_countries:
            res.append(country)
        return res


admin.site.register(models.AllowedCountry)
admin.site.register(models.ContentSubscription)

admin.site.register(models.CrowdVideo)
admin.site.register(models.CrowdAudio)

admin.site.register(models.Genre)
admin.site.register(models.Sponsor)

admin.site.register(models.Country)
admin.site.register(models.Category)
admin.site.register(models.Person)

admin.site.register(models.ContentSponsor)
admin.site.register(models.ContentGenre)
admin.site.register(models.ContentCountry)


@admin.register(models.ContentActor)
class ContentActorAdmin(admin.ModelAdmin):
    list_display = ("content", "person")
    search_fields = ("content__title_ru", "person__name_ru")


admin.site.register(models.ContentDirector)
admin.site.register(models.ContentProducer)
admin.site.register(models.ContentScenario)


@admin.register(models.ContentCollection)
class ContentCollectionAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "is_recommended", "is_kids")
    list_filter = ("is_recommended", "is_kids")


@admin.register(models.ContentCollectionContent)
class ContentCollectionContentAdmin(admin.ModelAdmin):
    list_display = ("collection_content", "content")
    list_filter = ("collection_content",)
    search_fields = ("content__title_ru", )
