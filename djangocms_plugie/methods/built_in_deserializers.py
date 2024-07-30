from django.apps import apps
from djangocms_plugie.version0.utils import handle_special_plugin_fields


def deserialize_relatedmanager(instance, importer, **kwargs):
    model_label = kwargs.get('_model_label', None)
    plugin = kwargs.get('_plugin_id', None)
    created_instances = []
    if model_label is not None and plugin is not None:
        model_class = apps.get_model(*model_label.split('.'))
        for instance_data in instance:
            instance_data.pop('meta', None)
            processed_fields = handle_special_plugin_fields(
                instance_data, plugin, importer.method_map)
            model_instance = model_class.objects.create(**processed_fields)
            model_instance.save()
            created_instances.append(model_instance)

    return created_instances


def deserialize_manyrelatedmanager(instance, importer, **kwargs):
    instances = []
    plugin_id = kwargs.get('_plugin_id', None)
    for instance_data in instance:
        fields = {'key': instance_data}
        processed_fields = handle_special_plugin_fields(
            fields, plugin_id, importer.method_map)
        instances.append(processed_fields['key'])
    return instances


def register_deserializers(importer):
    def relatedmanager_deserializer(instance, **kwargs):
        return deserialize_relatedmanager(instance, importer, **kwargs)

    def manyrelatedmanager_deserializer(instance, **kwargs):
        return deserialize_manyrelatedmanager(instance, importer, **kwargs)

    importer.method_map['relatedmanager'] = relatedmanager_deserializer
    importer.method_map['manyrelatedmanager'] = manyrelatedmanager_deserializer
