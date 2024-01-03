from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_elasticsearch_dsl.registries import registry

from content import utils


@receiver(post_save)
def update_document(sender, **kwargs):
    print("UPDATE DOCUMENT")
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    instance = kwargs['instance']
    if app_label == 'content':
        if model_name == 'content':
            if kwargs.get('update_fields') != frozenset(("rating", "rating_count")):
                if kwargs["instance"].draft == True:
                    registry.delete_related(instance)
                    registry.delete(instance)
                else:
                    instance.title_uz = utils.remove_quotes(instance.title_uz)
                    instance.title_ru = utils.remove_quotes(instance.title_ru)
                    registry.update(instance)


@receiver(post_delete)
def delete_document(sender, **kwargs):
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    instance = kwargs["instance"]

    if app_label == "content":
        if model_name == "content":
            registry.update(instance)
