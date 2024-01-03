import requests
import shutil
from django.contrib import admin
from lxml.html import fromstring

from content import models


def get_page_with_captcha(self, page_text):
    html = fromstring(page_text)
    # Get captcha image URL
    img = html.xpath('//div[@class="captcha__image"]//img')
    captcha_url = img[0].get('src')
    # Get captcha key
    input_captcha_key = html.xpath('//input[@class="form__key"]')
    captcha_key = input_captcha_key[0].get('value')
    # Get return path
    input_retpath = html.xpath('//input[@class="form__retpath"]')
    retpath = input_retpath[0].get('value')

    print(f"Captch URL = {captcha_url}, key = {captcha_key}")

    r = requests.get(captcha_url, stream=True)
    if r.status_code != 200:
        raise Exception('Could not download captcha image')
    captcha_filename = self.cache.get_cached_filename(captcha_url)
    with open(captcha_filename, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

    solver = CaptchaSolver(captcha_filename)
    task_id = solver.CreateTask()
    solution = solver.GetTaskResult(task_id)
    if not solution:
        print("Could not solve captcha")
        return None

    params = {'key': captcha_key, 'retpath': retpath, 'rep': solution}
    r = requests.get('https://www.kinopoisk.ru/checkcaptcha', params=params)
    # /checkcaptcha example:
    # https://www.kinopoisk.ru/checkcaptcha?key=<key>&retpath=<retpath>&rep=%D0%BB%D1%8E%D0%BD%D0%B3%D1%81%D1%82%D0%B0%D0%B4
    if r.status_code == 200:
        print("CAPTCHA SOLVED")

    return r


@admin.register(models.Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = (
        "title_ru", "category", "get_genres", "get_sponsors", "get_country", "get_allowed_countries", "slug", "is_serial","draft"
    )
    list_filter = ("draft", "is_serial")
    search_fields = ("title_ru", "title_uz")

    def save_model(self, request, obj, form, change):
        print("SAVE MODEL", request)
        # get persons and ratings from kinopoisk
        url = f"https://www.kinopoisk.ru/series/5304403/" # {obj.title_ru}
        response = requests.get(url=url)
        print("url: ", response.url)
        if response.url == url:
            pass

        # print("json: ", r.json())
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

