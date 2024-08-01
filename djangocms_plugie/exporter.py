import logging
from cms.models import CMSPlugin
from typing import Any, Dict, List
from djangocms_plugie.methods.method_map import ExporterMethodMap

logger = logging.getLogger(__name__)


class Exporter:
    def __init__(self):
        self.version = "0.3.0"
        self.skip_fields = ['alias_reference', 'source_string', 'placeholder', 'cmsplugin_ptr']
        self.method_map = ExporterMethodMap(exporter=self)

    def _get_downcasted_plugin(self, plugin):
        if isinstance(plugin, CMSPlugin):
            return self._get_plugin_instance(plugin)
        
        if hasattr(plugin, '_meta'):
            return plugin

        msg = f'The object {plugin} cannot be serialized because it is not a CMSPlugin or a model instance.'
        logger.error(msg)
        raise ValueError(msg)
    
    def _get_plugin_instance(self, plugin):
        downcasted_obj = plugin.get_plugin_instance()[0]
        if not downcasted_obj:
            # There are CMSPlugin instances which are not
            # associated with a plugin instance. This is a data integrity
            # issue. However, the plugin is not present in the CMS tree,
            # so we can ignore it.
            logger.warning(f'Plugin {plugin} has no instance. Skipping.')
            return {}
        return downcasted_obj
    
    def _get_related_fields(self, downcasted_obj):
        return [obj.name for obj in downcasted_obj._meta.related_objects if obj.remote_field.name == 'container']
    
    def _get_meta_fields(self, plugin):
        skip_fields = self.skip_fields
        return [field.name for field in plugin._meta.concrete_fields if field.name not in skip_fields]
    
    def _get_non_meta_field(self, downcasted_obj):
        skip_fields = self.skip_fields
        local_concrete_fields = self._get_local_concrete_fields(downcasted_obj)
        related_fields = self._get_related_fields(downcasted_obj)
        local_and_related_fields = local_concrete_fields + related_fields
        return [field for field in local_and_related_fields if field not in skip_fields]

    def _get_local_concrete_fields(self, downcasted_obj):
        local_concrete_fields = downcasted_obj._meta.local_concrete_fields
        return [field.name for field in local_concrete_fields if not field.is_relation]
    
    def _get_serialized_value(self, plugin, field_name):
        field_value = getattr(plugin, field_name)
        serialize_method = self.method_map.get_serialize_method(field_value)
        return serialize_method(field_value)
    
    def _get_meta_obj(self, plugin):
        meta_fields = self._get_meta_fields(plugin)
        return {field_name: self._get_serialized_value(plugin, field_name) for field_name in meta_fields}

    def _get_non_meta_obj(self, plugin, parent_related_field = None):
        non_meta_fields = self._get_non_meta_field(plugin)
        if parent_related_field is not None:
            non_meta_fields = [field for field in non_meta_fields if field.name != parent_related_field]
        return {field_name: self._get_serialized_value(plugin, field_name) for field_name in non_meta_fields}

    def serialize_plugin(self, plugin, parent_related_field = None):
        downcasted_obj = self._get_downcasted_plugin(plugin)
        serialized_obj = self._get_non_meta_obj(downcasted_obj, parent_related_field)
        serialized_obj['meta'] = self._get_meta_obj(plugin)
        if parent_related_field is not None:
            serialized_obj[f"{parent_related_field}_id"] = self._get_parent_related_field_obj(downcasted_obj, parent_related_field)
        return serialized_obj

    def _get_parent_related_field_obj(self, downcasted_obj, parent_related_field):
        if hasattr(downcasted_obj, parent_related_field):
            return self.method_map.method_map.get('_parent_related_field')

    def serialize_plugins(self, plugins: List[any]) -> List[Dict[str, Any]]:
        serialized_plugins = []
        for plugin in plugins:
            serialized_plugin = self.serialize_plugin(plugin)
            if serialized_plugin == {}:
                continue
            serialized_plugins.append(serialized_plugin)
        return serialized_plugins
