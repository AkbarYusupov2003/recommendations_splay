from django.contrib import admin

from content import models


@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = (
        "title_ru", "category", "get_genres", "get_sponsors", "get_country", "get_allowed_countries", "slug", "is_serial","draft"
    )
    list_filter = ("draft", "is_serial")
    search_fields = ("title_ru", "title_uz")

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


@admin.register(models.ContentCollection)
class ContentCollectionAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "is_recommended", "is_kids")
    list_filter = ("is_recommended", "is_kids")


@admin.register(models.ContentCollectionContent)
class ContentCollectionContentAdmin(admin.ModelAdmin):
    list_display = ("collection_content", "content")
    list_filter = ("collection_content",)
    search_fields = ("content__title_ru", )

