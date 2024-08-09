import logging
from cms.models import CMSPlugin
from djangocms_plugie.exporter.field_handler import FieldHandler

logger = logging.getLogger(__name__)


class PluginSerializer:
    def __init__(self, exporter_method_map):
        self.exporter_method_map = exporter_method_map
        self.field_handler = FieldHandler()

    def serialize_plugin(self, plugin, parent_related_field=None):
        downcasted_obj = self._get_downcasted_plugin(plugin)
        if not downcasted_obj:
            return {}

        non_meta_fields = self.field_handler.get_non_meta_fields(downcasted_obj)
        if parent_related_field:
            non_meta_fields.remove(parent_related_field)
            
        serialized_obj = self.field_handler.serialize_fields(
            downcasted_obj, non_meta_fields, self._get_serialized_value)

        serialized_obj['meta'] = self._get_meta_obj(plugin)

        if parent_related_field:
            serialized_obj[f"{parent_related_field}_id"] = self._get_parent_related_field_obj(
                downcasted_obj, parent_related_field)

        return serialized_obj

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
            logger.warning(f'Plugin {plugin} has no instance. Skipping.')
            return None
        return downcasted_obj

    def _get_serialized_value(self, plugin, field_name):
        field_value = getattr(plugin, field_name)
        serialize_method = self.exporter_method_map.get_serialize_method(field_value)
        return serialize_method(field_value)

    def _get_meta_obj(self, plugin):
        return {
            field.name: self._get_serialized_value(plugin, field.name)
            for field in plugin._meta.get_fields()
            if field.name in self.field_handler.meta_fields
        }

    def _get_parent_related_field_obj(self, downcasted_obj, parent_related_field):
        if hasattr(downcasted_obj, parent_related_field):
            return self.exporter_method_map.method_map.get('_parent_related_field')()
