from cms.models import CMSPlugin
from typing import Any, Dict, List


class Exporter:
    def __init__(self):
        self.version = "0.1.1"
        self.meta_fields = ['plugin_type', 'position', 'path', 'depth', 'numchild',
                            'changed_date', 'creation_date', 'id', 'language', 'parent']
        self.skip_fields = ['alias_reference', 'source_string', 'placeholder', 'cmsplugin_ptr']
        self.method_map = {
            'int': lambda value: value,
            'str': lambda value: value,
            'uuid': lambda value: str(value),
            'float': lambda value: value,
            'decimal': lambda value: str(value),
            'category': lambda value: value.name,
            'datetime': lambda value: int(value.timestamp()),
            'list': lambda value: self.serialize_list(value),
            'msflist': lambda value: self.serialize_list(value),
            'dict': lambda value: self.serialize_dict(value),
            'cmsplugin': lambda value: value.id,
            'nonetype': lambda value: None,
            'bool': lambda value: value,
            'safetext': lambda value: value,
            'relatedmanager': lambda value: {"_type": "inline", "_model_label": value.model._meta.label,
                                             "_data": self.serialize_related_manager(value)},
            '_parent_related_field': lambda: {"_type": "parent_related_field", "_data": None},

        }

    def serialize_plugin(self, obj: any, parent_related_field: str = None) -> Dict[str, Any]:
        if isinstance(obj, CMSPlugin):
            downcasted_obj = obj.get_plugin_instance()[0]
            if not downcasted_obj:
                # TODO: log issue. There are CMSPlugin instances which are not associated with a plugin instance.
                # This is a data integrity issue. However, the plugin is not present in the CMS tree,
                # so we can ignore it.
                return {}
        elif hasattr(obj, '_meta'):
            downcasted_obj = obj
        else:
            raise ValueError(
                f'The object {obj} cannot be serialized because it is not a CMSPlugin or a model instance.')
        serialized_obj = {}
        serialized_obj['meta'] = {}
        all_fields = downcasted_obj._meta.get_fields()
        filtered_fields = [field for field in all_fields if field.name != parent_related_field]
        for field in filtered_fields:
            field_name = field.name
            if not hasattr(downcasted_obj, field_name):
                # ._meta.get_fields() returns fields that are not present in the instance. We can safely ignore them.
                continue
            if field.name in self.skip_fields:
                # TODO: move this logic to filtered_fields
                continue
            if field.name in self.meta_fields:
                dict = serialized_obj['meta']
            else:
                dict = serialized_obj
            attr_value = getattr(downcasted_obj, field_name)
            serialize_method = self.get_serialize_method(attr_value)
            dict[field_name] = serialize_method(attr_value)
        # TODO: extract parent related field logic to a method
        if parent_related_field is not None:
            if hasattr(downcasted_obj, parent_related_field):
                serialize_method = self.method_map.get('_parent_related_field')
                serialized_obj[f"{parent_related_field}_id"] = serialize_method()
        return serialized_obj

    def serialize_plugins(self, plugins: List[any]) -> List[Dict[str, Any]]:
        serialized_plugins = []
        for plugin in plugins:
            serialized_plugin = self.serialize_plugin(plugin)
            if serialized_plugin == {}:
                continue
            serialized_plugins.append(serialized_plugin)
        return serialized_plugins

    def get_serialize_method(self, attr_value: Any):
        serialize_method = self.method_map.get(type(attr_value).__name__.lower())
        if serialize_method is not None:
            return serialize_method

        raise ValueError(f'No serialize method found for {type(attr_value).__name__}')

    def serialize_list(self, list: List) -> List:
        serialized_list = []
        for item in list:
            serialize_method = self.get_serialize_method(item)
            if serialize_method:
                serialized_list.append(serialize_method(item))
            else:
                serialized_list.append(item)
        return serialized_list

    def serialize_related_manager(self, related_manager: List) -> List:
        serialized_list = []
        related_field_name = related_manager.field.name
        for item in related_manager.all():
            serialized_list.append(self.serialize_plugin(item, parent_related_field=related_field_name))
        return serialized_list

    def serialize_many_related_manager(self, many_related_manager):
        serialized_list = []
        for item in many_related_manager.all():
            serialize_method = self.get_serialize_method(item)
            serialized_list.append(serialize_method(item))
        return serialized_list

    def serialize_dict(self, dict: Dict) -> Dict:
        serialized_dict = {}
        for key, value in dict.items():
            serialize_method = self.get_serialize_method(value)
            serialized_dict[key] = serialize_method(value)
        return serialized_dict
