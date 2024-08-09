def serialize_list(instance, loader):
    serialized_list = []
    for item in instance:
        serialize_method = loader.get_serialize_method(item)
        if serialize_method:
            serialized_list.append(serialize_method(item))
        else:
            serialized_list.append(item)
    return serialized_list


def serialize_relatedmanager(instance, loader):
    serialized_list = []
    related_field_name = instance.field.name
    for item in instance.all():
        serialized_list.append(loader.exporter.plugin_serializer.serialize_plugin(
            item, parent_related_field=related_field_name))

    return {
        "_type": "relatedmanager",
        "_model_label": instance.model._meta.label,
        "_list": serialized_list
    }


def serialize_manyrelatedmanager(instance, loader):
    serialized_list = []
    for item in instance.all():
        serialize_method = loader.get_serialize_method(item)
        serialized_list.append(serialize_method(item))

    return {
        "_type": "manyrelatedmanager",
        "_list": serialized_list
    }


def serialize_dict(instance, loader):
    serialized_dict = {}
    for key, value in instance.items():
        serialize_method = loader.get_serialize_method(value)
        serialized_dict[key] = serialize_method(value)
    return serialized_dict


def register_serializers(loader):
    def list_serializer(instance):
        return serialize_list(instance, loader)

    def msflist_serializer(instance):
        return serialize_list(instance, loader)

    def dict_serializer(instance):
        return serialize_dict(instance, loader)

    def relatedmanager_serializer(instance):
        return serialize_relatedmanager(instance, loader)

    def manyrelatedmanager_serializer(instance):
        return serialize_manyrelatedmanager(instance, loader)

    loader.method_map['list'] = list_serializer
    loader.method_map['msflist'] = msflist_serializer
    loader.method_map['dict'] = dict_serializer
    loader.method_map['relatedmanager'] = relatedmanager_serializer
    loader.method_map['manyrelatedmanager'] = manyrelatedmanager_serializer
