import requests
from bs4 import BeautifulSoup
from django import forms
from django.contrib import admin, messages

from content import models


class ContentForm(forms.ModelForm):
    kinopoisk_id = forms.CharField(required=False)


@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = (
        "title_ru", "category", "get_genres", "get_sponsors", "get_country", "get_allowed_countries", "slug", "is_serial","draft"
    )
    list_filter = ("draft", "is_serial")
    search_fields = ("title_ru", "title_uz")
    form = ContentForm

    def save_model(self, request, obj, form, change):
        obj.save()
        soup = BeautifulSoup(str(form), features="lxml")
        kinopoisk_input = soup.find("input", id="id_kinopoisk_id")
        if kinopoisk_input.has_attr("value"): # obj.kinopoisk_id
            headers = {"X-API-KEY": "DG0DEXV-EDW43B2-G3N8J6K-BA8ECZ6"}
            kinopoisk_id = kinopoisk_input['value']
            url = f"https://api.kinopoisk.dev/v1.4/movie/{kinopoisk_id}" # obj.kinopoisk_id
            response = requests.get(url, headers=headers)
            status = response.status_code
            if status == 200:
                result = response.json()

                rating_imdb = result["rating"]["imdb"]
                if rating_imdb:
                    print("imdb: ", rating_imdb)
                    obj.rating_imdb = rating_imdb
                    obj.save()

                for res_person in result["persons"]:
                    exists = models.Person.objects.filter(name_ru__iexact=res_person["name"]).first()
                    if exists:
                        person = exists
                    else:
                        person = models.Person.objects.create(
                            name_ru=res_person["name"],
                        )

                    if res_person["profession"] == "актеры":
                        models.ContentActor.objects.get_or_create(content=obj, person=person)

                    elif res_person["profession"] == "режиссеры":
                        models.ContentDirector.objects.get_or_create(content=obj, person=person)

                    elif res_person["profession"] == "продюсеры":
                        models.ContentProducer.objects.get_or_create(content=obj, person=person)

                    elif res_person["profession"] == "сценаристы":
                        models.ContentScenario.objects.get_or_create(content=obj, person=person)

                self.message_user(
                    request,
                    "Данные из кинопоиска успешно добавлены",
                    level=messages.SUCCESS
                )
            else:
                errors_dict = {401: "Unauthorized", 403: "Forbidden", 404: "NotFound"}
                if status in errors_dict.keys():
                    self.message_user(
                        request,
                        f"Произошла ошибка с добавлением данных из кинопоиска. На API сервере: {errors_dict[status]}",
                        level=messages.ERROR
                    )
                else:
                    self.message_user(
                        request,
                        f"Произошла ошибка с добавлением данных из кинопоиска. На API сервере: {status} код",
                        level=messages.ERROR
                    )

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


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("name_ru", )


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
