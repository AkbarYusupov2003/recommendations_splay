from django.contrib import admin

from app import models


admin.site.register(models.AllowedCountry)
admin.site.register(models.ContentSubscription)

admin.site.register(models.CrowdVideo)
admin.site.register(models.CrowdAudio)

admin.site.register(models.Genre)
admin.site.register(models.Sponsor)

admin.site.register(models.Country)
admin.site.register(models.Category)
admin.site.register(models.Person)

admin.site.register(models.Content)

admin.site.register(models.ContentSponsor)
admin.site.register(models.ContentGenre)
admin.site.register(models.ContentCountry)
