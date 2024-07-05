import logging
import requests
from django.apps import apps
from djangocms_plugie.version0.utils import handle_special_plugin_fields
from djangocms_plugie.version0.helpers import PluginContext


logger = logging.getLogger(__name__)


class HttpClient:
    def get(self, url, **kwargs):
        return requests.get(url, **kwargs)

    @property
    def exceptions(self):
        return requests.exceptions


class Logger:
    def log(self, level, message):
        logger.log(level, message)

    def info(self, message):
        logger.info(message)


class Importer:
    def __init__(self, http_client=None, logger=None):
        self.http_client = http_client or HttpClient()
        self.logger = logger or Logger()
        self.version = "0.2.0"
        self.method_map = {
            'inline': self._import_inline,
            'parent_related_field': self._import_parent_related_field,
            'manyrelatedmanager': self._import_many_related_manager,
        }
        self.dummy_plugins = [
            # e.g.: 'Module',
        ]

    def import_plugins_to_target(self, data):
        all_plugins = data.get("import_data").get("all_plugins")
        sorted_plugins = self.sort_plugins_by_depth(all_plugins)
        plugin_tree = self.create_plugin_tree(sorted_plugins, data)

        self.fix_plugin_tree(plugin_tree)

    def create_plugin_tree(self, sorted_plugins, data):
        plugin_map = {}

        for plugin_fields in sorted_plugins:
            plugin_context = self.create_plugin_context(plugin_fields, data, plugin_map)
            new_plugin = self.create_new_plugin(plugin_context)

            plugin_map[plugin_context.source_id] = {"plugin": new_plugin, "original_position": plugin_context.position}
        return plugin_map

    def create_plugin_context(self, plugin_fields, data, plugin_map):
        plugin_context = PluginContext(data.get('placeholder'), plugin_fields)

        is_root_plugin = plugin_context.parent_id not in plugin_map

        if is_root_plugin:
            plugin_context.target_plugin = data["plugin"]
            num_children_in_target = self.get_num_children_in_target(data)
            plugin_context.increment_position_by(num_children_in_target)
            plugin_context.validate_root_plugin()
        else:
            plugin_context.target_plugin = plugin_map[plugin_context.parent_id]["plugin"]

        return plugin_context

    def create_new_plugin(self, plugin_context):
        if plugin_context.plugin_type in self.dummy_plugins:
            return plugin_context.create_dummy_plugin()
        else:
            return plugin_context.create_plugin(self.method_map)

    @staticmethod
    def sort_plugins_by_depth(plugins):
        if not plugins:
            return plugins

        return sorted(plugins, key=lambda p: p.get("meta").get("depth", 1))

    @staticmethod
    def fix_plugin_tree(plugin_map):
        for source_plugin in plugin_map.values():
            new_plugin = source_plugin.get("plugin")
            original_position = source_plugin.get("original_position")
            if original_position is None:
                continue
            if new_plugin.position != original_position:
                new_plugin.position = original_position
                new_plugin.save()

    @staticmethod
    def get_num_children_in_target(data):
        target = data.get('plugin')
        if target:
            return target.get_descendants().filter(depth=target.depth + 1).count()

        target = data.get('placeholder')
        if target:
            return target.get_plugins().filter(parent__isnull=True).count()

        raise ValueError("Target plugin or placeholder is not defined")

    def _import_inline(self, data, **kwargs):
        model_label = kwargs.get('_model_label', None)
        plugin = kwargs.get('_plugin_id', None)
        created_instances = []
        if model_label is not None and plugin is not None:
            model_class = apps.get_model(*model_label.split('.'))
            for instance_data in data:
                instance_data.pop('meta', None)
                processed_fields = handle_special_plugin_fields(instance_data, plugin, self.method_map)
                model_instance = model_class.objects.create(**processed_fields)
                model_instance.save()
                created_instances.append(model_instance)

        return created_instances

    def _import_many_related_manager(self, data, **kwargs):
        instances = []
        plugin_id = kwargs.get('_plugin_id', None)
        for instance_data in data:
            fields = {'key': instance_data}
            processed_fields = handle_special_plugin_fields(fields, plugin_id, self.method_map)
            instances.append(processed_fields['key'])
        return instances

    def _import_parent_related_field(self, _, **kwargs):
        plugin = kwargs.get('_plugin_id', None)
        return plugin
