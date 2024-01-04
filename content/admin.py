import re
import requests
from lxml.html import fromstring
from django.contrib import admin

from content import models


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Connection": "keep-alive",
    "Cookie": "_yasc=VDySndpJfWuqTW26TlWbjIno7yzLLBZ78SHtuWVyOzuXvIy0gOfxaSSLM9n/gd4FIe5i; i=aG07CboIOI0F1uJCHCPf/cTc3tZ/9cx9/wyWJ83wSV3RJYTiLYgq7YXFK6+oO+PLN4QTBYTpl0k8X+4R9DZGILaGk8M=; yandexuid=2869332001704254694; _ym_uid=1703855575299104992; _ym_d=1704350533; yandex_login=; mda2_beacon=1704350284916; cycada=VXT/o0iKICizsHhPlY1LNSxORIvNO2b0/oq+nscZWlg=; my_perpages=%5B%5D; mobile=no; mda_exp_enabled=1; no-re-reg-required=1; session_key=eyJzZWNyZXQiOiJUNnF0c21aUlRwNnhYQUNUWXNSbUlaMFIiLCJfZXhwaXJlIjoxNzA0MzU5NDM3NDc4LCJ…AvrQYtL_0j7OnYMCg.oKGB7qsQzcVG_qaNpaV25kcr789J-rJn0fa9YkMjiNI; ys=c_chck.3939831260; sso_status=sso.passport.yandex.ru:synchronized; desktop_session_key=0d44d88f8dc39a4ab0623917e4ba139ad507e2f323f0e811d18352adf0a1c928b43bce39bbd7f24e7ec01ed54b5fae4ca1109808c4301c42f7fd90796bbdb474b2d26f012ca3b6ff6a5b896cd67235630cacf64d4451429388c6d54a61c438fd; desktop_session_key.sig=eiPOBomguIqxIwHt-V2_a3pAsvE; gdpr=0; _ym_isad=2; _ym_visorc=b; PHPSESSID=25503831e464283ada86cebd7161a74b; user_country=uz; yandex_gid=10335",
    "Host": "www.kinopoisk.ru",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "1",
    "TE": "trailers",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
}


@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = (
        "title_ru", "category", "get_genres", "get_sponsors", "get_country", "get_allowed_countries", "slug", "is_serial","draft"
    )
    list_filter = ("draft", "is_serial")
    search_fields = ("title_ru", "title_uz")

    def save_model(self, request, obj, form, change):
        # get persons and ratings from kinopoisk
        api_key = "DG0DEXV-EDW43B2-G3N8J6K-BA8ECZ6"
        url = f"https://api.kinopoisk.dev/v1.4/movie/search?query={obj.title_ru}"
        response = request.get(url, {"X-API-KEY": api_key})
        # TODO
        return super().save_model(request, obj, form, change)

    # def save_model(self, request, obj, form, change):
    #     # get persons and ratings from kinopoisk
    #     url = f"https://www.kinopoisk.ru/series/5304403/"
    #     response = requests.get(url=url)
    #
    #     if "sso.passport.yandex" in response.url:
    #         val = re.findall(r'var it =\s*(.*?);', response.text, re.DOTALL | re.MULTILINE)[0]
    #         val = re.findall(r'"retpath":\s*(.*?)', val, re.DOTALL | re.MULTILINE)[0].replace("\\u002F", "/")
    #     elif "showcaptcha" in response.url:
    #         # Каптча 1. С галочкой 2. С изображением и аудио
    #         pass
    #     return super().save_model(request, obj, form, change)

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
