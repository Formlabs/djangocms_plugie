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
        serialized_list.append(loader.exporter.serialize_plugin(
            item, parent_related_field=related_field_name))

    return {
        "_type": "relatedmanager",
        "_model_label": instance.model._meta.label,
        "_data": serialized_list
    }


def serialize_manyrelatedmanager(instance, loader):
    serialized_list = []
    for item in instance.all():
        serialize_method = loader.get_serialize_method(item)
        serialized_list.append(serialize_method(item))

    return {
        "_type": "manyrelatedmanager",
        "_data": serialized_list
    }


def serialize_dict(instance, loader):
    serialized_dict = {}
    for key, value in instance.items():
        serialize_method = loader.get_serialize_method(value)
        serialized_dict[key] = serialize_method(value)
    return serialized_dict


def register_serializers(loader):
    loader.method_map['list'] = lambda instance: serialize_list(
        instance, loader)
    loader.method_map['msflist'] = lambda instance: serialize_list(
        instance, loader)
    loader.method_map['dict'] = lambda instance: serialize_dict(
        instance, loader)
    loader.method_map['relatedmanager'] = lambda instance: serialize_relatedmanager(
        instance, loader)
    loader.method_map['manyrelatedmanager'] = lambda instance: serialize_manyrelatedmanager(
        instance, loader)
