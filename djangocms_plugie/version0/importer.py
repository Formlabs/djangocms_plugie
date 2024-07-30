import logging

from djangocms_plugie.version0.helpers import PluginContext
from djangocms_plugie.methods.method_map import ImporterMethodMap


logger = logging.getLogger(__name__)


class Logger:
    def log(self, level, message):
        logger.log(level, message)

    def info(self, message):
        logger.info(message)


class Importer:
    def __init__(self, logger=None):
        self.logger = logger or Logger()
        self.version = "0.2.0"
        self.method_map = ImporterMethodMap()
        self.dummy_plugins = [
            'Module',
        ]

    def import_plugins_to_target(self, data):
        all_plugins = data.get("import_data").get("all_plugins")
        sorted_plugins = self.sort_plugins_by_depth(all_plugins)
        plugin_tree = self.create_plugin_tree(sorted_plugins, data)

        self.fix_plugin_tree(plugin_tree)

    def create_plugin_tree(self, sorted_plugins, data):
        plugin_map = {}

        for plugin_fields in sorted_plugins:
            plugin_context = self.create_plugin_context(
                plugin_fields, data, plugin_map)
            new_plugin = self.create_new_plugin(plugin_context)

            plugin_map[plugin_context.source_id] = {
                "plugin": new_plugin,
                "original_position": plugin_context.position
            }
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
            target_plugin = plugin_map[plugin_context.parent_id]["plugin"]
            plugin_context.target_plugin = target_plugin

        return plugin_context

    def create_new_plugin(self, plugin_context):
        if plugin_context.plugin_type in self.dummy_plugins:
            return plugin_context.create_dummy_plugin()
        else:
            return plugin_context.create_plugin(self.method_map.method_map)

    @staticmethod
    def sort_plugins_by_depth(plugins):
        if not plugins:
            return plugins

        return sorted(
            plugins,
            key=lambda p: (
                p.get("meta").get("depth", 1),
                p.get("meta").get("position", 0)
            )
        )

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
            descendants = target.get_descendants()
            filtered_descendants = descendants.filter(
                depth=target.depth + 1
            )
            return filtered_descendants.count()

        target = data.get('placeholder')
        if target:
            return target.get_plugins().filter(parent__isnull=True).count()

        raise ValueError("Target plugin or placeholder is not defined")
